from django.test import TestCase, Client
from django.urls import reverse

class BaseTestConectati(TestCase):
    """
    Clase base para todos los tests que usan la base de datos 'conectati'.
    Incluye cliente, acceso a reverse y aislamiento automático de BDs.
    """
    databases = {'default', 'conectati'}

    def setUp(self):
        self.client = Client()
