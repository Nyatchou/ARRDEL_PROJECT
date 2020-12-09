from django.shortcuts import render
import pandas as pd

from django.http.response import JsonResponse
from .models import ProjectItem
from sentence_transformers import SentenceTransformer, util
from django.http import HttpResponse
from rest_framework import generics, response, status
from .serializers import ProjectItemSerializer
from django.views.generic.edit import FormView
from .forms import ProjectCaractsForm
from django import forms
import json
import requests




def get_projects_dataframe():
    resdatas = requests.get('http://127.0.0.1:8000/serverapi/projects/')
    datas = resdatas.json()
    list_keys = datas[0].keys()
    datas = [list(item.values()) for item in datas]

    df = pd.DataFrame(datas, columns=list_keys)
    df.rename(columns = {'id_repartition': 'IDRepartition', 'id_tache':'IDTache', 'commune': 'Commune',
     'departement':'Departement', 'region':'Région', 'intitule': 'Intitulé'},
    inplace=True)
    df = df.assign(IDSecteur = lambda x: 'NaN' )
    df = df.assign(IDChapitre = lambda x: 'NaN' )
    return df

embedder = SentenceTransformer('distilbert-multilingual-nli-stsb-quora-ranking')


def similarity_category_series(serie1, serie2):
    if serie1['IDChapitre'] == serie2['IDChapitre']:
        return 1.0
    else:
        if serie1['IDSecteur'] == serie2['IDSecteur']:
            return 0.5
        else:
            return 0.0

def similarity_tasks(serie1, serie2):
    if serie1['IDTache'] == serie2['IDTache']:
        return 1.0
    return 0.0

def similarity_zone(serie1, serie2):
    if serie1['Commune'] == serie2['Commune']:
        return 1.0
    else: 
        if serie1['Departement'] == serie2['Departement']:
            return 0.5
        else:
            if serie1['Région'] == serie2['Région']:
                return 0.25
    return 0.0

def compute_similarity_series(serie1, serie2):
    coeff = similarity_category_series(serie1, serie2)*0.5 + similarity_tasks(serie1, serie2)*0.2 + similarity_zone(serie1, serie2)*0.1
    return coeff

def compute_similarity(serie, dataframe):
    indexes_dataframe = dataframe.index.get_values()
    if len(indexes_dataframe) == 0:
        return None
    similarities_and_indexes = {}
    for index in indexes_dataframe:
        similarities_and_indexes[dataframe.loc[index]['IDRepartition']] = similarity_category_series(serie, dataframe.loc[index])*0.5 
        + similarity_tasks(serie, dataframe.loc[index])*0.2 + similarity_zone(serie, dataframe.loc[index])*0.1 
    similarities_df = pd.DataFrame({'score': list(similarities_and_indexes.values())}, index=list(similarities_and_indexes.keys()))
    return similarities_df





class GetProjectSimils(generics.RetrieveAPIView):
    serializer_class = ProjectItemSerializer
    queryset = ProjectItem.objects.all()


    def get_object(self):
        idrepartition = self.kwargs.get('idrep')
        item = ProjectItem.objects.get(idrepartition=idrepartition)
        return item

    def get(self, request , *args , **kwargs):
        query = self.get_object()
        projs = query.others_projects
        projsimilarities = [
            {'idrepartition' : item['idrepartition'], 'similarity_value': item['similarity_value'] } for item in projs
        ]
        data = {
            'idrepartition' : query.idrepartition ,
            'others_projects' : projsimilarities
        }
        return response.Response(data, status=status.HTTP_200_OK)

class GetProjectsSimils(generics.ListAPIView):
    serializer_class = ProjectItemSerializer
    queryset = ProjectItem.objects.all()

    def get(self, request , *args , **kwargs):
        query = self.get_queryset()
        datas = []
        for proj in query:
            projs = proj.others_projects
            projsimilarities = [
                {'idrepartition' : item['idrepartition'], 'similarity_value': item['similarity_value'] } for item in projs
            ]
            data = {
                'idrepartition' : proj.idrepartition ,
                'others_projects' : projsimilarities
            }
            datas.append(data)
        return response.Response(datas, status=status.HTTP_200_OK)


def save_projects_simils(request):
    count = ProjectItem.objects.all().delete()
    print(count)
    projects_df = get_projects_dataframe()
    corpus = list(projects_df['Intitulé'].values)
    corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)
    cos_all_scores = util.pytorch_cos_sim(corpus_embeddings, corpus_embeddings)
    cos_all_scores = cos_all_scores.cpu().numpy()

    for i in range(len(projects_df)):
        project1 = projects_df.iloc[i]
        project_sims = ProjectItem(idrepartition=project1['IDRepartition'])
        other_projects_sims_list = []
        for j in range(len(projects_df)):
            project2 = projects_df.iloc[j]
            if project1['IDRepartition'] != project2['IDRepartition']:
                simil_val = compute_similarity_series(project1, project2) + 0.2*(cos_all_scores[i][j])**2
                other_projects_sims_list.append(
                    {
                        'idrepartition': project2['IDRepartition'],
                        'similarity_value' : simil_val
                    }
                )
                project_sims.others_projects = other_projects_sims_list
        project_sims.save()
    return HttpResponse('OK')
        

class AddNewProjectSimilarities(FormView):
    template_name = 'projects_similarities_computer/project_caracts.html'
    form_class = ProjectCaractsForm
    success_url = '/addproject/'

    def form_valid(self, form):
        projects_df = get_projects_dataframe()
        idrep = form.cleaned_data.get('idrepartition')
        idtache = form.cleaned_data.get('idtache')
        commune = form.cleaned_data.get('commune')
        chapitre = form.cleaned_data.get('chapitre')
        secteur = form.cleaned_data.get('secteur')
        intitule = form.cleaned_data.get('intitule')

        data = {
            'idrepartition': idrep,
            'idtache': idtache,
            'intitule' : intitule,
            'commune' : commune
        }
        res = requests.post('http://127.0.0.1:8000/serverapi/projectcreate/', data=data)

        newproject = res.json()

        project_series = pd.Series(data=[ intitule,  idrep, idtache, commune, newproject['departement'], 
         newproject['region'], secteur, chapitre ], index=projects_df.columns)
        intitule_encode = embedder.encode([intitule], convert_to_tensor=True )
        simils_df = compute_similarity(project_series, projects_df)
        corpus = list(projects_df['Intitulé'].values)
        corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)
        cos_all_scores = util.pytorch_cos_sim(intitule_encode, corpus_embeddings)[0]
        cos_all_scores = cos_all_scores.cpu()
        dataframe_score = pd.DataFrame(cos_all_scores, columns = ['score'], index=projects_df['IDRepartition'].values)
        dataframe_score['score'] = dataframe_score['score']**2
        res_temp = simils_df[['score']]
        res_temp = res_temp.add(0.2 * dataframe_score)
        simils_df['score'] = res_temp['score']
        project_sims = ProjectItem(idrepartition=idrep)

        project_sims.others_projects = [
            { 'idrepartition' : index  , 'similarity_value': simils_df.loc[index]['score']} for index in simils_df.index.values
        ]
        project_sims.save()
        for project in ProjectItem.objects.all():
            if project.idrepartition != idrep:
                project.others_projects.append({'idrepartition' : idrep, 
                'similarity_value' : simils_df.loc[project.idrepartition]['score']})
                project.save()
        return super(AddNewProjectSimilarities, self).form_valid(form)
