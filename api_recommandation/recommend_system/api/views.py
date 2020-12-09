from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from  rest_framework import status
import pandas as pd
import numpy as np
import math
import random
from sklearn.metrics.pairwise import cosine_similarity
import operator
from django.http import HttpResponse, Http404
from django.views.generic.edit import FormView
import requests
import json
from recommend_system.api.forms import *

"""Récupération des paramètres se trouvant dans le fichier params.json"""
with open('./recommend_system/api/params.json') as file_read_params:
    json_params = json.load(file_read_params)

"""Récupération des urls se trouvant dans le fichier urls_backend.json"""
with open('./recommend_system/api/urls_backend.json') as file_read_urls:
    json_urls = json.load(file_read_urls)

"""url permettant d'accéder à la liste de tous les projets"""
url_projects_list = json_urls.get('url_projects_list') 


"""
Paramètres :
- réponse renvoyée par la requête à l'url 'url_users_visits_datas'(res_data)
- le dataframe contenant la liste des projets en paramètres (projects_df)

Cette fonction produit tout d'abord un dataframe avec les colonnes suivantes:
- User : identifiant d'un utilisateur
- IDRepartition : code d'un projet
- Visit_count : nombre de visites d'un utilisateur dans un projet sur la plateforme
- Print_project_file : 0 si il n'a pas imprimé la fiche projet, 1 sinon
- Behavior interesting : 0 s'il a eu un comportement sur la plateforme montrant un certain intérêt pour un projet, 1 sinon

A ces colonnes est ajouté une nouvelle colonne par la fonction 'rate_users_df' qui contient des 0 et 1,
et représente le non intérêt ou l'intérêt d'un utilisateur pour un projet 
"""
def transform_data_users_df(projects_df):
    """
    url permettant d'accéder aux nombre visites des tous les utilisateurs, 
    dans les différents projets sur la plateforme,  s'ils ont ou non imprimé 
    la fiche projet, et ont un comportement avec un intérêt manifeste
    """
    url_users_visits_datas = json_urls.get('url_users_visits_datas') 
    res_users_visits_datas = requests.get(url_users_visits_datas, headers={'Content-Type': 'application/json'})

    data_visits = res_users_visits_datas.json()
    #titles = list(data_visits[0].keys())
    datas_users_projects_list = [list(item.values()) for item in data_visits]
    users_df = pd.DataFrame(datas_users_projects_list, columns=list(data_visits[0].keys()))
    users_df = users_df.astype({'User':str})
    def func(elt: pd.DataFrame):
        elt = elt.merge(projects_df, on='IDRepartition', how='right')
        elt = elt.drop_duplicates(subset=['IDRepartition'], keep='first')
        values = {'Visit_count': 0, 'Print_project_file':0, 'Behavior_interesting':0, 'User': elt['User'].iloc[0]}
        values_types = {'Visit_count': int, 'Print_project_file':int, 'Behavior_interesting':int, 'User': type(elt['User'].iloc[0])}
    
        elt.fillna(values, downcast=values_types, inplace=True)
        return elt

    temp_df = users_df.groupby('User').apply(func)
    #users_df = temp_df.astype({'User':int ,'Visit_count':int, 'Behavior_interesting':int, 'Print_project_file':int, 'IDRepartition':str})
    users_df = rate_users_df(temp_df)
    users_df = pd.DataFrame(users_df.values, index=users_df.index.droplevel(0), columns=users_df.columns)
    return users_df

