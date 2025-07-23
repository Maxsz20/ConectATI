from django.contrib import admin
from .models import (
    Usuario, Amistad, Chat, Comentario,
    Configuracion, Mensaje, Notificacion, Publicacion
)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'email', 'ci', 'fecha_nacimiento', 'genero', 'foto')
    search_fields = ('nombre', 'email', 'ci')
    list_filter = ('genero',)
    ordering = ('nombre',)
    readonly_fields = ('id',)


@admin.register(Amistad)
class AmistadAdmin(admin.ModelAdmin):
    list_display = ('id', 'de_nombre', 'para_nombre', 'estado', 'fecha')
    search_fields = ('de_usuario__nombre', 'para_usuario__nombre')
    list_filter = ('estado', 'fecha')
    ordering = ('-fecha',)

    def de_nombre(self, obj):
        return obj.de_usuario.nombre
    de_nombre.short_description = 'De'

    def para_nombre(self, obj):
        return obj.para_usuario.nombre
    para_nombre.short_description = 'Para'


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario1_nombre', 'usuario2_nombre', 'fecha_inicio')
    ordering = ('-fecha_inicio',)

    def usuario1_nombre(self, obj):
        return obj.usuario1.nombre
    usuario1_nombre.short_description = 'Usuario 1'

    def usuario2_nombre(self, obj):
        return obj.usuario2.nombre
    usuario2_nombre.short_description = 'Usuario 2'


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'publicacion_id', 'usuario_nombre', 'texto_corto', 'fecha')
    search_fields = ('texto',)
    list_filter = ('fecha',)
    ordering = ('-fecha',)

    def usuario_nombre(self, obj):
        return obj.usuario.nombre
    usuario_nombre.short_description = 'Usuario'

    def texto_corto(self, obj):
        return (obj.texto[:50] + '...') if len(obj.texto) > 50 else obj.texto
    texto_corto.short_description = 'Texto'


@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'tema', 'idioma', 'publicaciones_privadas')
    list_filter = ('tema', 'idioma', 'publicaciones_privadas')


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_id', 'emisor_nombre', 'texto_corto', 'fecha')
    ordering = ('-fecha',)
    search_fields = ('texto',)

    def emisor_nombre(self, obj):
        return obj.emisor.nombre
    emisor_nombre.short_description = 'Emisor'

    def texto_corto(self, obj):
        return (obj.texto[:50] + '...') if len(obj.texto) > 50 else obj.texto
    texto_corto.short_description = 'Mensaje'


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario_nombre', 'tipo', 'leida', 'fecha')
    list_filter = ('tipo', 'leida', 'por_correo', 'fecha')
    search_fields = ('contenido',)
    ordering = ('-fecha',)

    def usuario_nombre(self, obj):
        return obj.usuario.nombre
    usuario_nombre.short_description = 'Usuario'


@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario_nombre', 'texto_corto', 'privacidad', 'fecha')
    search_fields = ('texto',)
    list_filter = ('privacidad', 'fecha')
    ordering = ('-fecha',)

    def usuario_nombre(self, obj):
        return obj.usuario.nombre
    usuario_nombre.short_description = 'Usuario'

    def texto_corto(self, obj):
        return (obj.texto[:50] + '...') if obj.texto and len(obj.texto) > 50 else obj.texto
    texto_corto.short_description = 'Texto'
