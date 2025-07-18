# web/app/urls.py

from django.urls import path
from . import views

urlpatterns = [
#    path('', views.index, name='index'),
    path('login/', views.LoginView, name='login'),
    path('register/', views.RegisterView, name='register'),
    path('forgotten_password/', views.ForgottenPassView, name = 'forgotten_password'),
    path('feed/', views.FeedView, name='feed'),
    path('notifications/', views.NotifyView, name='notifications'),
    path('friends/', views.FriendView, name='friends'),
    path('chat/', views.ChatView, name='chat'),
    path('settings/', views.SettingsView, name='settings'),
    path('post/', views.PostView, name='post'),
    path('search/', views.SearchView, name='search'),
    path('profile/', views.ProfileView, name='profile'),
]
