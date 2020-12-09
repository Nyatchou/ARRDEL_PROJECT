from server_arrdelstest.models import *
from server_arrdelstest.api.serializers import *
from rest_framework import generics, response, status
import pandas as pd
from server_arrdelstest.models import *
import string
import random
from django.http import HttpResponse, JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_project_object(request):
    idrep = request.POST.get('idrepartition')
    intitule = request.POST.get('intitule')
    idtache = request.POST.get('idtache')
    nomcommune = request.POST.get('commune')
    commune = Commune.objects.get(nom=nomcommune)
    departement = commune.departement
    region = departement.region
    project = Project.objects.create(id_repartition=idrep, intitule=intitule, id_tache=idtache, commune=commune)
    data = {
        'idrepartition': project.id_repartition,
        'idtache': project.id_tache,
        'intitule' : project.intitule,
        'commune' : commune.nom,
        'departement' : departement.nom,
        'region' : region.nom
    }
    return JsonResponse(data=data)

class RendAllVisitsAndBehavior(generics.ListAPIView):
    serializer_class = BehaviorInProjectSerializer
    queryset = BehaviorInProject.objects.all()
    
    def get(self, request , *args , **kwargs):
        query = self.get_queryset()
        data = self.serializer_class(query, many=True).data
        for item in data:
            item['User'] = item.pop('user')
            item['Behavior_interesting'] = item.pop('behavior_interesting')
            item['Print_project_file'] = item.pop('print_project_file')
            item['Visit_count'] = item.pop('visits_count')
            item['IDRepartition'] = item.pop('projectcode')
        return response.Response(data=data, status=status.HTTP_200_OK)
    # def get(self, request , *args , **kwargs):
    #     pass

class RendVisitsAndBehaviorForSingleUser(generics.ListAPIView):
    serializer_class = BehaviorInProjectSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user')
        return BehaviorInProject.objects.filter(user=user_id)
    
    def get(self, request , *args , **kwargs):
        try:
            user = User.objects.get(pk=self.kwargs.get('user'))
            query = self.get_queryset()
            data = self.serializer_class(query, many=True).data
            for item in data:
                item['User'] = item.pop('user')
                item['Behavior_interesting'] = item.pop('behavior_interesting')
                item['Print_project_file'] = item.pop('print_project_file')
                item['Visit_count'] = item.pop('visits_count')
                item['IDRepartition'] = item.pop('projectcode')
            return response.Response(data=data, status=status.HTTP_200_OK)
        except :
            return response.Response("User does not exist", status=status.HTTP_404_NOT_FOUND)


class RendNBRecommandationsForProjectsSingleUser(generics.ListAPIView):
    serializer_class = BehaviorWhenRecommandSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user')
        return BehaviorWhenRecommand.objects.filter(user=user_id)

    def get(self, request , *args , **kwargs):
        try:
            user = User.objects.get(pk=self.kwargs.get('user'))
            query = self.get_queryset()
            data = self.serializer_class(query, many=True).data
            for item in data:
                item.pop('user')
            return response.Response(data=data, status=status.HTTP_200_OK)
        except :
            return response.Response("User does not exist", status=status.HTTP_404_NOT_FOUND)


class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def get(self, request , *args , **kwargs):
        query = self.get_queryset()
        data = self.serializer_class(query, many=True).data

        for item in data:
            commune = Commune.objects.get(id = item['commune'])
            departement = commune.departement
            region = departement.region
            item['commune'] = commune.nom
            item['departement'] = departement.nom
            item['region'] = region.nom

        return response.Response(data, status=status.HTTP_200_OK)

class VisitsCommuneListView(generics.ListAPIView):
    serializer_class = CommuneVisitsCountSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user')
        return CommuneVisitsCount.objects.filter(user=user_id)

    def get(self, request , *args , **kwargs):
        try:
            user = User.objects.get(pk=self.kwargs.get('user'))
            query = self.get_queryset()
            data = self.serializer_class(query, many=True).data
            dict_data = dict()
            for item in data:
                dict_data[item['commune_code']] = item['visits_count']

            datas = {
                'item' : 'Code_Commune',
                'data' : dict_data
            }

            return response.Response(datas, status=status.HTTP_200_OK)
        except :
            return response.Response("User does not exist", status=status.HTTP_404_NOT_FOUND)        

