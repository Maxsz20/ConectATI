from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from app.models import Usuario, CodigoRecuperacion
import json

class ForgottenPasswordTestCase(TestCase):
    databases = {'default', 'conectati'}

    def setUp(self):
        self.client = Client()
        self.url_vista = reverse('forgotten_password')
        self.url_enviar_codigo = reverse('enviar_codigo')
        self.usuario = Usuario.objects.using('conectati').create(
            nombre='Daniela Carrero',
            username='daniela',
            email='daniela@example.com',
            ci='12345678',
            contrasena=make_password('123456')
        )

    def test_renderizado_html_correcto(self):
        response = self.client.get(self.url_vista)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Recuperar Contraseña')
        self.assertContains(response, 'form')
        self.assertContains(response, 'type="email"')
        self.assertContains(response, 'Enviar código')

    def test_peticion_post_sin_email(self):
        response = self.client.post(self.url_enviar_codigo, content_type="application/json", data="{}")
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"ok": False, "error": "Correo vacío"})

    def test_peticion_post_con_email_inexistente(self):
        response = self.client.post(
            self.url_enviar_codigo,
            content_type="application/json",
            data=json.dumps({"email": "noexiste@example.com"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {"ok": False, "error": "Correo no registrado"})

    def test_peticion_post_exitosa(self):
        response = self.client.post(
            self.url_enviar_codigo,
            content_type="application/json",
            data=json.dumps({"email": "daniela@example.com"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"ok": True})
        self.assertTrue(
            CodigoRecuperacion.objects.using('conectati').filter(usuario=self.usuario).exists()
        )
