from django.shortcuts import render

# Create your views here.
def amistades(request):
    return render(request, 'app/amistades.html')

