from django.urls import reverse
from app.models import Usuario, Amistad
from django.contrib.auth.hashers import make_password
from app.tests.base_test import BaseTestConectati
import json

class SolicitudAmistadTestCase(BaseTestConectati):
    def setUp(self):
        super().setUp()
        # Usuarios de prueba
        self.usuario1 = Usuario.objects.using('conectati').create(
            nombre='Daniela',
            username='daniela',
            email='daniela@example.com',
            ci='11111111',
            contrasena=make_password('clave123')
        )
        self.usuario2 = Usuario.objects.using('conectati').create(
            nombre='Maxi',
            username='maxi',
            email='maxi@example.com',
            ci='22222222',
            contrasena=make_password('clave123')
        )
        self.url = reverse('enviar_solicitud_amistad')

        session = self.client.session
        session['usuario_id'] = self.usuario1.id
        session.save()

    def test_enviar_solicitud_exito(self):
        data = {'para_usuario_id': self.usuario2.id}
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'ok': True})
        self.assertTrue(Amistad.objects.using('conectati').filter(
            de_usuario=self.usuario1, para_usuario=self.usuario2).exists())

    def test_enviar_solicitud_duplicada(self):
        # Primero, crea la solicitud
        Amistad.objects.using('conectati').create(
            de_usuario=self.usuario1, para_usuario=self.usuario2, estado='pendiente')
        data = {'para_usuario_id': self.usuario2.id}
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'ok': False, 'error': 'Ya existe'})
        # Solo debe existir una solicitud pendiente
        self.assertEqual(Amistad.objects.using('conectati').filter(
            de_usuario=self.usuario1, para_usuario=self.usuario2).count(), 1)

    def test_enviar_solicitud_usuario_inexistente(self):
        data = {'para_usuario_id': 99999}
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'ok': False, 'error': 'Usuario destino no existe'})
        self.assertEqual(Amistad.objects.using('conectati').filter(
            de_usuario=self.usuario1, para_usuario_id=99999).count(), 0)

    def test_solo_permite_post_y_autenticado(self):
        # No autenticado
        client2 = self.client_class()
        data = {'para_usuario_id': self.usuario2.id}
        response = client2.post(self.url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {'ok': False, 'error': 'Método no permitido'})
        # No es POST
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {'ok': False, 'error': 'Método no permitido'})