"""
"""
def rate_users_df(dataframe):
    with open('./recommend_system/api/params.json') as file_read_params:
        json_params = json.load(file_read_params)
    MIN_VISITS_INTEREST = json_params.get('MIN_VISITS_INTEREST')
    NB_VISITS_INTEREST = json_params.get('NB_VISITS_INTEREST')

    dataframe = dataframe.assign(Rating = lambda x: 0)
    condition2 = operator.and_(dataframe['Visit_count'] > MIN_VISITS_INTEREST -1 , dataframe['Visit_count'] < NB_VISITS_INTEREST)
    condition3 = operator.or_(dataframe['Print_project_file'] == 1, dataframe['Visit_count'] > NB_VISITS_INTEREST-1)
    condition4 = operator.and_(dataframe['Behavior_interesting'] == 1, condition2)

    dataframe['Rating'].mask(condition4, 1, inplace=True)
    dataframe['Rating'].mask(condition3, 1, inplace=True)
    return dataframe

def get_transform_projects_similarities():
    url_proj_simils = json_urls.get('url_projects_similarities')
    res = requests.get(url_proj_simils, headers={'Content-Type': 'application/json'})
    projects_simils = res.json()
    projects_simils_df = pd.DataFrame()
    for project_simils in projects_simils:         
        idreps = [item['idrepartition'] for item in project_simils['others_projects']]
        values = [item['similarity_value'] for item in project_simils['others_projects']]
        project_simils_df = pd.DataFrame({
            'Project1' : idreps,
            'SimilarityScore' : values
        })
        project_simils_df = project_simils_df.assign(Project2 = lambda x: project_simils['idrepartition'])
        projects_simils_df = pd.concat([projects_simils_df, project_simils_df])
    projects_simils_df = projects_simils_df.pivot(index='Project1', columns='Project2', values = 'SimilarityScore')
    return projects_simils_df


res_pj_list = requests.get(url_projects_list, headers={'Content-Type': 'application/json'})
projects_list_all = [ item['id_repartition'] for item in res_pj_list.json()]
projects_df = pd.DataFrame({'IDRepartition':projects_list_all})

projects_sims_df = get_transform_projects_similarities()

users_df = transform_data_users_df( projects_df)


