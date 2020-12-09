from django.urls import path

from recommend_system.api.views import *

urlpatterns = [
    #path('<str:user>/<str:item_code>', ListRecommendItemView.as_view(), name='item-recommand'),
    path('recommand_content/<str:user_id>', RecommandProjectView2.as_view()),
    path('recommand_collab_filter/<str:user_id>', RecommandProjectView.as_view()),
    path('recommanditem/<str:user_id>/<str:item>', ListRecommendItemView.as_view()),
    path('updatedfs/', update_users_dataframe),
    path('projsundesired/', ProjectsUndesiredListView.as_view()),
    path('formparams/', ParamsConfigView.as_view(), name='form_params'),
    path('formurls/', UrlsConfigView.as_view(), name='form_urls')
]