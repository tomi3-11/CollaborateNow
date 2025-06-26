# Defining the URLS for the accounts app
from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('create_project/', views.create_project, name='create_project'),
    path('create_project/step1/', views.create_project_wizard_step1, name='create_project_wizard_step1'),
    path('create_project/step2/', views.create_project_wizard_step2, name='create_project_wizard_step2'),
    path('create_project/step3/', views.create_project_wizard_step3, name='create_project_wizard_step3'),
    path('create_project/submit/', views.create_project_wizard_submit, name='create_project_wizard_submit'),
    path('project_submitted/', views.project_submitted, name='project_submitted'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/join/<int:project_id>/', views.join_project, name='join_project'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('my_projects/', views.joined_projects, name='my_projects'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]