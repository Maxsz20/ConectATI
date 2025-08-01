# web/app/urls.py

from django.urls import path
from . import views

urlpatterns = [
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
    path('publicacion/<int:publicacion_id>/', views.PostView, name='post'),
    path('search_mobile/', views.SearchMobileView, name='search_mobile'),
    path('profile/', views.ProfileView, name='profile'),
    path('editprofile/', views.EditProfileView, name='editprofile'),
    path('post_mobile/', views.PostMobileView, name='post_mobile'),
    path('reply_mobile/<int:publicacion_id>/', views.ReplyMobileView, name='reply_mobile'),
    path('reply_mobile_comment/<int:comentario_id>/', views.ReplyToCommentMobileView, name='reply_mobile_comment'), 
    path('logout/', views.LogoutView, name='logout'),
    path('publicacion/<int:publicacion_id>/estrella/', views.dar_estrella, name='dar_estrella'),
    path('buscar-usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
    path('enviar-solicitud-amistad/', views.enviar_solicitud_amistad, name='enviar_solicitud_amistad'),
    path('aceptar-solicitud/', views.aceptar_solicitud, name='aceptar_solicitud'),
    path('rechazar-solicitud/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('usuario/<int:usuario_id>/', views.ProfileView, name='ver_perfil_usuario'),
    path('enviar-solicitud-chat/', views.enviar_solicitud_chat, name='enviar_solicitud_chat'),
    path('aceptar-solicitud-chat/', views.aceptar_solicitud_chat, name='aceptar_solicitud_chat'),
    path('rechazar-solicitud-chat/', views.rechazar_solicitud_chat, name='rechazar_solicitud_chat'),
    path('obtener-conversacion/', views.obtener_conversacion, name='obtener_conversacion'),
    path('obtener-mensajes-chat/', views.obtener_mensajes_chat, name='obtener_mensajes_chat'),
    path('comentar/', views.crear_comentario, name='crear_comentario'),
    path('eliminar-foto-perfil/', views.eliminar_foto_perfil, name='eliminar_foto_perfil'),
    path('notificaciones/marcar_leidas/', views.marcar_notificaciones_leidas, name='marcar_leidas'),
    path('eliminar-amistad/', views.eliminar_amistad, name='eliminar_amistad'),
    path('eliminar-chat/', views.eliminar_chat, name='eliminar_chat'),
    path('verificar-codigo/', views.verificar_codigo, name='verificar_codigo'),
    path('enviar-codigo/', views.enviar_codigo, name='enviar_codigo'),
    path('cambiar-clave/', views.cambiar_password, name='cambiar-clave'),
    path('comentario/<int:comentario_id>/', views.CommentThreadView, name='comentario_hilo'),
    path("guardar-idioma/", views.guardar_idioma, name="guardar_idioma"),
    path("marcar_leida_individual/", views.marcar_notificacion_individual, name="marcar_leida_individual"),
    path("guardar-privacidad/", views.guardar_privacidad, name="guardar_privacidad"),
]
