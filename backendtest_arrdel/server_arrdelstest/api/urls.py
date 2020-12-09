from django.urls import path

from server_arrdelstest.api.views import *

urlpatterns = [
    path('initdatabase/', create_all_objects ),
    path('visitsdatas/', RendAllVisitsAndBehavior.as_view()),
    path('recommandnbtimes/<int:user>', RendNBRecommandationsForProjectsSingleUser.as_view() ),
    path('visitsdata/<int:user>', RendVisitsAndBehaviorForSingleUser.as_view()),
    path('projects/', ProjectListView.as_view()),
    path('projectcreate/', create_project_object),
    path('communesvisits/<int:user>', VisitsCommuneListView.as_view()),
    path('departementsvisits/<int:user>', VisitsDepartementListView.as_view())
]