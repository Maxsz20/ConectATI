from .models import Notificacion, Publicacion, Usuario, Chat, Mensaje, Comentario, Estrella, Amistad, SolicitudChat
from django.utils import timezone
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
import json
from django.utils.translation import gettext as _

def crear_notificacion(usuario_destino, tipo, contenido, emisor=None, por_correo=False, publicacion_id=None, comentario_id=None):
    """Funcion de utilidad para crear notificaciones"""
    if not usuario_destino:
        return

    Notificacion.objects.using('conectati').create(
        usuario=usuario_destino,
        emisor=emisor,
        tipo=tipo,
        contenido=contenido,
        leida=False,
        por_correo=por_correo,
        fecha=timezone.now(),
        publicacion_id=publicacion_id,
        comentario_id=comentario_id
    )

# Logica para procesar publicaciones
def procesar_publicacion(request, form):
    """Funcion de utilidad para procesar publicaciones"""
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

@csrf_exempt
def eliminar_foto_perfil(request):
    """Funcion de utilidad para eliminar la foto de perfil del usuario"""
    if request.method == "POST" and request.session.get("usuario_id"):
        try:
            usuario = Usuario.objects.using('conectati').get(id=request.session["usuario_id"])
            if usuario.foto:
                nombre_archivo = os.path.basename(usuario.foto)
                ruta_completa = os.path.join(settings.MEDIA_ROOT, 'fotos_perfil', nombre_archivo)
                if os.path.exists(ruta_completa):
                    os.remove(ruta_completa)
                usuario.foto = ''
                usuario.save(using='conectati')
            return JsonResponse({"ok": True})
        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)})
    return JsonResponse({"ok": False, "error": "No autorizado"}, status=403)


@require_POST
def marcar_notificaciones_leidas(request):
    """Funcion de utilidad para marcar las notificaciones como leidas"""
    if not request.session.get('usuario_id'):
        return JsonResponse({'ok': False}, status=403)

    usuario_id = request.session['usuario_id']
    Notificacion.objects.using('conectati').filter(usuario_id=usuario_id, leida=False).update(leida=True)
    
    return JsonResponse({'ok': True})

@csrf_exempt
@require_POST
def marcar_notificacion_individual(request):
    """Marca como leída una notificación específica"""
    if not request.session.get('usuario_id'):
        return JsonResponse({'ok': False}, status=403)

    try:
        data = json.loads(request.body)
        notif_id = data.get('id')
        usuario_id = request.session['usuario_id']

        notificacion = Notificacion.objects.using('conectati').get(id=notif_id, usuario_id=usuario_id)
        notificacion.leida = True
        notificacion.save(using='conectati')
        return JsonResponse({'ok': True})

    except Notificacion.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'No encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

def obtener_mensajes_chat(request):
    """Funcion de utilidad para obtener los mensajes de chat entre usuarios"""
    if not request.session.get('usuario_id'):
        return JsonResponse({'error': 'No autenticado'}, status=403)

    usuario_id = request.session['usuario_id']
    otro_id = request.GET.get('usuario_id')

    try:
        chat = Chat.objects.using('conectati').get(
            (Q(usuario1_id=usuario_id, usuario2_id=otro_id) |
             Q(usuario1_id=otro_id, usuario2_id=usuario_id))
        )
        mensajes = Mensaje.objects.using('conectati').filter(chat=chat).order_by('fecha')
        datos = [{
            'texto': m.texto,
            'propio': m.emisor_id == usuario_id
        } for m in mensajes]
        return JsonResponse({'ok': True, 'mensajes': datos})
    except Chat.DoesNotExist:
        return JsonResponse({'ok': True, 'mensajes': []})


