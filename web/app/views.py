from django.shortcuts import render, redirect
from .forms import RegistroForm, PublicacionForm, EditarPerfilForm
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.utils import timezone
from .models import Usuario, Publicacion, Estrella, Amistad, SolicitudChat, Chat, Mensaje, Comentario, Notificacion, CodigoRecuperacion, Configuracion
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
import os
import json
from django.conf import settings
from django.db.models import Q, Count
from django.http import JsonResponse
from datetime import timedelta
from django.views.decorators.http import require_POST
from django.utils import translation
from django.urls import reverse

from .utils import (crear_notificacion, procesar_publicacion, eliminar_foto_perfil, subir_foto_perfil, marcar_notificaciones_leidas, 
obtener_mensajes_chat, crear_comentario, dar_estrella, buscar_usuarios, obtener_conversacion,
enviar_solicitud_chat, aceptar_solicitud_chat, rechazar_solicitud_chat, enviar_solicitud_amistad, aceptar_solicitud, 
rechazar_solicitud, eliminar_amistad, eliminar_chat, obtener_hilo_completo, marcar_notificacion_individual, enviar_mensaje_chat)

# Create your views here.
def InicioRedirectView(request):
    if request.session.get('usuario_id'):
        return redirect('feed')
    else:
        return redirect('login')

