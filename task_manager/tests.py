from django.test import TestCase, Client
from django.test.utils import override_settings
from django.contrib.auth import get_user_model


class InitialTests(TestCase):

    def setUp(self):
        self.client = Client()

        self._override = override_settings(LANGUAGE_CODE='en-us')
        self._override.enable()

    def tearDown(self):
        self._override.disable()
        super().tearDown()

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='utest',
                                                  password='ptest')

    def test_index(self):
        response = self.client.get('/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        content = response.content.decode()
        self.assertIn('Log In', content)
        self.assertIn('Sign up', content)

    def test_login(self):
        response = self.client.get('/login/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        response_redirect = self.client.post('/login/', {"username": "utest",
                                                         "password": "ptest"})

        response = self.client.get('/')
        content = response.content.decode()
        self.assertIn('utest', content)
        self.assertIn('Log Out', content)
        self.assertIn('You are logged in', content)
        self.assertRedirects(response_redirect, '/', 302, 200)

        response_redirect = self.client.post('/logout/')

        response = self.client.get('/')
        content = response.content.decode()
        self.assertIn('Log In', content)
        self.assertIn('Sign up', content)
        self.assertIn('You are logged out.', content)
        self.assertRedirects(response_redirect, '/', 302, 200)

    def test_error_login(self):
        response = self.client.post('/login/', {"username": "",
                                                "password": ""})
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        response = self.client.post('/login/', {"username": "utest",
                                                "password": "popo"})
        status_code = response.status_code
        self.assertEqual(status_code, 200)
        content = response.content.decode()
        self.assertIn('Please enter a correct username and password.', content)

        response = self.client.post('/login/', {"username": "fug",
                                                "password": "ptest"})
        status_code = response.status_code
        self.assertEqual(status_code, 200)
        content = response.content.decode()
        self.assertIn('Please enter a correct username and password.', content)
