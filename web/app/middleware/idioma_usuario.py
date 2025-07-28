# app/middleware/idioma_usuario.py

from django.utils import translation
from app.models import Configuracion, Usuario

class IdiomaUsuarioMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        idioma = 'es'  # Idioma por defecto

        usuario_id = request.session.get('usuario_id')
        if usuario_id:
            try:
                configuracion = Configuracion.objects.using('conectati').get(usuario_id=usuario_id)
                if configuracion.idioma in ['es', 'en']:
                    idioma = configuracion.idioma
            except Configuracion.DoesNotExist:
                pass
            except Exception as e:
                pass
        else:
            pass

        translation.activate(idioma)
        request.LANGUAGE_CODE = idioma
        return self.get_response(request)
