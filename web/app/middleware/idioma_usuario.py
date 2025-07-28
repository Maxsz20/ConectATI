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
            print(f"Middleware - usuario_id detectado: {usuario_id}")
            try:
                configuracion = Configuracion.objects.using('conectati').get(usuario_id=usuario_id)
                if configuracion.idioma in ['es', 'en']:
                    idioma = configuracion.idioma
                    print(f"Idioma aplicado desde configuración: {idioma}")
            except Configuracion.DoesNotExist:
                print("Middleware - Configuración no encontrada para el usuario.")
            except Exception as e:
                print(f"Middleware - Error inesperado: {e}")
        else:
            print("Middleware - No hay usuario en la sesión.")

        translation.activate(idioma)
        request.LANGUAGE_CODE = idioma
        return self.get_response(request)
