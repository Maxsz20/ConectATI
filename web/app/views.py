from django.shortcuts import render

# Create your views here.
def FriendView(request):
    return render(request, 'app/amistades.html', {})

