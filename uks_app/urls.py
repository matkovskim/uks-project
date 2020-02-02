from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
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

    #users
    path('register/', views.register_user, name="register"),
    path('logout/', auth_views.LogoutView.as_view(template_name = 'uks_app/logout.html'), name="logout"),
    path('login/', auth_views.LoginView.as_view(template_name = 'uks_app/login.html'), name="login"),
    path('profile/<str:id>/', views.profile, name="profile"),
    path('profile/<str:id>/update', views.profile_update, name="profile_update"),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name = 'uks_app/password_reset.html'), name="password_reset"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name = 'uks_app/password_reset_done.html'), name="password_reset_done"),
    path('password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name = 'uks_app/password_reset_confirm.html'), name="password_reset_confirm"),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name = 'uks_app/password_reset_complete.html'), name="password_reset_complete")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)