@csrf_exempt
def crear_comentario(request):
    """Función para crear comentarios o respuestas"""
    if request.method == "POST" and request.session.get('usuario_id'):
        try:
            texto = request.POST.get("texto", "").strip()
            publicacion_id = request.POST.get("publicacion_id")
            comentario_id = request.POST.get("comentario_id")  # Nuevo

            if not texto:
                return JsonResponse({"ok": False, "error": "Texto vacío"})

            usuario = Usuario.objects.using('conectati').get(id=request.session["usuario_id"])
            publicacion = Publicacion.objects.using('conectati').get(id=publicacion_id)

            comentario = Comentario(
                usuario=usuario,
                publicacion=publicacion,
                texto=texto,
                fecha=timezone.now()
            )

            # Si es respuesta a otro comentario
            if comentario_id:
                comentario_padre = Comentario.objects.using('conectati').get(id=comentario_id)
                comentario.respuesta_a = comentario_padre

            comentario.save(using='conectati')

            # Notificación
            if comentario_id:
                # Notificar al autor del comentario si no es el mismo usuario
                if comentario_padre.usuario.id != usuario.id:
                    crear_notificacion(
                        usuario_destino=comentario_padre.usuario,
                        tipo="respuesta",
                        contenido=_("respondió tu comentario"),
                        emisor=usuario,
                        publicacion_id=publicacion.id,
                        comentario_id=comentario.id
                    )
            else:
                # Comentario directo a publicación
                if publicacion.usuario.id != usuario.id:
                    crear_notificacion(
                        usuario_destino=publicacion.usuario,
                        tipo="comentario",
                        contenido=_("comentó tu publicación"),
                        emisor=usuario,
                        publicacion_id=publicacion.id
                    )

            nuevo_total = Comentario.objects.using('conectati').filter(publicacion=publicacion).count()

            return JsonResponse({
                "ok": True,
                "nuevo_total": nuevo_total,
                "comentario": {
                    "id": comentario.id,
                    "texto": comentario.texto,
                    "nombre": usuario.nombre,
                    "username": usuario.username,
                    "foto": usuario.foto if usuario.foto else '/static/images/default_user.avif',
                    "fecha": comentario.fecha.strftime("%H:%M · %d/%m/%Y"),
                    "publicacion_id": publicacion.id
                }
            })

        except Exception as e:
            print("Error al comentar:", e)
            return JsonResponse({"ok": False, "error": str(e)})

    return JsonResponse({"ok": False, "error": "No autorizado o método incorrecto"}, status=403)



def dar_estrella(request, publicacion_id):
    """Funcion de utilidad para dar estrellas a publicaciones"""
    if not request.session.get('usuario_id'):
        return JsonResponse({'error': 'No autenticado'}, status=403)

    user_id = request.session['usuario_id']
    try:
        publicacion = Publicacion.objects.using('conectati').get(id=publicacion_id)

        # Verificar si ya dio estrella
        ya_dio = Estrella.objects.using('conectati').filter(usuario_id=user_id, publicacion_id=publicacion_id).exists()
        if ya_dio:
            return JsonResponse({'ok': False, 'repetido': True})

        # Sumar estrella
        publicacion.estrellas += 1
        publicacion.save(using='conectati')

        # Crear notificación si el comentario no es propio
        if publicacion.usuario.id != user_id:
            crear_notificacion(
                usuario_destino=publicacion.usuario,
                tipo="estrella",
                contenido=_(" dio estrella a tu publicación"),
                emisor=Usuario.objects.using('conectati').get(id=user_id)
            )
        # Guardar registro
        nueva = Estrella(usuario_id=user_id, publicacion_id=publicacion_id)
        nueva.save(using='conectati')

        return JsonResponse({'ok': True, 'nuevas_estrellas': publicacion.estrellas})
    except Publicacion.DoesNotExist:
        return JsonResponse({'error': 'No encontrada'}, status=404)

