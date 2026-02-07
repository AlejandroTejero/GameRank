from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class SimpleTestCase(TestCase):

    # Prueba de registro
    def test_registration(self):
        # Paso 1: Crear un usuario (registro)
        response = self.client.post(reverse('registro'), {
            'username': 'testuser',
            'password1': 'password123',
            'password2': 'password123',
        })

        # Verificar que el registro fue exitoso
        self.assertEqual(response.status_code, 200)

    # Paso 2: Iniciar sesión
    def test_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)  # Redirige a la página principal

    # Paso 3: Acceder a la página de ayuda de la pagina
    def test_ayuda(self):
        response = self.client.post(reverse('ayuda'))
        self.assertEqual(response.status_code, 200)  # La página de detalles del juego se carga correctamente
