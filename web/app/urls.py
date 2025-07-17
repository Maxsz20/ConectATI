# web/app/urls.py

from django.urls import path
from . import views

urlpatterns = [
#    path('', views.index, name='index'),
#    path('feed/', views.feed, name='feed'),
#    path('notificaciones/', views.notificaciones, name='notificaciones'),
    path('amistades/', views.FriendView, name='amistades'),
#    path('chat/', views.chat, name='chat'),
#    path('configuracion/', views.configuracion, name='configuracion'),
#    path('publicar/', views.publicar, name='publicar'),
#    path('busqueda/', views.busqueda, name='busqueda'),
#    path('perfil/', views.perfil, name='perfil'),
#    path('logout/', views.logout_view, name='logout'),
#    path('login/', views.login_view, name='login'),
#    path('registro/', views.registro, name='registro'),
]