def buscar_usuarios(request):
    """Funcion de utilidad para buscar usuarios"""
    try:
        # Verificar que el usuario esté autenticado mediante la sesión
        if not request.session.get('usuario_id'):
            return JsonResponse({'error': 'No autenticado'}, status=403)

        # Obtener el término de búsqueda desde los parámetros GET y limpiarlo
        query = request.GET.get('q', '').strip()
        if not query:
            # Si no hay término de búsqueda, retornar lista vacía
            return JsonResponse({'usuarios': []})

        # Obtener el ID del usuario actual para excluirlo de los resultados
        usuario_actual_id = request.session['usuario_id']
        
        # Buscar usuarios que coincidan con el nombre o username, excluyendo al usuario actual
        # Limitar a 10 resultados para optimizar rendimiento
        resultados = Usuario.objects.using('conectati') \
            .filter(Q(nombre__icontains=query) | Q(username__icontains=query)) \
            .exclude(id=usuario_actual_id)[:10]

        # Preparar lista para almacenar datos de usuarios encontrados
        usuarios_data = []
        for usuario in resultados:
            # Para cada usuario encontrado, verificar si ya existe una relación de amistad
            amistad = Amistad.objects.using('conectati').filter(
                Q(de_usuario_id=usuario_actual_id, para_usuario_id=usuario.id) |
                Q(de_usuario_id=usuario.id, para_usuario_id=usuario_actual_id)
            ).first()
            
            # Verificar si ya existe una solicitud de chat
            solicitud_chat = SolicitudChat.objects.using('conectati').filter(
                Q(de_usuario_id=usuario_actual_id, para_usuario_id=usuario.id) |
                Q(de_usuario_id=usuario.id, para_usuario_id=usuario_actual_id)
            ).first()

            # Determinar el estado de la solicitud de chat (pendiente, aceptada, etc.)
            estado_chat = None
            if solicitud_chat:
                estado_chat = solicitud_chat.estado

            # Determinar el estado de la amistad (pendiente, aceptada, etc.)
            estado_amistad = None
            if amistad:
                estado_amistad = amistad.estado  # ← esto puede ser 'pendiente', 'aceptada', etc.

            # Agregar datos del usuario a la lista de resultados
            usuarios_data.append({
                'id': usuario.id,
                'nombre': usuario.nombre,
                'username': usuario.username,
                'foto': usuario.foto if usuario.foto else '/static/images/default_user.avif',
                'estado_amistad': estado_amistad,
                'estado_chat': estado_chat,
            })

        # Retornar los usuarios encontrados en formato JSON
        return JsonResponse({'usuarios': usuarios_data})
    
    except Exception as e:
        return JsonResponse({'error': 'Error interno en la búsqueda'}, status=500)

def obtener_conversacion(request):
    """Funcion de utilidad para obtener los mensajes de chat entre usuarios"""
    if not request.session.get('usuario_id'):
        return JsonResponse({'error': 'No autenticado'}, status=403)

    usuario_id = request.session['usuario_id']
    chat_id = request.GET.get('chat_id')

    try:
        chat = Chat.objects.using('conectati').get(id=chat_id)
        mensajes = Mensaje.objects.using('conectati').filter(chat=chat).order_by('fecha')

        mensajes_data = []
        for msg in mensajes:
            mensajes_data.append({
                'id': msg.id,
                'texto': msg.texto,
                'es_emisor': msg.emisor.id == usuario_id
            })

        return JsonResponse({'ok': True, 'mensajes': mensajes_data})
    except Chat.DoesNotExist:
        return JsonResponse({'error': 'Chat no encontrado'}, status=404)

@csrf_exempt
def enviar_solicitud_chat(request):
    """Funcion de utilidad para enviar solicitudes de chat entre usuarios"""
    if request.method == 'POST' and request.session.get('usuario_id'):
        try:
            data = json.loads(request.body)
            de_id = request.session['usuario_id']
            para_id = int(data.get('para_usuario_id'))

            if de_id == para_id:
                return JsonResponse({'ok': False, 'error': 'No puedes enviarte solicitud a ti mismo'})

            # Verifica si ya existe
            ya_existe = SolicitudChat.objects.using('conectati').filter(
                de_usuario_id=de_id, para_usuario_id=para_id
            ).exists()

            if ya_existe:
                return JsonResponse({'ok': False, 'error': 'Ya existe solicitud'})

            SolicitudChat.objects.using('conectati').create(
                de_usuario_id=de_id,
                para_usuario_id=para_id,
                estado='pendiente'
            )
            crear_notificacion(
                usuario_destino=Usuario.objects.using('conectati').get(id=para_id),
                tipo='chat',
                contenido=_(" te envió una solicitud de chat"),
                emisor=Usuario.objects.using('conectati').get(id=de_id)
            )
            return JsonResponse({'ok': True})
        except Exception as e:
            print("❌ Error solicitud chat:", e)
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

