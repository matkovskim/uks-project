from django.urls import path

from . import views

urlpatterns = [ 
    path('', views.index, name='index'),
    
    #projects
    path('project/', views.ProjectView.as_view(), name='all_projects'),
    path('project/new/', views.create_update_project, name='new_project'),
    path('project/<int:pk>/delete/', views.ProjectDelete.as_view(), name='delete_project'),
    path('project/<int:project_id>/edit/', views.create_update_project, name='edit_project'),
    path('project/<int:pk>/', views.OneProjectView.as_view(), name='one_project'),

    #issues
    path('project/<int:project_id>/issue/new/', views.create_update_issue, name='new_issue'),
    path('project/<int:project_id>/issue/<int:pk>/', views.OneIssueView.as_view(), name='one_issue'),
    path('project/<int:project_id>/issue/<int:pk>/delete/', views.IssueDelete.as_view(), name='delete_issue'),
    path('project/<int:project_id>/issue/<int:issue_id>/edit/', views.create_update_issue, name='edit_issue'),
    path('project/<int:project_id>/issue/<int:issue_id>/changestate/', views.change_issue_state, name='change_state_issue'),

    #search
    path('search/', views.search_projects, name='search'),

]