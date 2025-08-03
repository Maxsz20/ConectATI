from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from app.models import Usuario, Configuracion, Publicacion
from django.contrib.auth.hashers import make_password
from app.tests.base_test import BaseTestConectati

class PublicacionTestCase(BaseTestConectati):
    def setUp(self):
        super().setUp()
        self.url_feed = reverse('feed')
        self.url_mobile = reverse('post_mobile')

        self.usuario = Usuario.objects.using('conectati').create(
            nombre='Daniela Carrero',
            username='daniela',
            email='daniela@example.com',
            ci='12345678',
            contrasena=make_password('clave123')
        )

        Configuracion.objects.using('conectati').create(
            usuario=self.usuario,
            publicaciones_privadas=False,
            idioma='es',
            tema='claro',
            notificar_chat=True,
            notificar_comentario=True,
            notificar_amistad=True
        )

        session = self.client.session
        session['usuario_id'] = self.usuario.id
        session.save()

    # -------- DESKTOP (FEED) --------
    def test_post_desktop_texto(self):
        data = {
            'texto': 'Publicación desde desktop',
            'privacidad': 'publica'
        }
        response = self.client.post(self.url_feed, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Publicacion.objects.using('conectati').filter(texto='Publicación desde desktop').exists())

    def test_post_desktop_vacio(self):
        data = {
            'texto': '',
            'privacidad': 'publica'
        }
        response = self.client.post(self.url_feed, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No puedes publicar algo vacío.")
        self.assertFalse(Publicacion.objects.using('conectati').exists())

    def test_post_desktop_con_imagen(self):
        imagen = SimpleUploadedFile("foto_desktop.jpg", b"fakeimg", content_type="image/jpeg")
        data = {
            'texto': 'Desktop con imagen',
            'archivo': imagen,
            'privacidad': 'publica'
        }
        response = self.client.post(self.url_feed, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Publicacion.objects.using('conectati').filter(texto='Desktop con imagen').exists())

    def test_post_desktop_privada(self):
        data = {
            'texto': 'Post privado desktop',
            'privacidad': 'privada'
        }
        response = self.client.post(self.url_feed, data=data)
        self.assertEqual(response.status_code, 302)
        pub = Publicacion.objects.using('conectati').get(usuario=self.usuario, texto='Post privado desktop')
        self.assertEqual(pub.privacidad, 'privada')

    # -------- MOBILE --------
    def test_post_mobile_texto(self):
        data = {
            'texto': 'Publicación desde mobile',
            'privacidad': 'publica'
        }
        response = self.client.post(self.url_mobile, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Publicacion.objects.using('conectati').filter(texto='Publicación desde mobile').exists())

    def test_post_mobile_vacio(self):
        data = {
            'texto': '',
            'privacidad': 'publica'
        }
        response = self.client.post(self.url_mobile, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No puedes publicar algo vacío.")
        self.assertFalse(Publicacion.objects.using('conectati').exists())

    def test_post_mobile_con_imagen(self):
        imagen = SimpleUploadedFile("foto_mobile.jpg", b"fakeimg", content_type="image/jpeg")
        data = {
            'texto': 'Mobile con imagen',
            'archivo': imagen,
            'privacidad': 'publica'
        }
        response = self.client.post(self.url_mobile, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Publicacion.objects.using('conectati').filter(texto='Mobile con imagen').exists())

    def test_post_mobile_privada(self):
        data = {
            'texto': 'Post privado mobile',
            'privacidad': 'privada'
        }
        response = self.client.post(self.url_mobile, data=data)
        self.assertEqual(response.status_code, 302)
        pub = Publicacion.objects.using('conectati').get(usuario=self.usuario, texto='Post privado mobile')
        self.assertEqual(pub.privacidad, 'privada')
