from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Region(models.Model):
    code = models.CharField(max_length = 50)
    nom = models.CharField(max_length = 100)

    def __str__(self):
        return self.nom

class Departement(models.Model):
    code = models.CharField(max_length = 50)
    nom = models.CharField(max_length = 100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nom

class Commune(models.Model):
    code = models.CharField(max_length = 50)
    nom = models.CharField(max_length = 100)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom

class Project(models.Model):
    intitule = models.TextField()
    id_repartition = models.CharField(max_length= 50, unique=True)
    id_tache = models.CharField(max_length=50)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE)

    def __str__(self):
        return self.id_repartition

class BehaviorInProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    visits_count = models.IntegerField()
    behavior_interesting = models.IntegerField(default=0)
    print_project_file = models.IntegerField(default=0)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class BehaviorWhenRecommand(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nb_recommandations = models.IntegerField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class CommuneVisitsCount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE)
    visits_count = models.IntegerField(default=1)


class DepartementVisitsCount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE)
    visits_count = models.IntegerField(default=1)

class ProjectVisitsCount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    visits_count = models.IntegerField(default=1)


    