@csrf_exempt
def aceptar_solicitud_chat(request):
    """Funcion de utilidad para aceptar solicitudes de chat entre usuarios"""
    if request.method == 'POST' and request.session.get('usuario_id'):
        try:
            data = json.loads(request.body)
            solicitud_id = int(data.get('solicitud_id'))

            solicitud = SolicitudChat.objects.using('conectati').select_related('de_usuario', 'para_usuario').get(id=solicitud_id)

            if solicitud.para_usuario.id != request.session['usuario_id']:
                return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=403)

            solicitud.estado = 'aceptada'
            solicitud.fecha_aceptada = timezone.now()
            solicitud.save(using='conectati')

            # Crear chat solo si aún no existe entre los dos usuarios
            ya_existe_chat = Chat.objects.using('conectati').filter(
                Q(usuario1=solicitud.de_usuario, usuario2=solicitud.para_usuario) |
                Q(usuario1=solicitud.para_usuario, usuario2=solicitud.de_usuario)
            ).exists()

            if not ya_existe_chat:
                nuevo_chat = Chat.objects.using('conectati').create(
                    usuario1=solicitud.de_usuario,
                    usuario2=solicitud.para_usuario,
                    fecha_inicio=timezone.now()
                )
            else:
                nuevo_chat = Chat.objects.using('conectati').get(
                    Q(usuario1=solicitud.de_usuario, usuario2=solicitud.para_usuario) |
                    Q(usuario1=solicitud.para_usuario, usuario2=solicitud.de_usuario)
                )

            return JsonResponse({
                'ok': True,
                'chat': {
                    'id': nuevo_chat.id,
                    'username': solicitud.de_usuario.username,
                    'nombre': solicitud.de_usuario.nombre,
                    'foto': solicitud.de_usuario.foto or '/static/images/default_user.avif'
                }
            })
        except Exception as e:
            print("Error al aceptar solicitud de chat:", e)
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

@csrf_exempt
def rechazar_solicitud_chat(request):
    """Funcion de utilidad para rechazar solicitudes de chat entre usuarios"""
    if request.method == 'POST' and request.session.get('usuario_id'):
        try:
            data = json.loads(request.body)
            solicitud_id = data.get('solicitud_id')
            usuario_id = request.session['usuario_id']
            solicitud = SolicitudChat.objects.using('conectati').get(id=solicitud_id, para_usuario_id=usuario_id, estado='pendiente')
            solicitud.estado = 'rechazada'
            solicitud.save(using='conectati')
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)
    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)


@csrf_exempt
def enviar_solicitud_amistad(request):
    """Funcion de utilidad para enviar solicitudes de amistad entre usuarios"""
    # Verificar que sea una petición POST y que el usuario esté autenticado
    if request.method == 'POST' and request.session.get('usuario_id'):
        try:
            # Parsear los datos JSON enviados en el cuerpo de la petición
            data = json.loads(request.body)
            de_id = request.session['usuario_id']  # ID del usuario que envía la solicitud
            para_id = int(data.get('para_usuario_id'))  # ID del usuario que recibirá la solicitud

            # Verificar si ya existe una solicitud de amistad entre estos usuarios
            ya_existe = Amistad.objects.using('conectati').filter(
                de_usuario_id=de_id,
                para_usuario_id=para_id
            ).exists()

            if not ya_existe:
                # Si no existe, crear nueva solicitud de amistad con estado 'pendiente'
                Amistad.objects.using('conectati').create(
                    de_usuario_id=de_id,
                    para_usuario_id=para_id,
                    estado='pendiente'
                )
                crear_notificacion(
                    usuario_destino=Usuario.objects.using('conectati').get(id=para_id),
                    tipo='amistad',
                    contenido=_(" te envió una solicitud de amistad"),
                    emisor=Usuario.objects.using('conectati').get(id=de_id)
                )
                return JsonResponse({'ok': True})
            else:
                # Si ya existe, informar que no se puede crear duplicada
                return JsonResponse({'ok': False, 'error': 'Ya existe'})
        except Exception as e:
            # Manejar errores durante el proceso de creación
            print("❌ Error:", e)
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    # Si no es POST o no está autenticado, retornar error de método no permitido
    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

