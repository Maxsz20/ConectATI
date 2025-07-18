from django.shortcuts import render

# Create your views here.
def FriendView(request):
    return render(request, 'app/amistades.html', {})

def LoginView(request):
    return render(request, 'app/iniciar_sesion.html', {})
