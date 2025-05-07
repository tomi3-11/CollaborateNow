# Create Custom URL patterns for the forum app

from django.urls import path
from . import views

app_name = 'forum'
urlpatterns = [
    path('forum/', views.forum_topic_list, name='forum_topic_list'),
    path('forum/create_topic', views.create_topic, name='create_topic'),
    path('forum/topic/<int:topic_id>/', views.forum_topic_detail, name='forum_topic_detail'),
    path('forum/topic/<int:topic_id>/post/', views.create_post, name='create_post'),
    path('forum/post/edit/<int:post_id>', views.edit_post, name='edit_post'),
    path('forum/post/delete/<int:post_id>', views.delete_post, name='delete_post'),
    path('forum/search/', views.forum_search, name='forum_search'),
]