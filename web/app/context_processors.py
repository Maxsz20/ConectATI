# web/app/context_processors.py

from .models import Usuario, Chat, SolicitudChat
from django.db.models import Q

def usuario_actual(request):
    usuario = None
    if request.session.get('usuario_id'):
        try:
            usuario = Usuario.objects.using('conectati').get(id=request.session['usuario_id'])
        except Usuario.DoesNotExist:
            pass
    return {'usuario_logueado': usuario}

def datos_chat_context(request):
    if not request.session.get('usuario_id'):
        return {}

    usuario_id = request.session['usuario_id']

    # Chats existentes
    chats = Chat.objects.using('conectati').filter(
        Q(usuario1_id=usuario_id) | Q(usuario2_id=usuario_id)
    )

    lista_chats = []
    for c in chats:
        otro = c.usuario2 if c.usuario1_id == usuario_id else c.usuario1
        lista_chats.append({
            'id': c.id,
            'nombre': otro.nombre,
            'username': otro.username,
            'foto': otro.foto if otro.foto else '/static/images/default_user.avif'
        })

    # Solicitudes de chat pendientes recibidas
    solicitudes_pendientes = SolicitudChat.objects.using('conectati').filter(
        para_usuario_id=usuario_id,
        estado='pendiente'
    ).select_related('de_usuario')

    return {
        'chats': lista_chats,
        'solicitudes_chat_pendientes': solicitudes_pendientes
    }