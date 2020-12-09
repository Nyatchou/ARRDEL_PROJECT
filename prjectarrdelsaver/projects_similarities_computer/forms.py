from django import forms
import pandas as pd
from .models import ProjectItem
import requests



resdatas = requests.get('http://127.0.0.1:8000/serverapi/projects/')

datas = resdatas.json()
list_keys = datas[0].keys()
datas = [item.values() for item in datas]
df = pd.DataFrame(datas, columns=list_keys)
df.rename(columns = {'id_repartition': 'IDRepartition', 'id_tache':'IDTache', 'commune': 'Commune', 'departement':'Departement', 'region':'Région'},
 inplace=True)
df = df.assign(IDSecteur = lambda x: 'NaN' )
df = df.assign(IDChapitre = lambda x: 'NaN' )



IDSECTEURS = list(df['IDSecteur'].unique())
IDSECTEURS = [(item, item) for item in IDSECTEURS]
IDCHAPITRES = list(df['IDChapitre'].unique())
IDCHAPITRES = [(item, item) for item in IDCHAPITRES]
COMMUNES = list(df['Commune'].unique())
COMMUNES = [(item, item) for item in COMMUNES]


class ProjectCaractsForm(forms.Form):
    idrepartition = forms.CharField(max_length=80)
    idtache = forms.CharField(max_length=80)
    intitule = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows':2}))
    commune = forms.ChoiceField(choices=COMMUNES, widget=forms.Select(attrs={'class': 'browser-default custom-select'}))
    chapitre = forms.ChoiceField(choices=IDCHAPITRES, widget=forms.Select(attrs={'class': 'browser-default custom-select'}))
    secteur = forms.ChoiceField(choices=IDSECTEURS, widget=forms.Select(attrs={'class': 'browser-default custom-selects'}))

    def clean_idrepartition(self):
        idrep = self.cleaned_data.get('idrepartition')
        try:
            project = ProjectItem.objects.get(idrepartition=idrep)
            raise forms.ValidationError('Cet identifiant de projet existe déjà !')
        except ProjectItem.DoesNotExist:
            pass
        return idrep