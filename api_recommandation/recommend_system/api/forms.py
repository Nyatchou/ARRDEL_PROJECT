from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
import json



class ParamsForm(forms.Form):

    MIN_VISITS_INTEREST = forms.IntegerField(min_value=1, max_value=20)
    NB_VISITS_INTEREST = forms.IntegerField(min_value=1, max_value=50)
    MIN_COEFF_SIMILARITY_USERS = forms.FloatField(min_value=0, max_value=1.0)
    MIN_COEFF_SIMILARITY_USERS_APPROACH = forms.FloatField(min_value=0, max_value=1.0)
    MIN_COEFF_SIMILARITY_PROJECTS = forms.FloatField(min_value=0, max_value=1.0)
    NB_MAX_RECOMMANDATIONS = forms.IntegerField(min_value=1, max_value=1000)
    NB_SIMILAR_PROJECTS_BY_PROJECT = forms.IntegerField(min_value=1, max_value=500)
    NB_PROJECTS_UNDESIDED = forms.IntegerField(min_value=0, max_value=1000)
    PERIOD_RECOMMAND = forms.IntegerField(min_value=1, max_value=50)
    def __init__(self, *args, **kwargs):
        super(ParamsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('Valider', 'Valider'))



class UrlsConfigForms(forms.Form):
    url_users_visits_datas = forms.URLField()
    url_projects_list = forms.URLField()
    url_user_recommands_count = forms.URLField()
    url_datas_visits_commune = forms.URLField()
    url_datas_visits_departement = forms.URLField()
    url_projects_similarities = forms.URLField()
    def __init__(self, *args, **kwargs):
        super(UrlsConfigForms, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('Valider', 'Valider'))
