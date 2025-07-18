from django.shortcuts import render

# Create your views here.
def FriendView(request):
    return render(request, 'app/amistades.html', {})

def LoginView(request):
    return render(request, 'app/iniciar_sesion.html', {})

def RegisterView(request):
    return render(request, 'app/registrarse.html', {})

def ForgottenPassView(request):
    return render(request, 'app/forgotten_password.html', {})

def PerfilView(request):
    return render(request, 'app/perfil.html', {
        'no_area_info': True
    })

def PerfilView(request):
    return render(request, 'app/perfil.html', {
        'no_area_info': True
    })

def ProfileView(request):
    return render(request, 'app/perfil.html', {})

def FeedView(request):
    return render(request, 'app/feed.html', {})

def NotifyView(request):
    return render(request, 'app/notificaciones.html', {})

def ChatView(request):
    return render(request, 'app/chat.html', {})

def SettingsView(request):
    return render(request, 'app/configuracion.html', {})

def PostView(request):
    return render(request, 'app/publicar.html', {})

def SearchView(request):
    return render(request, 'app/busqueda.html', {})