def FriendView(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']

    # Amistades aceptadas (el usuario puede ser en cualquiera de los dos lados)
    amistades = Amistad.objects.using('conectati').filter(
        Q(de_usuario_id=usuario_id) | Q(para_usuario_id=usuario_id),
        estado='aceptada'
    ).select_related('de_usuario', 'para_usuario')

    amigos = []
    for a in amistades:
        if a.de_usuario_id == usuario_id:
            amigo = a.para_usuario
        else:
            amigo = a.de_usuario
        amigos.append({
            'id': amigo.id,
            'nombre': amigo.nombre,
            'username': amigo.username,
            'descripcion': amigo.descripcion or '',
            'foto': amigo.foto or '/static/images/default_user.avif',
            'amistad_id': a.id
        })

    # Solicitudes pendientes recibidas (donde yo soy el receptor)
    solicitudes = Amistad.objects.using('conectati').filter(
        para_usuario_id=usuario_id,
        estado='pendiente'
    ).select_related('de_usuario')

    return render(request, 'app/amistades.html', {
        'amigos': amigos,
        'solicitudes': solicitudes,
    })

def LoginView(request):

    if request.session.get('usuario_id'):
        return redirect('feed')  # Ya está logueado, no mostrar login otra vez

    if request.method == "POST":
        email_o_usuario = request.POST.get("correo_usuario")
        password = request.POST.get("password")

        try:
            usuario = Usuario.objects.using('conectati').filter(
                models.Q(email=email_o_usuario) |
                models.Q(username=email_o_usuario)
            ).first()

            if check_password(password, usuario.contrasena):
                request.session['usuario_id'] = usuario.id
                return redirect('feed')
            else:
                messages.error(request, "Credenciales incorrectas.")
        except Usuario.DoesNotExist:
            messages.error(request, "Credenciales incorrectas.")

    return render(request, 'app/iniciar_sesion.html', {})


def RegisterView(request):

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if Usuario.objects.using('conectati').filter(email=data['email']).exists():
                form.add_error('email', 'Este correo ya está registrado.')
            elif Usuario.objects.using('conectati').filter(ci=data['ci']).exists():
                form.add_error('ci', 'Esta cédula ya está registrada.')
            elif Usuario.objects.using('conectati').filter(username=data['username']).exists():
                form.add_error('username', 'Este nombre de usuario ya está registrado.')
            else:
                nuevo_usuario = Usuario(
                    nombre=data['nombre'],
                    username=data['username'],
                    email=data['email'],
                    ci=data['ci'],
                    contrasena=make_password(data['contrasena'])
                )
                nuevo_usuario.save(using='conectati')
                # Crear configuración por defecto
                Configuracion.objects.using('conectati').create(
                    usuario=nuevo_usuario,
                    tema="claro",
                    idioma="es",
                    publicaciones_privadas=False,
                    notificar_chat=True,
                    notificar_comentario=True,
                    notificar_amistad=True
                )

                return redirect('login')
    else:
        form = RegistroForm()

    return render(request, 'app/registrarse.html', {'form': form})

def LogoutView(request):
    # Limpiar sesión o hacer logout
    request.session.flush()  # o logout(request) si usas django.contrib.auth

    # Limpiar mensajes pendientes
    list(messages.get_messages(request))

    return redirect('login')

def ForgottenPassView(request):
    return render(request, 'app/forgotten_password.html', {})

def CheckCodeView(request):
    return render(request, 'app/check_code.html', {})

def ChangePassView(request):
    return render(request, 'app/change_password.html', {})

def ProfileView(request, usuario_id=None):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_actual_id = request.session['usuario_id']
    if usuario_id is None:
        usuario_id = usuario_actual_id  # Ver tu propio perfil

    try:
        usuario_perfil = Usuario.objects.using('conectati').get(id=usuario_id)

        estrellas_usuario = Estrella.objects.using('conectati') \
            .filter(usuario_id=usuario_actual_id) \
            .values_list('publicacion_id', flat=True)

        # Verificar si hay amistad (si es otro perfil)
        amistad = None
        if usuario_actual_id != usuario_id:
            amistad = Amistad.objects.using('conectati').filter(
                Q(de_usuario_id=usuario_actual_id, para_usuario_id=usuario_id) |
                Q(de_usuario_id=usuario_id, para_usuario_id=usuario_actual_id)
            ).first()

        estado_amistad = amistad.estado if amistad else None

        # Verificar si hay solicitud de chat
        solicitud_chat = SolicitudChat.objects.using('conectati').filter(
            Q(de_usuario_id=usuario_actual_id, para_usuario_id=usuario_id) |
            Q(de_usuario_id=usuario_id, para_usuario_id=usuario_actual_id)
        ).first()
        estado_chat = solicitud_chat.estado if solicitud_chat else None

        cantidad_amigos = Amistad.objects.using('conectati').filter(
            Q(de_usuario_id=usuario_id) | Q(para_usuario_id=usuario_id),
            estado='aceptada'
        ).count()

        # Publicaciones: todas si es tu perfil o amigos, públicas si no
        if usuario_actual_id == usuario_id or estado_amistad == 'aceptada':
            publicaciones = Publicacion.objects.using('conectati') \
                .filter(usuario=usuario_perfil)
        else:
            publicaciones = Publicacion.objects.using('conectati') \
                .filter(usuario=usuario_perfil, privacidad='publica')

        publicaciones = publicaciones.annotate(num_comentarios=Count('comentario')).order_by('-fecha')

        return render(request, 'app/perfil.html', {
            'usuario_perfil': usuario_perfil,
            'publicaciones': publicaciones,
            'cantidad_amigos': cantidad_amigos,
            'estado_amistad': estado_amistad,
            'estado_chat': estado_chat,
            'es_propio_perfil': usuario_actual_id == usuario_id,
            'no_area_info': True,
            'estrellas_usuario': list(estrellas_usuario)
        })

    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('feed')



def EditProfileView(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario = Usuario.objects.using('conectati').get(id=request.session['usuario_id'])

    # Si es una solicitud AJAX con archivo
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.FILES.get('foto_archivo'):
        archivo = request.FILES['foto_archivo']
        nombre_archivo = f"{timezone.now().strftime('%Y%m%d%H%M%S')}_{archivo.name}"
        ruta_guardado = os.path.join(settings.MEDIA_ROOT, 'fotos_perfil', nombre_archivo)

        os.makedirs(os.path.dirname(ruta_guardado), exist_ok=True)
        with open(ruta_guardado, 'wb+') as destino:
            for chunk in archivo.chunks():
                destino.write(chunk)

        # Guardamos solo el path relativo como texto
        usuario.foto = f"/media/fotos_perfil/{nombre_archivo}"
        usuario.save(using='conectati')

        return JsonResponse({
            "ok": True,
            "foto_url": usuario.foto
        })

    # Si es envío normal (POST)
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save(using='conectati')
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('profile')
    else:
        form = EditarPerfilForm(instance=usuario)

    return render(request, 'app/editar_perfil.html', {
        'form': form,
        'usuario_logueado': usuario,
        'no_area_info': True
    })

def FeedView(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    form = PublicacionForm()
    usuario_id = request.session['usuario_id']

    # Obtener IDs de amigos con amistad aceptada
    amistades = Amistad.objects.using('conectati').filter(
        Q(de_usuario_id=usuario_id) | Q(para_usuario_id=usuario_id),
        estado='aceptada'
    )

    amigos_ids = set()
    for amistad in amistades:
        if amistad.de_usuario_id == usuario_id:
            amigos_ids.add(amistad.para_usuario_id)
        else:
            amigos_ids.add(amistad.de_usuario_id)

    # Publicaciones públicas o privadas de amigos
    publicaciones = Publicacion.objects.using('conectati') \
        .filter(
            Q(privacidad='publica') |
            Q(privacidad='privada', usuario_id__in=amigos_ids) |
            Q(usuario_id=usuario_id)
        ) \
        .annotate(num_comentarios=Count('comentario', filter=Q(comentario__respuesta_a__isnull=True))) \
        .order_by('-fecha')

    # Estrellas del usuario
    estrellas_usuario = Estrella.objects.using('conectati') \
        .filter(usuario_id=usuario_id) \
        .values_list('publicacion_id', flat=True)
    
    configuracion = Configuracion.objects.using('conectati').get(usuario_id=usuario_id)

    # Manejo de publicación nueva
    if request.method == "POST":
        form = PublicacionForm(request.POST, request.FILES)
        nueva = procesar_publicacion(request, form)
        if nueva:
            return redirect('feed')

    return render(request, 'app/feed.html', {
        'form': form,
        'publicaciones': publicaciones,
        'estrellas_usuario': list(estrellas_usuario),
        'configuracion': configuracion
    })

def NotifyView(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']

    ahora = timezone.localtime()
    hoy = ahora.date()
    ayer = hoy - timedelta(days=1)
    semana_pasada = hoy - timedelta(days=7)

    notificaciones = Notificacion.objects.using('conectati') \
        .filter(usuario_id=usuario_id) \
        .select_related('emisor') \
        .order_by('-fecha')

    grupo_hoy = []
    grupo_ayer = []
    grupo_semana = []

    for n in notificaciones:
        # Asignar la URL según el tipo de notificación
        if n.tipo == 'comentario' and n.publicacion_id:
            n.url_destino = reverse('post', args=[n.publicacion_id])
        elif n.tipo == 'respuesta' and n.comentario_id:
            n.url_destino = reverse('comentario_hilo', args=[n.comentario_id])
        elif n.tipo == 'chat':
            n.url_destino = reverse('chat')
        elif n.tipo == 'amistad':
            n.url_destino = reverse('friends')
        elif n.tipo == 'estrella' and n.publicacion_id:
            n.url_destino = reverse('post', args=[n.publicacion_id])
        else:
            n.url_destino = None  # O "#" si prefieres

        # Agrupación por fecha
        fecha_notif = timezone.localtime(n.fecha).date()
        if fecha_notif == hoy:
            grupo_hoy.append(n)
        elif fecha_notif == ayer:
            grupo_ayer.append(n)
        elif fecha_notif >= semana_pasada:
            grupo_semana.append(n)

    return render(request, 'app/notificaciones.html', {
        'grupo_hoy': grupo_hoy,
        'grupo_ayer': grupo_ayer,
        'grupo_semana': grupo_semana,
    })


def ChatView(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']

    # Obtener todos los chats donde participa el usuario
    chats_qs = Chat.objects.using('conectati').filter(
        Q(usuario1_id=usuario_id) | Q(usuario2_id=usuario_id)
    ).select_related('usuario1', 'usuario2').order_by('-fecha_inicio')

    chats_data = []
    for chat in chats_qs:
        otro_usuario = chat.usuario2 if chat.usuario1.id == usuario_id else chat.usuario1
        chats_data.append({
            'id': chat.id,
            'username': otro_usuario.username,
            'nombre': otro_usuario.nombre,
            'foto': otro_usuario.foto or '/static/images/default_user.avif',
            'usuario_id': otro_usuario.id,
        })

    # Obtener mensajes del primer chat si existe
    primer_chat = chats_qs.first()
    mensajes = []
    if primer_chat:
        mensajes = Mensaje.objects.using('conectati') \
            .filter(chat=primer_chat) \
            .order_by('fecha')

    solicitudes_chat_pendientes = SolicitudChat.objects.using('conectati') \
        .filter(para_usuario_id=usuario_id, estado='pendiente') \
        .select_related('de_usuario') \
        .order_by('-fecha')

    return render(request, 'app/chat.html', {
        'chats': chats_data,
        'primer_chat': chats_data[0] if chats_data else None,
        'mensajes': mensajes,
        'solicitudes_chat_pendientes': solicitudes_chat_pendientes,
    })

def SettingsView(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']
    configuracion = None
    try:
        configuracion = Configuracion.objects.using('conectati').get(usuario_id=usuario_id)
    except Configuracion.DoesNotExist:
        pass

    return render(request, 'app/configuracion.html', {
        'configuracion': configuracion
    })

def PostView(request, publicacion_id):
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    try:
        publicacion = Publicacion.objects.using('conectati').select_related('usuario').get(id=publicacion_id)
        comentarios = Comentario.objects.using('conectati').filter(publicacion=publicacion, respuesta_a__isnull=True).select_related('usuario').order_by('fecha')

        usuario_id = request.session['usuario_id']
        estrellas_usuario = Estrella.objects.using('conectati') \
            .filter(usuario_id=usuario_id) \
            .values_list('publicacion_id', flat=True)

        es_propia = usuario_id == publicacion.usuario.id

        estado_amistad = None
        if not es_propia:
            amistad = Amistad.objects.using('conectati').filter(
                Q(de_usuario_id=usuario_id, para_usuario_id=publicacion.usuario.id) |
                Q(de_usuario_id=publicacion.usuario.id, para_usuario_id=usuario_id)
            ).first()

            if amistad:
                estado_amistad = amistad.estado

        for comentario in comentarios:
            comentario.num_comentarios = Comentario.objects.filter(respuesta_a=comentario).count()

        return render(request, 'app/publicacion.html', {
            'publicacion': publicacion,
            'comentarios': comentarios,
            'num_comentarios': comentarios.count(),
            'estrellas_usuario': list(estrellas_usuario),
            'es_propia': es_propia,
            'estado_amistad': estado_amistad,
        })

    except Publicacion.DoesNotExist:
        messages.error(request, 'Publicación no encontrada.')
        return redirect('feed')

def CommentThreadView(request, comentario_id):
    comentario = Comentario.objects.select_related('publicacion', 'usuario', 'respuesta_a').get(id=comentario_id)
    respuestas = Comentario.objects.filter(respuesta_a=comentario).order_by('fecha')
    usuario = Usuario.objects.using('conectati').get(id=request.session['usuario_id'])

    estrellas_usuario = Estrella.objects.using('conectati') \
            .filter(usuario_id=usuario) \
            .values_list('publicacion_id', flat=True)

    # Número total de comentarios directos a la publicación original
    num_comentarios = Comentario.objects.filter(publicacion=comentario.publicacion, respuesta_a__isnull=True).count()

    # Obtener cantidad de respuestas del comentario actual
    comentario.num_comentarios = Comentario.objects.filter(respuesta_a=comentario).count()

    # Hilo de padres (desde el más antiguo hasta el comentario padre directo)
    hilo = obtener_hilo_completo(comentario)  # devuelve lista [padre, abuelo, ...]

    # Anotar a cada comentario del hilo su número de respuestas
    for c in hilo:
        c.num_comentarios = Comentario.objects.filter(respuesta_a=c).count()

    # Anotar a cada comentario nuevo su número de respuestas
    for r in respuestas:
        r.num_comentarios = Comentario.objects.filter(respuesta_a=r).count()
    
    return render(request, 'app/hilo_comentario.html', {
        'comentario': comentario,
        'respuestas': respuestas,
        'num_comentarios': num_comentarios,
        'hilo': hilo,
        'publicacion': comentario.publicacion,
        'usuario_logueado': usuario,
        'estrellas_usuario': list(estrellas_usuario),
    })

    
def PostMobileView(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    form = PublicacionForm()

    if request.method == "POST":
        form = PublicacionForm(request.POST, request.FILES)
        nueva = procesar_publicacion(request, form)
        if nueva:
            return redirect('feed')

    configuracion = Configuracion.objects.using('conectati').get(usuario_id=request.session['usuario_id'])        

    return render(request, 'app/publicar_mobile.html', {
        'form': form,
        'no_area_info': True,
        'configuracion': configuracion
    })

def ReplyMobileView(request, publicacion_id):
    if not request.session.get('usuario_id'):
        return redirect('login')
    try:
        publicacion = Publicacion.objects.using('conectati').select_related('usuario').get(id=publicacion_id)
        autor = publicacion.usuario
        usuario_logueado = Usuario.objects.using('conectati').get(id=request.session['usuario_id'])
    except Publicacion.DoesNotExist:
        messages.error(request, 'Publicación no encontrada.')
        return redirect('feed')

    error = None
    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        if texto:
            Comentario.objects.using('conectati').create(
                publicacion=publicacion,
                usuario=usuario_logueado,
                texto=texto,
                fecha=timezone.now()
            )
            return redirect('publicacion', publicacion_id=publicacion.id)
        else:
            error = 'El comentario no puede estar vacío.'
    return render(request, 'app/responder_mobile.html', {
        'publicacion': publicacion,
        'autor': autor,
        'usuario_logueado': usuario_logueado,
        'error': error,
        'no_area_info': True
    })

def ReplyToCommentMobileView(request, comentario_id):
    if not request.session.get('usuario_id'):
        return redirect('login')
    try:
        comentario = Comentario.objects.using('conectati') \
            .select_related('usuario', 'publicacion') \
            .get(id=comentario_id)

        publicacion = comentario.publicacion
        autor = comentario.usuario
        usuario_logueado = Usuario.objects.using('conectati').get(id=request.session['usuario_id'])

    except Comentario.DoesNotExist:
        messages.error(request, 'Comentario no encontrado.')
        return redirect('feed')

    error = None
    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        if texto:
            Comentario.objects.using('conectati').create(
                publicacion=publicacion,
                usuario=usuario_logueado,
                texto=texto,
                fecha=timezone.now(),
                respuesta_a=comentario
            )
            return redirect('comentario_hilo', comentario.id)
        else:
            error = 'El comentario no puede estar vacío.'
    
    return render(request, 'app/responder_mobile.html', {
        'publicacion': publicacion,
        'autor': autor,
        'comentario': comentario,
        'usuario_logueado': usuario_logueado,
        'error': error,
        'no_area_info': True
    })


def SearchMobileView(request):
    return render(request, 'app/busqueda_mobile.html', {'no_area_info': True})


@csrf_exempt
def enviar_codigo(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            correo = data.get('email')

            # Verificación básica del correo
            if not correo:
                return JsonResponse({'ok': False, 'error': 'Correo vacío'}, status=400)

            try:
                usuario = Usuario.objects.using('conectati').get(email=correo)
            except Usuario.DoesNotExist:
                return JsonResponse({'ok': False, 'error': 'Correo no registrado'}, status=404)

            # Generar código aleatorio
            codigo = get_random_string(length=6, allowed_chars='0123456789')

            # Guardar en la BD (eliminando códigos previos)
            CodigoRecuperacion.objects.using('conectati').filter(usuario=usuario).delete()
            CodigoRecuperacion.objects.using('conectati').create(usuario=usuario, codigo=codigo)

            # Enviar correo
            mensaje = f'Tu código de recuperación es: {codigo}'
            
            try:
                email = EmailMessage(
                    subject='Código de recuperación - ConectATI',
                    body=mensaje,
                    from_email='noreply@conectati.com',
                    to=[correo]
                )
                email.content_subtype = "plain"
                email.send()
            except Exception as email_error:
                print(f"Error enviando correo: {email_error}")
                pass

            return JsonResponse({'ok': True})

        except Exception as e:
            print("Error en enviar_codigo:", e)
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

@csrf_exempt
def verificar_codigo(request):
    if request.method == 'GET':
        # Mostrar la página de verificación de código
        return render(request, 'app/check_code.html', {})
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            codigo = data.get('codigo')

            recuperacion = CodigoRecuperacion.objects.using('conectati').get(codigo=codigo)
            if recuperacion.expirado():
                recuperacion.delete()
                return JsonResponse({'ok': False, 'error': 'Código expirado'}, status=410)

            # Guardar ID temporal en sesión para el siguiente paso
            request.session['recuperacion_usuario_id'] = recuperacion.usuario.id
            recuperacion.delete()
            return JsonResponse({'ok': True})

        except CodigoRecuperacion.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Código inválido'}, status=404)
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)


@csrf_exempt
def cambiar_password(request):
    if request.method == 'GET':
        # Mostrar la página de cambio de contraseña
        return render(request, 'app/change_password.html', {})
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            nueva = data.get('nueva')

            usuario_id = request.session.get('recuperacion_usuario_id')
            if not usuario_id:
                return JsonResponse({'ok': False, 'error': 'Sesión expirada'}, status=403)

            usuario = Usuario.objects.using('conectati').get(id=usuario_id)
            usuario.contrasena = make_password(nueva)  # Hashear la nueva contraseña
            usuario.save(using='conectati')
            del request.session['recuperacion_usuario_id']
            return JsonResponse({'ok': True})
            
        except Usuario.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Usuario no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)


@require_POST
def guardar_idioma(request):
    idioma = request.POST.get("idioma", "es")

    # Activar inmediatamente el idioma en la sesión del usuario
    request.session[settings.LANGUAGE_COOKIE_NAME] = idioma
    translation.activate(idioma)

    # Guardar en la configuración del usuario
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        try:
            configuracion = Configuracion.objects.using('conectati').get(usuario_id=usuario_id)
            configuracion.idioma = idioma
            configuracion.save(using='conectati')
        except Configuracion.DoesNotExist:
            pass 

    return redirect(request.META.get("HTTP_REFERER", "/"))

@require_POST
def guardar_privacidad(request):
    valor = request.POST.get("privacidad", "").strip().lower()
    es_privado = valor == "privado"

    usuario_id = request.session.get("usuario_id")
    if usuario_id:
        try:
            configuracion = Configuracion.objects.using("conectati").get(usuario_id=usuario_id)
            configuracion.publicaciones_privadas = es_privado
            configuracion.save(using="conectati")
        except Configuracion.DoesNotExist:
            pass

    return redirect(request.META.get("HTTP_REFERER", "/"))

@require_POST
def guardar_tema(request):
    tema = request.POST.get("tema", "").strip().lower()
    if tema not in ["claro", "oscuro"]:
        return redirect(request.META.get("HTTP_REFERER", "/"))

    usuario_id = request.session.get("usuario_id")
    if usuario_id:
        try:
            configuracion = Configuracion.objects.using("conectati").get(usuario_id=usuario_id)
            configuracion.tema = tema
            configuracion.save(using="conectati")
        except Configuracion.DoesNotExist:
            pass

    return redirect(request.META.get("HTTP_REFERER", "/"))


