from django.shortcuts import render, redirect
from .forms import RegistroForm, PublicacionForm
from django.utils import timezone
from .models import Usuario, Publicacion, Estrella, Amistad
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.http import JsonResponse
import os
from django.conf import settings

# Create your views here.
def InicioRedirectView(request):
    if request.session.get('usuario_id'):
        return redirect('feed')
    else:
        return redirect('login')

def FriendView(request):
    return render(request, 'app/amistades.html', {})

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

    usuario = Usuario.objects.using('conectati').get(id=request.session['usuario_id'])

    publicaciones = Publicacion.objects.using('conectati').filter(usuario=usuario).order_by('-fecha')

    return render(request, 'app/perfil.html', {
        'usuario_logueado': usuario,
        'publicaciones': publicaciones,
        'no_area_info': True
    })


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