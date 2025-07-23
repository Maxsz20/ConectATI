from django.shortcuts import render, redirect
from .forms import RegistroForm, PublicacionForm
from django.utils import timezone
from .models import Usuario, Publicacion
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db import models

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
    return render(request, 'app/perfil.html', {'no_area_info': True})

def EditProfileView(request):
    return render(request, 'app/editarPerfil.html', {'no_area_info': True})

def FeedView(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    form = PublicacionForm()
    publicaciones = Publicacion.objects.using('conectati').filter(
        privacidad='publica'
    ).order_by('-fecha')

    if request.method == "POST":
        form = PublicacionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            if not data['texto'] and not data['archivo']:
                form.add_error(None, "Debes escribir algo o subir un archivo.")
            else:
                usuario = Usuario.objects.using('conectati').get(id=request.session['usuario_id'])
                nueva = Publicacion(
                    usuario=usuario,
                    texto=data['texto'],
                    archivo=data['archivo'],
                    privacidad=data['privacidad'].lower(),
                    fecha=timezone.now()
                )
                nueva.save(using='conectati')
                return redirect('feed')  # redirige para limpiar el POST

    return render(request, 'app/feed.html', {
        'form': form,
        'publicaciones': publicaciones
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
    return render(request, 'app/publicar_mobile.html', {'no_area_info': True})

def ReplyMobileView(request):
    return render(request, 'app/responder_mobile.html', {'no_area_info': True})

def SearchView(request):
    return render(request, 'app/busqueda.html', {})

def SearchMobileView(request):
    return render(request, 'app/busqueda_mobile.html', {'no_area_info': True})
