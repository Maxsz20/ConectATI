from django.shortcuts import render, redirect
from .forms import RegistroForm, PublicacionForm
from django.utils import timezone
from .models import Usuario, Publicacion, Estrella, Amistad
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
from django.http import JsonResponse

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
    )

    amigos = []
    for a in amistades:
        if a.de_usuario_id == usuario_id:
            amigo = a.para_usuario
        else:
            amigo = a.de_usuario
        amigos.append(amigo)

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
                return redirect('login')
    else:
        form = RegistroForm()

    return render(request, 'app/registrarse.html', {'form': form})

def LogoutView(request):
    request.session.flush()  # ← borra todos los datos de sesión
    return redirect('login')


def ForgottenPassView(request):
    return render(request, 'app/forgotten_password.html', {})

def CheckCodeView(request):
    return render(request, 'app/check_code.html', {})

def ChangePassView(request):
    return render(request, 'app/change_password.html', {})

def ProfileView(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    usuario_id = request.session['usuario_id']
    return ver_perfil_usuario(request, usuario_id)

# Vista para ver perfil de otros usuarios (y propio)
def ver_perfil_usuario(request, usuario_id):
    # Verificar que el usuario esté autenticado
    if not request.session.get('usuario_id'):
        return redirect('login')

    try:
        # Obtener el usuario cuyo perfil se quiere ver
        usuario_perfil = Usuario.objects.using('conectati').get(id=usuario_id)
        
        # Obtener el usuario actual para verificar relación de amistad
        usuario_actual_id = request.session['usuario_id']
        
        # Verificar si existe una relación de amistad
        amistad = Amistad.objects.using('conectati').filter(
            Q(de_usuario_id=usuario_actual_id, para_usuario_id=usuario_id) |
            Q(de_usuario_id=usuario_id, para_usuario_id=usuario_actual_id)
        ).first()
        
        estado_amistad = None
        if amistad:
            estado_amistad = amistad.estado
        
        # Contar amistades aceptadas del usuario del perfil
        cantidad_amigos = Amistad.objects.using('conectati').filter(
            Q(de_usuario_id=usuario_id) | Q(para_usuario_id=usuario_id),
            estado='aceptada'
        ).count()
        
        # Obtener publicaciones del usuario (solo públicas si no son amigos)
        if estado_amistad == 'aceptada' or usuario_actual_id == usuario_id:
            # Si son amigos o es el mismo usuario, mostrar todas las publicaciones
            publicaciones = Publicacion.objects.using('conectati').filter(usuario=usuario_perfil).order_by('-fecha')
        else:
            # Si no son amigos, solo mostrar publicaciones públicas
            publicaciones = Publicacion.objects.using('conectati').filter(
                usuario=usuario_perfil, 
                privacidad='publica'
            ).order_by('-fecha')
        
        return render(request, 'app/perfil.html', {
            'usuario_perfil': usuario_perfil,
            'publicaciones': publicaciones,
            'cantidad_amigos': cantidad_amigos,
            'estado_amistad': estado_amistad,
            'es_propio_perfil': usuario_actual_id == usuario_id,
            'no_area_info': True
        })
        
    except Usuario.DoesNotExist:
        # Si el usuario no existe, redirigir al feed con un mensaje de error
        messages.error(request, 'Usuario no encontrado.')
        return redirect('feed')

def EditProfileView(request):
    return render(request, 'app/editarPerfil.html', {'no_area_info': True})

def FeedView(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    form = PublicacionForm()
    publicaciones = Publicacion.objects.using('conectati').filter(privacidad='publica').order_by('-fecha')

    estrellas_usuario = []
    if request.session.get('usuario_id'):
        user_id = request.session['usuario_id']
        estrellas_usuario = Estrella.objects.using('conectati') \
            .filter(usuario_id=user_id) \
            .values_list('publicacion_id', flat=True)

    if request.method == "POST":
        form = PublicacionForm(request.POST, request.FILES)
        nueva = procesar_publicacion(request, form)
        if nueva:
            return redirect('feed')

    return render(request, 'app/feed.html', {
        'form': form,
        'publicaciones': publicaciones,
        'estrellas_usuario': list(estrellas_usuario)
    })


def NotifyView(request):
    return render(request, 'app/notificaciones.html', {})

def ChatView(request):
    return render(request, 'app/chat.html', {})

def SettingsView(request):
    return render(request, 'app/configuracion.html', {})

def PostView(request):
    return render(request, 'app/publicacion.html', {})
    
def PostMobileView(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    form = PublicacionForm()

    if request.method == "POST":
        form = PublicacionForm(request.POST, request.FILES)
        nueva = procesar_publicacion(request, form)
        if nueva:
            return redirect('feed')

    return render(request, 'app/publicar_mobile.html', {
        'form': form,
        'no_area_info': True,
    })

def ReplyMobileView(request):
    return render(request, 'app/responder_mobile.html', {'no_area_info': True})

def SearchView(request):
    return render(request, 'app/busqueda.html', {})

def SearchMobileView(request):
    return render(request, 'app/busqueda_mobile.html', {'no_area_info': True})

# Función para procesar publicaciones
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


# Lógica para dar estrellas a una publicación
def dar_estrella(request, publicacion_id):
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

        # Guardar registro
        nueva = Estrella(usuario_id=user_id, publicacion_id=publicacion_id)
        nueva.save(using='conectati')

        return JsonResponse({'ok': True, 'nuevas_estrellas': publicacion.estrellas})
    except Publicacion.DoesNotExist:
        return JsonResponse({'error': 'No encontrada'}, status=404)


# Logica para buscar usuarios
def buscar_usuarios(request):
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
                'estado_amistad': estado_amistad  # ← esto sí lo necesita el JS
            })

        # Retornar los usuarios encontrados en formato JSON
        return JsonResponse({'usuarios': usuarios_data})
    
    except Exception as e:
        # Manejar cualquier error que pueda ocurrir durante la búsqueda
        print("ERROR en buscar_usuarios:", e)
        return JsonResponse({'error': 'Error interno en la búsqueda'}, status=500)


# Logica para enviar solicitud de amistad
@csrf_exempt
def enviar_solicitud_amistad(request):
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

# Logica para aceptar una solicitud de amistad
@csrf_exempt
def aceptar_solicitud(request):
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
                'foto': amigo.foto or '/static/images/default_user.avif'
            }

            # Retornar confirmación exitosa junto con los datos del amigo
            return JsonResponse({'ok': True, 'amigo': amigo_data})
        except Exception as e:
            # Manejar errores durante el proceso de aceptación
            print("❌ Error aceptando:", e)
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)
    
    # Si no es POST o no está autenticado, retornar error
    return JsonResponse({'ok': False}, status=405)

# Logica para rechazar una solicitud de amistad
@csrf_exempt
def rechazar_solicitud(request):
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