from django.urls import path

from . import views

urlpatterns = [ 
    path('', views.index, name='index'),
    path('project/', views.ProjectView.as_view(), name='all_projects'),
    path('project/new/', views.create_update_project, name='new_project'),
    path('project/<int:pk>/delete/', views.ProjectDelete.as_view(), name='delete_project'),
    path('project/<int:project_id>/edit/', views.create_update_project, name='edit_project'),
    path('project/<int:pk>/', views.OneProjectView.as_view(), name='one_project'),
]