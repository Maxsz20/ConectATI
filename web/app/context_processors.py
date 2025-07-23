# web/app/context_processors.py

from .models import Usuario

def usuario_actual(request):
    usuario = None
    if request.session.get('usuario_id'):
        try:
            usuario = Usuario.objects.using('conectati').get(id=request.session['usuario_id'])
        except Usuario.DoesNotExist:
            pass
    return {'usuario_logueado': usuario}