@csrf_exempt
def aceptar_solicitud(request):
    """Funcion de utilidad para aceptar una solicitud de amistad"""
    # Verificar que sea una petición POST y que el usuario esté autenticado
    if request.method == 'POST' and request.session.get('usuario_id'):
        try:
            # Parsear los datos JSON para obtener el ID de la solicitud
            data = json.loads(request.body)
            solicitud_id = data.get('solicitud_id')
            usuario_id = request.session['usuario_id']

            # Buscar la solicitud de amistad específica dirigida al usuario actual
            amistad = Amistad.objects.using('conectati').get(id=solicitud_id, para_usuario_id=usuario_id)
            
            # Cambiar el estado de la solicitud a 'aceptada' y actualizar la fecha
            amistad.estado = 'aceptada'
            amistad.fecha = timezone.now() 
            amistad.save(using='conectati')

            # Obtener datos del nuevo amigo para enviarlos de vuelta al frontend
            amigo = amistad.de_usuario
            amigo_data = {
                'id': amigo.id,
                'nombre': amigo.nombre,
                'username': amigo.username,
                'descripcion': amigo.descripcion or '',
                'foto': amigo.foto or '/static/images/default_user.avif',
                'amistad_id': amistad.id
            }

            # Retornar confirmación exitosa junto con los datos del amigo
            return JsonResponse({'ok': True, 'amigo': amigo_data})
        except Exception as e:
            # Manejar errores durante el proceso de aceptación
            print("❌ Error aceptando:", e)
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)
    
    # Si no es POST o no está autenticado, retornar error
    return JsonResponse({'ok': False}, status=405)

@csrf_exempt
def rechazar_solicitud(request):
    """Funcion de utilidad para rechazar una solicitud de amistad"""
    # Verificar que sea una petición POST y que el usuario esté autenticado
    if request.method == 'POST' and request.session.get('usuario_id'):
        try:
            # Parsear los datos JSON para obtener el ID de la solicitud
            data = json.loads(request.body)
            solicitud_id = data.get('solicitud_id')
            usuario_id = request.session['usuario_id']

            # Buscar la solicitud de amistad específica dirigida al usuario actual
            amistad = Amistad.objects.using('conectati').get(id=solicitud_id, para_usuario_id=usuario_id)
            
            # Eliminar completamente la solicitud de amistad de la base de datos
            amistad.delete(using='conectati')

            # Retornar confirmación exitosa
            return JsonResponse({'ok': True})
        except Exception as e:
            # Manejar errores durante el proceso de rechazo
            print("Error rechazando:", e)
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)
    
    # Si no es POST o no está autenticado, retornar error
    return JsonResponse({'ok': False}, status=405)

def eliminar_amistad(request):
    """Función de utilidad para eliminar una amistad entre usuarios"""

    if request.method == 'POST' and request.session.get('usuario_id'):
        try:
            data = json.loads(request.body)
            amistad_id = data.get('amistad_id')
            usuario_id = request.session['usuario_id']

            # Buscar la amistad donde el usuario sea uno de los involucrados (más general)
            amistad = Amistad.objects.using('conectati').get(id=amistad_id)

            if amistad.de_usuario_id != usuario_id and amistad.para_usuario_id != usuario_id:
                return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=403)

            # Eliminar la amistad
            amistad.delete(using='conectati')
            return JsonResponse({'ok': True})

        except Amistad.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Amistad no encontrada'}, status=404)

        except Exception as e:
            print("Error eliminando amistad:", e)
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

@csrf_exempt
def eliminar_chat(request):
    """Función de utilidad para eliminar un chat entre usuarios"""
    if request.method == 'POST' and request.session.get('usuario_id'):
        try:
            data = json.loads(request.body)
            chat_id = data.get('chat_id')
            usuario_id = request.session['usuario_id']

            if not chat_id:
                return JsonResponse({'ok': False, 'error': 'chat_id vacío'}, status=400)

            # Buscar el chat
            chat = Chat.objects.using('conectati').get(id=chat_id)

            # Verificar si el usuario está involucrado
            if chat.usuario1_id != usuario_id and chat.usuario2_id != usuario_id:
                return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=403)

            # Eliminar la solicitud de chat en ambas direcciones
            SolicitudChat.objects.using('conectati').filter(
                Q(de_usuario_id=chat.usuario1_id, para_usuario_id=chat.usuario2_id) |
                Q(de_usuario_id=chat.usuario2_id, para_usuario_id=chat.usuario1_id)
            ).delete()

            chat.delete(using='conectati')

            return JsonResponse({'ok': True})

        except Chat.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Chat no encontrado'}, status=404)

        except Exception as e:
            print("❌ Error eliminando chat:", e)
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

def obtener_hilo_completo(comentario):
    """Función de utilidad para obtener el hilo completo de una publicación o comentario"""
    hilo = []
    actual = comentario

    while actual.respuesta_a is not None:
        hilo.insert(0, actual.respuesta_a)
        actual = actual.respuesta_a

    return hilo
