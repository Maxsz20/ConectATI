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