class VisitsDepartementListView(generics.ListAPIView):
    serializer_class = DepartmentVisitsCountSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user')
        return DepartementVisitsCount.objects.filter(user=user_id)

    def get(self, request , *args , **kwargs):
        try:
            user = User.objects.get(pk=self.kwargs.get('user'))
            query = self.get_queryset()
            data = self.serializer_class(query, many=True).data
            dict_data = dict()
            for item in data:
                dict_data[item['dept_code']] = item['visits_count']

            datas = {
                'item' : 'Code_Departement',
                'data' : dict_data
            }

            return response.Response(datas, status=status.HTTP_200_OK)
        except :
            return response.Response("User does not exist", status=status.HTTP_404_NOT_FOUND)        

def create_all_objects(request):
    # data = pd.read_excel (r'C:\Users\Utilisateur\Notebooks\Liste des Projets.xlsx')
    # df = pd.DataFrame(data, columns = ['IDTache', 'IDRepartition', 'IDSecteur', 'Intitulé', 'IDChapitre', 'Commune', 'Departement', 'Région', 'xCommune', 'xDepartement', 'xRégion'])
    # # for row_ind in df.index.values:
    # #     row = df.iloc[row_ind]
    # #     region, createdr = Region.objects.get_or_create(code = row['xRégion'], nom = row['Région'])
    # #     departement, createdd = Departement.objects.get_or_create(code = row['xDepartement'], nom=row['Departement'], region=region)
    # #     commune, createdc = Commune.objects.get_or_create(code=row['xCommune'], nom=row['Commune'], departement=departement)
    # #     projet, createdp = Project.objects.get_or_create(intitule=row['Intitulé'], id_repartition=row['IDRepartition'], id_tache=row['IDTache'], commune=commune)


    recommands_count_df = pd.read_pickle('./server_arrdelstest/api/dataframe_files/recommands_count_df.pkl')
    # users_df = pd.read_pickle('./server_arrdelstest/api/dataframe_files/users_dataframe.pkl')
    # userscommunes_visits = pd.read_pickle('./server_arrdelstest/api/dataframe_files/userscommunes_visits.pkl') 
    # usersdepartements_visits = pd.read_pickle('./server_arrdelstest/api/dataframe_files/usersdepartements_visits.pkl') 

    # # def make_random_username():
    # #     digits_list = list(string.ascii_letters) + ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    # #     ind = random.randint(26, 51)
    # #     username = digits_list[ind]
    # #     rand_len = random.randint(8, 35)
    # #     for _ in range(rand_len):
    # #         index_rand = random.randint(0, 61)
    # #         username += digits_list[index_rand]
    # #     return username


    # # for _ in range(500):
    # #     User.objects.create_user(username=make_random_username(), password='azerty45.0*')

    # for ind in range(len(users_df)):
    #     user_serie = users_df.iloc[ind]
    #     project = Project.objects.get(id_repartition=user_serie['IDRepartition'])
    #     try:
    #         data_visit_to_save, created = BehaviorInProject.objects.get_or_create(user = User.objects.get(pk=user_serie['User']),
    #         visits_count=user_serie['Visit_count'], behavior_interesting=user_serie['Behavior_interesting'], 
    #         print_project_file=user_serie['Print_project_file'], project=project)
    #     except:
    #         print('22b')

    print(recommands_count_df)
    for ind in range(len(recommands_count_df)):
        item = recommands_count_df.iloc[ind]
        project = Project.objects.get(id_repartition=item['IDRepartition'])
        try:
            data_recommandcount_to_save, created = BehaviorWhenRecommand.objects.get_or_create(user = User.objects.get(pk=item['User']), 
            project=project, nb_recommandation=item['Recommands'])
        except:
            print('11b')

    # for ind in range(20, len(userscommunes_visits)):
    #     item = userscommunes_visits.iloc[ind]
    #     try:
    #         CommuneVisitsCount.objects.create(user = User.objects.get(pk=item['User']), commune=Commune.objects.get(code=item['Code_Commune']), visits_count=item['Visits_count'] )
    #     except:
    #         print("aa")

    # for ind in range(20, len(usersdepartements_visits)):
    #     item = usersdepartements_visits.iloc[ind]
    #     try:
    #         DepartementVisitsCount.objects.create(user = User.objects.get(pk=item['User']), departement=Departement.objects.get(code=item['Code_Departement']), visits_count=item['Visits_count'] )
    #     except:
    #         print('bb')

    return HttpResponse('ok')


    