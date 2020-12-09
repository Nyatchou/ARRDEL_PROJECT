from rest_framework import serializers
from server_arrdelstest.models import  *

class BehaviorInProjectSerializer(serializers.ModelSerializer):
    projectcode = serializers.SerializerMethodField(read_only=True) 
    class Meta:
        model = BehaviorInProject
        fields = [
            'user',
            'visits_count',
            'behavior_interesting',
            'print_project_file',
            'projectcode'
        ]
    def get_projectcode(self, obj):
        return obj.project.id_repartition

class BehaviorWhenRecommandSerializer(serializers.ModelSerializer):
    projectcode = serializers.SerializerMethodField(read_only=True) 
    class Meta:
        model = BehaviorWhenRecommand
        fields = [
            'user',
            'nb_recommandations',
            'projectcode'
        ]
    def get_projectcode(self, obj):
        return obj.project.id_repartition

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = ['id']

class CommuneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commune
        exclude = ['id']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departement
        exclude = ['id']


class ProjectVisitsCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectVisitsCount
        exclude = ['id']

class CommuneVisitsCountSerializer(serializers.ModelSerializer):
    commune_code = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CommuneVisitsCount
        fields =[
            'commune_code',
            'visits_count'
        ]

    def get_commune_code(self, obj):
        return obj.commune.code

class DepartmentVisitsCountSerializer(serializers.ModelSerializer):

    dept_code = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = DepartementVisitsCount
        fields = [
            'dept_code',
            'visits_count'
        ]
    def get_dept_code(self, obj):
        return obj.departement.code