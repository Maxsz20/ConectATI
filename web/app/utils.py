from .models import Notificacion, Publicacion, Usuario
from django.utils import timezone
import os
from django.conf import settings

def crear_notificacion(usuario_destino, tipo, contenido, emisor=None, por_correo=False):
    if not usuario_destino:
        return

    Notificacion.objects.using('conectati').create(
        usuario=usuario_destino,
        emisor=emisor,
        tipo=tipo,
        contenido=contenido,
        leida=False,
        por_correo=por_correo,
        fecha=timezone.now()
    )

# Logica para procesar publicaciones
def procesar_publicacion(request, form):
    if not form.is_valid():
        return None  # O maneja errores si quieres mostrar mensajes

    data = form.cleaned_data
    archivo_obj = request.FILES.get('archivo')
    archivo_nombre = None

    if archivo_obj:
        ruta_media = os.path.join(settings.MEDIA_ROOT, 'publicaciones')
        os.makedirs(ruta_media, exist_ok=True)

        archivo_nombre = archivo_obj.name
        ruta_completa = os.path.join(ruta_media, archivo_nombre)

        with open(ruta_completa, 'wb+') as destino:
            for chunk in archivo_obj.chunks():
                destino.write(chunk)

    if not data['texto'] and not archivo_nombre:
        return None  # O agrega lógica para errores personalizados

    usuario = Usuario.objects.using('conectati').get(id=request.session['usuario_id'])
    nueva = Publicacion(
        usuario=usuario,
        texto=data['texto'],
        archivo_nombre=archivo_nombre,
        privacidad=data['privacidad'].lower(),
        fecha=timezone.now()
    )
    nueva.save(using='conectati')
    return nueva