"""Cette vue peut renvoyer dans sa réponse une liste de communes,
regions, departement, chapitres, secteurs, ... représentant pour chacun des éléments
précédents, les plus visités
"""
class ListRecommendItemView(APIView):

    #authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        #item peut être 'commune', 'departement', 'region', ...
        item = self.kwargs.get('item')
        """cette url permet d'avoir pour un utilisateur particulier le 
        nombre de visites qu'il a eu a effectué dans chaque commune sur 
        la plateforme"""
        """cette url permet d'avoir pour un utilisateur particulier le 
        nombre de visites qu'il a eu a effectué dans chaque departement sur 
        la plateforme"""
        urls_dict = {
            'commune': json_urls.get('url_datas_visits_commune') ,
            'departement' : json_urls.get('url_datas_visits_departement')
        }
        url = urls_dict.get(item).format(user_id)
        NB_MAX_RECOMMANDATIONS = json_params.get('NB_MAX_RECOMMANDATIONS')

        try:
            res = requests.get(url, headers={'Content-Type':      
                'application/json'})
            """Format supposé des données :
            {
                'item' : "element à recommander",
                'data: : "dictionnaire contenant les items et le nombre de visites dans chacun"
            }
            """

            if res.status_code == 200:
                data = res.json()
                df = create_dataframe(data['item'], data['data'])
                recommanded_list, item = make_recommandation(df, NB_MAX_RECOMMANDATIONS)
                datas = {
                    'recommand_list': recommanded_list,
                    'item': item
                }
                return Response(datas, status=status.HTTP_200_OK)
            if res.status_code == 404:
                return Response("Erreur d'accès aux informations, il se pourrait que cet identifiant ne corresponde à aucun utilisateur", 
                    status=status.HTTP_404_NOT_FOUND)
            
            return Response("error")
        except requests.exceptions.RequestException :
            return Response("Connexion au serveur distant impossible", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

"""
Paramètres : 
- column_name : l'élément à recommander, peut être 'Code_Commune', 'Code_Departement'
- elements_and_visitscount : les éléments visités sur la plateforme avec le nombre de visites pour chacun

Elle renvoie un dataframe avec les éléments visités sur la plateforme avec le nombre
de visites pour chaque élément
"""

def create_dataframe(column_name: str, elements_and_visitscount: dict):
    elements_list = list(elements_and_visitscount.keys())
    visits_count_list = list(elements_and_visitscount.values())
    df = pd.DataFrame({column_name: elements_list, 'Visits_count': visits_count_list})
    return df



def make_recommandation(dataframe: pd.DataFrame, NB_MAX: int):
    columns_titles = dataframe.columns.tolist()
    columns_titles.remove('Visits_count')
    title_column = columns_titles[0]
    df_choices = dataframe.sort_values('Visits_count', ascending = False)
    #total_visits = df_choices['Visits_count'].sum()
    mean_visits = df_choices['Visits_count'].mean()
    recommanded = []
    if len(df_choices) <= NB_MAX:
        recommanded.extend(df_choices[title_column].tolist())
    else:
        mosts_visits_elt = df_choices[df_choices['Visits_count'] > mean_visits]
        recommanded.extend(mosts_visits_elt[:NB_MAX][title_column].tolist())
    return recommanded, title_column

class RecommandProjectView2(APIView):
    def get(self, request, *args, **kwargs):
        user_index = self.kwargs.get('user_id')
        # url_singleuser_visits_datas = "http://127.0.0.1:8000/serverapi/visitsdata/{}".format(user_index)
        # res_singleuser_visits_datas = requests.get(url_singleuser_visits_datas, headers={'Content-Type': 'application/json'})
        # data_singleuser_visits = res_singleuser_visits_datas.json()
        # datas_singleuser_projects_list = [list(item.values()) for item in data_singleuser_visits]
        # singleuser_df = pd.DataFrame(datas_singleuser_projects_list, columns=list(data_singleuser_visits[0].keys()))
        # singleuser_df = rate_users_df(singleuser_df)
        PERIOD_RECOMMAND = json_params.get('PERIOD_RECOMMAND')

        singleuser_df = users_df[users_df['User'] == user_index]
        """
        url permettant d'avoir pour un utilisateur particulier le 
        nombre de fois où chaque projet lui a été recommandé
        """
        url_user_recommands_count0 = json_urls.get('url_user_recommands_count')
        url_user_recommands_count = url_user_recommands_count0.format(user_index)
        try:
            res_user_recommands_count = requests.get(url_user_recommands_count, headers={'Content-Type': 'application/json'})
            if res_user_recommands_count.status_code == 200:
                data_count_recommands = [list(item.values()) for item in res_user_recommands_count.json()]
                recommands_user_df = pd.DataFrame(data_count_recommands, columns=['Recommands_count', 'IDRepartition'])
                recommands_user_df = recommands_user_df.merge(projects_df, on='IDRepartition',  how='right')
                recommands_user_df = recommands_user_df.fillna(0)
                recommands_user_df = recommands_user_df.assign(Score_recommands = recommands_user_df['Recommands_count'] // PERIOD_RECOMMAND)
                recommands_user_df = recommands_user_df.drop(columns=['Recommands_count'])
                
                datas_list_currentuser =  singleuser_df[singleuser_df['Visit_count'] > 0]

                projects_to_recommand = self.recommand_by_content_based_approach(projects_sims_df, recommands_user_df, datas_list_currentuser)
                datas = projects_to_recommand['IDRepartition'].values
                # datas = []
                # for ind in range(len(projects_to_recommand)):
                #     proj = projects_to_recommand.iloc[ind]
                #     datas.append(
                #         {
                #             'idrepartition': proj['IDRepartition'],
                #             'score': proj['score'],
                #             'period_recommand_score' : proj['Score_recommands']
                #         }
                #     )

                return Response(datas, status=status.HTTP_200_OK)
            if res_user_recommands_count.status_code == 404:
                return Response("Erreur d'accès aux informations, il se pourrait que cet identifiant ne corresponde à aucun utilisateur", 
                    status=status.HTTP_404_NOT_FOUND)
            
            return Response("error")
        except requests.exceptions.RequestException :
            return Response("Erreur de connexion au serveur distant", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def recommand_by_content_based_approach(self, projects_sims_df, currentuser_datas_df, projects_list_user):
        MIN_COEFF_SIMILARITY_PROJECTS = json_params.get('MIN_COEFF_SIMILARITY_PROJECTS')
        NB_MAX_RECOMMANDATIONS = json_params.get('NB_MAX_RECOMMANDATIONS')
        NB_SIMILAR_PROJECTS_BY_PROJECT = json_params.get('NB_SIMILAR_PROJECTS_BY_PROJECT')
        recommanded_df = pd.DataFrame()
        projects_seen = projects_list_user['IDRepartition'].values
        projects_well_rated = projects_list_user[projects_list_user['Rating'] > 0]['IDRepartition'].values
        for project_id in projects_well_rated:
            temp = projects_sims_df[project_id]
            temp = temp.drop(projects_seen)
            temp = pd.DataFrame({'IDRepartition': temp.index, 'score': temp.values})
            temp = temp[temp['score'] > MIN_COEFF_SIMILARITY_PROJECTS].sort_values('score', ascending=False)[:NB_SIMILAR_PROJECTS_BY_PROJECT]
            recommanded_df = pd.concat([recommanded_df, temp])
        final_user_df = pd.merge(recommanded_df, currentuser_datas_df, on='IDRepartition', how='left')
        final_user_df.dropna(subset=['score'], inplace=True)
        final_user_df.sort_values(['Score_recommands', 'score'], ascending=[True, False], inplace=True)
        final_user_df.drop_duplicates(subset=['IDRepartition'], keep='first')
        return final_user_df[:NB_MAX_RECOMMANDATIONS]

def update_users_dataframe(request):
    res_pj_list = requests.get(url_projects_list, headers={'Content-Type': 'application/json'})
    if res_pj_list.status_code == 200:
        projects_list_all = [ item['id_repartition'] for item in res_pj_list.json() ]
        new_projects_df = pd.DataFrame({'IDRepartition':projects_list_all})
        global projects_df
        projects_df = new_projects_df
        new_users_df = transform_data_users_df(projects_df)
        global users_df
        users_df = new_users_df
        return HttpResponse('ok')
    else:
        return Http404('Not Found')
    return HttpResponse('Unknown Error')


class RecommandProjectView(APIView):
    def get(self, request, *args, **kwargs):
        user_index = self.kwargs.get('user_id')
        current_user_df = users_df[users_df['User'] == user_index]
        """
        url permettant d'avoir pour un utilisateur particulier le 
        nombre de fois où chaque projet lui a été recommandé
        """
        url_user_recommands_count0 = json_urls.get('url_user_recommands_count')
        url_user_recommands_count = url_user_recommands_count0.format(user_index)
        try:
            res_user_recommands_count = requests.get(url_user_recommands_count, headers={'Content-Type': 'application/json'})
            if res_user_recommands_count.status_code == 200:
                recommandscount_user_df = self.transform_data_recommands_count(res_user_recommands_count, projects_df)
                
                projects_to_recommand = self.recommand_by_collaborative_filtering(users_df, current_user_df, recommandscount_user_df)
                projects_to_recommand = projects_to_recommand['IDRepartition'].values

                return Response(projects_to_recommand, status = status.HTTP_200_OK)
            if res_user_recommands_count.status_code == 404:
                return Response("Erreur d'accès aux informations, il se pourrait que cet identifiant ne corresponde à aucun utilisateur", 
                    status=status.HTTP_404_NOT_FOUND)
            return Response("error")
        except requests.exceptions.RequestException :
            return Response("Erreur de connexion au serveur distant", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def recommand_by_collaborative_filtering(self, users_df, current_user_df, recommands_user_df):
        MIN_COEFF_SIMILARITY_USERS_APPROACH = json_params.get('MIN_COEFF_SIMILARITY_USERS_APPROACH')
        NB_MAX_RECOMMANDATIONS = json_params.get('NB_MAX_RECOMMANDATIONS')

        rate_projects = users_df.pivot(index='IDRepartition', columns='User', values='Rating')

        projects_list_user = current_user_df[current_user_df['Visit_count'] > 0]
        projects_well_rated = projects_list_user[projects_list_user['Rating'] > 0]['IDRepartition'].values
        projects_seen = projects_list_user['IDRepartition'].values
        
        recommanded_list = []
        for project_id in projects_well_rated:
            similarity_project = cosine_similarity(rate_projects, rate_projects.loc[project_id].to_numpy().reshape(1, -1))
            similarity_project = similarity_project.reshape(-1)
            similarity_project_df = pd.DataFrame({'score': similarity_project}, index=rate_projects.index)
            similarity_project_df = similarity_project_df.sort_values('score', ascending=False)
            similarity_project_df = similarity_project_df[similarity_project_df['score'] > MIN_COEFF_SIMILARITY_USERS_APPROACH]
            for project in similarity_project_df.index.get_values():
                if project not in recommanded_list + list(projects_seen):
                    recommanded_list.append(project)

        recommandprojs_df = pd.DataFrame({'IDRepartition': recommanded_list})
        recommandprojs_df = pd.merge(recommandprojs_df, recommands_user_df, on='IDRepartition', how='left')
        recommandprojs_df =  recommandprojs_df.dropna(subset=['Score_recommands'])
        recommandprojs_df.sort_values('Score_recommands', ascending=True, inplace=True)

        return recommandprojs_df[:NB_MAX_RECOMMANDATIONS]


    def transform_data_recommands_count(self, res_data, projects_df):
        PERIOD_RECOMMAND = json_params.get('PERIOD_RECOMMAND')
        data_count_recommands = [ list(item.values()) for item in res_data.json() ]
        recommands_user_df = pd.DataFrame(data_count_recommands, columns=['Recommands_count', 'IDRepartition']) 
        recommands_user_df = recommands_user_df.merge(projects_df, on='IDRepartition',  how='right')        
        recommands_user_df = recommands_user_df.fillna(0)
        recommands_user_df = recommands_user_df.assign(Score_recommands = recommands_user_df['Recommands_count'] // PERIOD_RECOMMAND)
        recommands_user_df = recommands_user_df.drop(columns=['Recommands_count'])
        return recommands_user_df

    def recommand_by_collaborative_filtering2(self, users_df, current_user_df, recommands_user_df):
        NB_MAX_RECOMMANDATIONS = json_params.get('NB_MAX_RECOMMANDATIONS')

        rate_users = users_df.pivot(index='User', columns='IDRepartition', values='Rating')

        projects_list_user = current_user_df[current_user_df['Visit_count'] > 0]
        #projects_well_rated = projects_list_user[projects_list_user['Rating'] > 0]['IDRepartition'].values
        projects_seen = projects_list_user['IDRepartition'].values
        user_ratings = rate_users.loc[current_user_df['User'].iloc[0]].values.reshape(1, -1)
        similarity_df = self.create_df_users_similarities(rate_users, user_ratings)
        recommanded = []
        for user in similarity_df[1:].index:
            user_prefs_df = pd.DataFrame()
            user_prefs_df['Rating'] = rate_users.loc[user]
            user_prefs = user_prefs_df.drop(user_prefs_df[user_prefs_df['Rating'] == 0.0].index, axis=0, inplace=False)
            for project in user_prefs.index.values:
                if project not in recommanded + list(projects_seen):
                    recommanded.append(project)


        recommandprojs_df = pd.DataFrame({'IDRepartition': recommanded})
        recommandprojs_df = pd.merge(recommandprojs_df, recommands_user_df, on='IDRepartition', how='left')
        recommandprojs_df =  recommandprojs_df.dropna(subset=['Score_recommands'])
        recommandprojs_df.sort_values('Score_recommands', ascending=True, inplace=True)

        return recommandprojs_df[:NB_MAX_RECOMMANDATIONS]
        

    def create_df_users_similarities(self, users_pivot_df, user):
        MIN_COEFF_SIMILARITY_USERS = json_params.get('MIN_COEFF_SIMILARITY_USERS')

        similarities_user = cosine_similarity(users_pivot_df, user)
        similarities_user = similarities_user.reshape(-1)
        #Creation d'un dictionnaire avec comme valeur un array contenant les similarités entre les utilisateurs 
        dict_df = {'score': similarities_user}

        """
        Creation d'un dataframe de similarités avec des lignes identifiées par les utilisateurs 
        Chaque élément représente la similarité entre l'utilisateur identifié sur la ligne 
        et l'utilisateur random choisi plus haut
        """
        similarity_df = pd.DataFrame(dict_df, index=users_pivot_df.index)

        #On ordonne le dataframe par coefficient de similarité décroissant
        similarity_df = similarity_df.sort_values('score', ascending=False)
        #On choisi les utilisateurs pour lesquelles la similarité est supérieure à 0.5
        similarity_df = similarity_df[similarity_df['score'] > MIN_COEFF_SIMILARITY_USERS ]

        return similarity_df

class ProjectsUndesiredListView(APIView):
    def get(self, request, *args, **kwargs):
        NB_PROJECTS_UNDESIDED = json_params.get('NB_PROJECTS_UNDESIDED')
        projects_undesired_df = users_df.groupby('IDRepartition')[['Rating']].apply(lambda x: x[x['Rating'] > 0].count())

        projects_undesired_df.rename(columns={'Rating': 'Count'}, inplace=True)
        projects_undesired_df = projects_undesired_df.sort_values('Count')
        projects_undesired = projects_undesired_df[:NB_PROJECTS_UNDESIDED].index.values

        return Response(projects_undesired, status = status.HTTP_200_OK)


class ParamsConfigView(FormView):
    form_class = ParamsForm
    template_name = 'recommend_system/paramsconf.html'
    success_url = '/api/formparams/'

    def form_valid(self, form):

        with open('./recommend_system/api/params.json') as file_read:
            json_params0 = json.load(file_read)
        json_forms_data = {}

        for key in json_params0.keys():
            json_forms_data[key] = form.cleaned_data.get(key)

        with open('./recommend_system/api/params.json', "w") as file:
            json.dump(json_forms_data, file)

        global json_params
        json_params = json_forms_data
        #form.cleaned_data.get('MIN_VISITS_INTEREST')
        return super(ParamsConfigView, self).form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        with open('./recommend_system/api/params.json') as file:
            params = json.load(file)
        for key in params.keys():
            initial[key] = params[key]
        return initial

class UrlsConfigView(FormView):
    form_class = UrlsConfigForms
    template_name = 'recommend_system/urlsconf.html'
    success_url = '/api/formurls/'

    def form_valid(self, form):

        with open('./recommend_system/api/urls_backend.json') as file_read:
            json_urls0 = json.load(file_read)
        json_forms_data = {}

        for key in json_urls0.keys():
            json_forms_data[key] = form.cleaned_data.get(key)

        with open('./recommend_system/api/urls_backend.json', "w") as file:
            json.dump(json_forms_data, file)

        global json_urls
        json_urls = json_forms_data
        global url_projects_list
        url_projects_list = json_forms_data.get('url_projects_list')
        
        #form.cleaned_data.get('MIN_VISITS_INTEREST')
        return super(UrlsConfigView, self).form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        with open('./recommend_system/api/urls_backend.json') as file:
            urls = json.load(file)
        for key in urls.keys():
            initial[key] = urls[key]
        return initial

