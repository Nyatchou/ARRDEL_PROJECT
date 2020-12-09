from djongo import models
# Create your models here.
#from mongoengine import *
from django import forms


class SimilarityItem(models.Model):
    idrepartition = models.CharField(max_length=80)
    similarity_value = models.FloatField()
    class Meta:
        abstract = True

class SimilarityItemForm(forms.ModelForm):
    class Meta:
        model = SimilarityItem
        fields = [
            'idrepartition',
            'similarity_value'
        ]

class ProjectItem(models.Model):
    idrepartition = models.CharField(max_length=80)
    others_projects = models.ArrayField(
        model_container= SimilarityItem, 
        model_form_class= SimilarityItemForm   
    )


# class SimilarityItem(EmbeddedDocument):
#     idrepartition = StringField(max_length=80)
#     similarity_value = FloatField()


# class ProjectItem(Document):
#     idrepartition = StringField(max_length=80)
#     others_projects = ListField(
#         EmbeddedDocumentField(SimilarityItem)
#     )
