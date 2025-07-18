# web/app/urls.py

from django.urls import path
from . import views

urlpatterns = [
#    path('', views.index, name='index'),
    path('app/login/', views.LoginView, name='login'),
    path('app/register/', views.RegisterView, name='register'),
    path('app/forgotten_password/', views.ForgottenPassView, name = 'forgotten_password'),
    path('app/forgotten_password/check_code/', views.CheckCodeView, name = 'check_code'),
    path('app/forgotten_password/check_code/change_password', views.ChangePassView, name = 'change_password'),
    path('app/feed/', views.FeedView, name='feed'),
    path('app/notifications/', views.NotifyView, name='notifications'),
    path('app/friends/', views.FriendView, name='friends'),
    path('app/chat/', views.ChatView, name='chat'),
    path('app/settings/', views.SettingsView, name='settings'),
    path('app/post/', views.PostView, name='post'),
    path('app/search/', views.SearchView, name='search'),
    path('app/search_mobile/', views.SearchMobileView, name='search_mobile'),
    path('app/profile/', views.ProfileView, name='profile'),
    path('app/editprofile/', views.EditProfileView, name='editprofile'),
    path('app/post_mobile/', views.PostMobileView, name='post_mobile'),
    path('app/reply_mobile/', views.ReplyMobileView, name='reply_mobile'),
    
    ]
