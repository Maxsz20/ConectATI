from django.contrib import admin
from .models import (
    Usuario, Amistad, Chat, Comentario,
    Configuracion, Mensaje, Notificacion, Publicacion
)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'email', 'ci')
    search_fields = ('nombre', 'email', 'ci')

@admin.register(Amistad)
class AmistadAdmin(admin.ModelAdmin):
    list_display = ('id', 'de_usuario', 'para_usuario', 'estado', 'fecha')
    search_fields = ('de_usuario__nombre', 'para_usuario__nombre')

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario1', 'usuario2', 'fecha_inicio')

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'publicacion', 'usuario', 'texto', 'fecha', 'respuesta_a')
    search_fields = ('texto',)

@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'tema', 'idioma', 'publicaciones_privadas')

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'emisor', 'texto', 'fecha')

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'tipo', 'leida', 'fecha')

@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'texto', 'fecha')
    search_fields = ('texto',)
