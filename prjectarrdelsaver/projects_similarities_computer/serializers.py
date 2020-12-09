from rest_framework import serializers
from .models import ProjectItem, SimilarityItem
#from rest_framework_mongoengine.serializers import DocumentSerializer, EmbeddedDocumentSerializer


# class SimilarityItemSerializer(EmbeddedDocumentSerializer):
#     class Meta:
#         model = SimilarityItem
#         fields = [
#             'idrepartition',
#             'similarity_value'
#         ]

# class ProjectItemSerializer(DocumentSerializer):
#     others_projects = SimilarityItemSerializer(many=True, read_only=True)
#     class Meta:
#         model = ProjectItem
#         fields = [
#             'idrepartition',
#             'others_projects'
#         ]
#         depth = 2

class ProjectItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectItem
        fields = [
            'idrepartition',
            'others_projects'
        ]
