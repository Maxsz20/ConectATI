from django.urls import reverse
from app.models import Usuario
from django.contrib.auth.hashers import make_password
from app.tests.base_test import BaseTestConectati



class RegistroTestCase(BaseTestConectati):
    def setUp(self):
        super().setUp()
        self.url = reverse('register')
        self.url_login = reverse('login')

    def test_renderizado_html_correcto(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ConectATI')
        self.assertContains(response, 'Registrarse')
        self.assertContains(response, 'name="nombre"')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="ci"')
        self.assertContains(response, 'name="contrasena"')
        self.assertContains(response, 'name="confirmar_contrasena"')

    def test_registro_exitoso_redirecciona_a_login(self):
        datos = {
            'nombre': 'Daniela Carrero',
            'username': 'daniela',
            'email': 'daniela@example.com',
            'ci': '12345678',
            'contrasena': 'contrasena_segura',
            'confirmar_contrasena': 'contrasena_segura',
        }
        response = self.client.post(self.url, data=datos)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url_login)
        self.assertTrue(
            Usuario.objects.using('conectati').filter(username='daniela').exists()
        )

    def test_registro_con_passwords_diferentes(self):
        datos = {
            'nombre': 'Daniela Carrero',
            'username': 'daniela',
            'email': 'daniela@example.com',
            'ci': '12345678',
            'contrasena': 'clave1',
            'confirmar_contrasena': 'clave2',
        }
        response = self.client.post(self.url, data=datos)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Las contraseñas no coinciden')
        self.assertFalse(
            Usuario.objects.using('conectati').filter(username='daniela').exists()
        )

    def test_registro_con_username_repetido(self):
        Usuario.objects.using('conectati').create(
            nombre='Existente',
            username='daniela',
            email='otro@example.com',
            ci='99999999',
            contrasena=make_password('123')
        )
        datos = {
            'nombre': 'Nuevo',
            'username': 'daniela',
            'email': 'nuevo@example.com',
            'ci': '12345678',
            'contrasena': 'clave123',
            'confirmar_contrasena': 'clave123',
        }
        response = self.client.post(self.url, data=datos)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este nombre de usuario ya está registrado.")

    def test_registro_con_email_repetido(self):
        Usuario.objects.using('conectati').create(
            nombre='Existente',
            username='otro',
            email='daniela@example.com',
            ci='88888888',
            contrasena=make_password('123')
        )
        datos = {
            'nombre': 'Nuevo',
            'username': 'nuevo',
            'email': 'daniela@example.com',
            'ci': '12345678',
            'contrasena': 'clave123',
            'confirmar_contrasena': 'clave123',
        }
        response = self.client.post(self.url, data=datos)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este correo ya está registrado.")

    def test_registro_con_ci_repetida(self):
        Usuario.objects.using('conectati').create(
            nombre='Existente',
            username='otro',
            email='otro@example.com',
            ci='12345678',
            contrasena=make_password('123')
        )
        datos = {
            'nombre': 'Nuevo',
            'username': 'nuevo',
            'email': 'nuevo@example.com',
            'ci': '12345678',
            'contrasena': 'clave123',
            'confirmar_contrasena': 'clave123',
        }
        response = self.client.post(self.url, data=datos)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Esta cédula ya está registrada.")
