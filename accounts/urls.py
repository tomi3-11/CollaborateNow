# Defining the URLS for the accounts app
from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('create_project/', views.create_project, name='create_project'),
    path('project_submitted/', views.project_submitted, name='project_submitted'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/join/<int:project_id>/', views.join_project, name='join_project'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('my_projects/', views.joined_projects, name='my_projects'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]