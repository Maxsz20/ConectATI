# web/app/urls.py

from django.urls import path
from . import views

urlpatterns = [
#    path('', views.index, name='index'),
    path('login/', views.LoginView, name='login'),
    path('register/', views.RegisterView, name='register'),
    path('forgotten_password/', views.ForgottenPassView, name = 'forgotten_password'),
    path('forgotten_password/check_code/', views.CheckCodeView, name = 'check_code'),
    path('forgotten_password/check_code/change_password', views.ChangePassView, name = 'change_password'),
    path('feed/', views.FeedView, name='feed'),
    path('notifications/', views.NotifyView, name='notifications'),
    path('friends/', views.FriendView, name='friends'),
    path('chat/', views.ChatView, name='chat'),
    path('settings/', views.SettingsView, name='settings'),
    path('post/', views.PostView, name='post'),
    path('search/', views.SearchView, name='search'),
    path('search_mobile/', views.SearchMobileView, name='search_mobile'),
    path('profile/', views.ProfileView, name='profile'),
    path('editprofile/', views.EditProfileView, name='editprofile'),
    path('post_mobile/', views.PostMobileView, name='post_mobile'),
    path('reply_mobile/', views.ReplyMobileView, name='reply_mobile'),
    path('logout/', views.LogoutView, name='logout'),
    path('publicacion/<int:publicacion_id>/estrella/', views.dar_estrella, name='dar_estrella'),
    path('buscar-usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
    path('enviar-solicitud-amistad/', views.enviar_solicitud_amistad, name='enviar_solicitud_amistad'),
    path('aceptar-solicitud/', views.aceptar_solicitud, name='aceptar_solicitud'),
    path('rechazar-solicitud/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('usuario/<int:usuario_id>/', views.ver_perfil_usuario, name='ver_perfil_usuario'),
]
