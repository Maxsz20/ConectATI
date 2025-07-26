# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.TextField()
    username = models.TextField(unique=True) 
    email = models.TextField(unique=True)
    ci = models.TextField(unique=True)
    foto = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    genero = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    color_favorito = models.TextField(blank=True, null=True)
    libro_favorito = models.TextField(blank=True, null=True)
    musica_favorita = models.TextField(blank=True, null=True)
    videojuegos = models.TextField(blank=True, null=True)
    lenguajes = models.TextField(blank=True, null=True)
    contrasena = models.TextField()

    class Meta:
        managed = False
        db_table = 'Usuario'
        app_label = 'app'

    def __str__(self):
        return f"Usuario: {self.nombre} {self.username} ({self.email})"


class Amistad(models.Model):
    de_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    para_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='amistad_para_usuario_set')
    estado = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Amistad'
        app_label = 'app'


class Chat(models.Model):
    usuario1 = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    usuario2 = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='chat_usuario2_set')
    fecha_inicio = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Chat'
        app_label = 'app'


class Comentario(models.Model):
    publicacion = models.ForeignKey('Publicacion', on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha = models.DateTimeField(blank=True, null=True)
    respuesta_a = models.ForeignKey('self', on_delete=models.CASCADE, db_column='respuesta_a', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Comentario'
        app_label = 'app'


class Configuracion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tema = models.TextField(blank=True, null=True)
    idioma = models.TextField(blank=True, null=True)
    publicaciones_privadas = models.BooleanField(blank=True, null=True)
    notificar_chat = models.BooleanField(blank=True, null=True)
    notificar_comentario = models.BooleanField(blank=True, null=True)
    notificar_amistad = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Configuracion'
        app_label = 'app'


class Mensaje(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    emisor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Mensaje'
        app_label = 'app'


class Notificacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # receptor
    emisor = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True, related_name='notificaciones_emitidas')  # nuevo campo
    tipo = models.TextField(blank=True, null=True)
    contenido = models.TextField(blank=True, null=True)
    leida = models.BooleanField(blank=True, null=True, default=False)
    por_correo = models.BooleanField(blank=True, null=True, default=False)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Notificacion'
        app_label = 'app'


class Publicacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    texto = models.TextField(blank=True, null=True)
    archivo_nombre = models.TextField(blank=True, null=True)
    privacidad = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    estrellas = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'Publicacion'
        app_label = 'app'

class Estrella(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'Estrella'
        app_label = 'app'
        unique_together = ('usuario', 'publicacion')

class SolicitudChat(models.Model):
    de_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitudes_chat_enviadas')
    para_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitudes_chat_recibidas')
    estado = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada')], default='pendiente')
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_aceptada = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'SolicitudChat'
        app_label = 'app'
        unique_together = ('de_usuario', 'para_usuario')

    def __str__(self):
        return f"Solicitud de {self.de_usuario.username} a {self.para_usuario.username} ({self.estado})"

