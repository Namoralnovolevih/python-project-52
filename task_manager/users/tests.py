from django.test import TestCase, Client
from django.test.utils import override_settings
from django.contrib.auth import get_user_model


class UsersTests(TestCase):

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
        cls.user1 = user_model.objects.create_user(username='utest1',
                                                   password='ptest')
        cls.user2 = user_model.objects.create_user(username='utest2',
                                                   password='ptest')

    def test_show_users(self):
        response = self.client.get('/users/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        content = response.content.decode()
        self.assertIn('utest1', content)
        self.assertIn('utest2', content)

    def test_create_user(self):
        response = self.client.get('/users/create/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        response_redirect = self.client.post('/users/create/',
                                             {"username": "utest3",
                                              "password1": "ptest",
                                              "password2": "ptest"})

        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You have successfully registered', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

    def test_error_create_user(self):
        response = self.client.post('/users/create/', {"username": "utest3#",
                                                       "password1": "ptest",
                                                       "password2": "ptest"})
        content = response.content.decode()
        self.assertIn('numbers and the symbols @/./+/-/_.', content)

        response = self.client.post('/users/create/', {"username": "utest3",
                                                       "password1": "p",
                                                       "password2": "p"})
        content = response.content.decode()
        self.assertIn('This password is too short.', content)

        response = self.client.post('/users/create/', {"username": "utest1",
                                                       "password1": "ppp",
                                                       "password2": "ppp"})
        content = response.content.decode()
        self.assertIn('A user with that username already exists.', content)

    def test_update_user(self):
        self.client.login(username="utest1", password="ptest")
        user_id = get_user_model().objects.get(username='utest2').id
        response_redirect = self.client.get(f'/users/{user_id}/update/')

        response = self.client.get('/users/')
        content = response.content.decode()
        self.assertIn('You do not have permission to modify another user.',
                      content)
        self.assertRedirects(response_redirect, '/users/', 302, 200)

        user_id = get_user_model().objects.get(username='utest1').id
        response = self.client.get(f'/users/{user_id}/update/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        response_redirect = self.client.post(f'/users/{user_id}/update/',
                                             {"username": "utest10",
                                              "password1": "ptest",
                                              "password2": "ptest"})
        response = self.client.get('/users/')
        content = response.content.decode()
        self.assertIn('User successfully changed', content)
        self.assertIn('utest10', content)
        self.assertIn('Log In', content)
        self.assertRedirects(response_redirect, '/users/', 302, 200)

        self.client.login(username="utest10", password="ptest")
        response = self.client.get(f'/users/{user_id}/update/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

    def test_delete_user(self):
        self.client.login(username="utest1", password="ptest")

        user_id = get_user_model().objects.get(username='utest2').id
        response_redirect = self.client.get(f'/users/{user_id}/delete/')
        response = self.client.get('/users/')
        content = response.content.decode()
        self.assertIn('You do not have permission to modify another user.',
                      content)
        self.assertRedirects(response_redirect, '/users/', 302, 200)

        user_id = get_user_model().objects.get(username='utest1').id
        response = self.client.get(f'/users/{user_id}/delete/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)
        content = response.content.decode()
        self.assertIn('utest1', content)

        response_redirect = self.client.post(f'/users/{user_id}/delete/')
        response = self.client.get('/users/')
        content = response.content.decode()
        self.assertIn('User deleted successfully', content)
        self.assertNotIn('utest1', content)
        self.assertIn('Log In', content)
        self.assertRedirects(response_redirect, '/users/', 302, 200)
