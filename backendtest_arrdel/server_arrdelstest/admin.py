from django.contrib import admin
from server_arrdelstest.models import *
# Register your models here.
admin.site.register(Project)
admin.site.register(Commune)
admin.site.register(Departement)
admin.site.register(Region)
admin.site.register(CommuneVisitsCount)
admin.site.register(DepartementVisitsCount)
admin.site.register(ProjectVisitsCount)
admin.site.register(BehaviorInProject)
admin.site.register(BehaviorWhenRecommand)