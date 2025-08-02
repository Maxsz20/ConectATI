from django.urls import reverse
from django.contrib.auth.hashers import make_password
from app.models import Usuario, Configuracion
from app.tests.base_test import BaseTestConectati

class LoginTestCase(BaseTestConectati):
    def setUp(self):
        super().setUp()
        self.url = reverse('login')
        self.url_feed = reverse('feed')
        self.usuario = Usuario.objects.using('conectati').create(
            nombre='Daniela Carrero',
            username='daniela',
            email='daniela@example.com',
            ci='12345678',
            contrasena=make_password('contrasena_segura')
        )
        Configuracion.objects.using('conectati').create(
            usuario=self.usuario,
            tema="claro",
            idioma="es",
            publicaciones_privadas=False,
            notificar_chat=True,
            notificar_comentario=True,
            notificar_amistad=True
        )

    def test_renderizado_login_html(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ConectATI")
        self.assertContains(response, "Iniciar Sesión")
        self.assertContains(response, 'name="correo_usuario"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, "¿Olvidaste tu contraseña?")
        self.assertContains(response, "¿Aún no eres usuario?")

    def test_login_exitoso_con_email(self):
        datos = {
            'correo_usuario': 'daniela@example.com',
            'password': 'contrasena_segura'
        }
        response = self.client.post(self.url, data=datos)
        self.assertRedirects(response, self.url_feed)
        # Verificamos que la sesión fue iniciada
        session = self.client.session
        self.assertEqual(session['usuario_id'], self.usuario.id)

    def test_login_exitoso_con_username(self):
        datos = {
            'correo_usuario': 'daniela',
            'password': 'contrasena_segura'
        }
        response = self.client.post(self.url, data=datos)
        self.assertRedirects(response, self.url_feed)
        session = self.client.session
        self.assertEqual(session['usuario_id'], self.usuario.id)

    def test_login_falla_por_credenciales_incorrectas(self):
        datos = {
            'correo_usuario': 'daniela@example.com',
            'password': 'clave_incorrecta'
        }
        response = self.client.post(self.url, data=datos)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Credenciales incorrectas.")

    def test_login_redirige_si_ya_esta_logueado(self):
        session = self.client.session
        session['usuario_id'] = self.usuario.id
        session.save()
        response = self.client.get(self.url)
        self.assertRedirects(response, self.url_feed)
