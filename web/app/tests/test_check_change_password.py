from django.urls import reverse
from django.contrib.auth.hashers import make_password
from app.models import Usuario, CodigoRecuperacion
from app.tests.base_test import BaseTestConectati
import json

class RecuperacionCodigoTestCase(BaseTestConectati):
    def setUp(self):
        super().setUp()
        self.usuario = Usuario.objects.using('conectati').create(
            nombre='Daniela',
            username='daniela',
            email='daniela@example.com',
            ci='12345678',
            contrasena=make_password('vieja123')
        )
        self.codigo_obj = CodigoRecuperacion.objects.using('conectati').create(
            usuario=self.usuario,
            codigo='123456'
        )
        self.url_check = reverse('check_code')
        self.url_change = reverse('change_password')

    def test_check_code_get_renderiza_html(self):
        response = self.client.get(self.url_check)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Verifica tu código")

    def test_check_code_post_valido(self):
        response = self.client.post(
            self.url_check,
            content_type="application/json",
            data=json.dumps({"codigo": "123456"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"ok": True})
        self.assertEqual(self.client.session.get("recuperacion_usuario_id"), self.usuario.id)

    def test_check_code_post_invalido(self):
        response = self.client.post(
            self.url_check,
            content_type="application/json",
            data=json.dumps({"codigo": "000000"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {"ok": False, "error": "Código inválido"})

    def test_change_password_get_renderiza_html(self):
        response = self.client.get(self.url_change)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cambiar Contraseña")

    def test_change_password_post_exitosa(self):
        session = self.client.session
        session['recuperacion_usuario_id'] = self.usuario.id
        session.save()

        response = self.client.post(
            self.url_change,
            content_type="application/json",
            data=json.dumps({"nueva": "nueva123"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"ok": True})

    def test_change_password_sin_sesion(self):
        response = self.client.post(
            self.url_change,
            content_type="application/json",
            data=json.dumps({"nueva": "nueva123"})
        )
        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, {"ok": False, "error": "Sesión expirada"})
