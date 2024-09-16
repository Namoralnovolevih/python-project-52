from django.test import TestCase, Client
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
from .models import Label


class LabelsTests(TestCase):

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
        cls.user_auth = user_model.objects.create_user(username='user_label',
                                                       password='pass_label',
                                                       first_name='user',
                                                       last_name='author')
        cls.label_one = Label.objects.create(name='One label')

    def test_error_access(self):
        id = self.label_one.id

        response_redirect = self.client.get('/labels/')
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.get('/labels/create/')
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.get(f'/labels/{id}/update/')
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.get(f'/labels/{id}/delete/')
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.post('/labels/create/',
                                             {'name': 'error labels'})
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.post(f'/labels/{id}/update/',
                                             {'name': 'error labels'})
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.post(f'/labels/{id}/delete/')
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

    def test_successfull_access(self):
        self.client.login(username="user_label", password="pass_label")
        id = self.label_one.id

        response = self.client.get('/labels/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        response = self.client.get('/labels/create/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        response = self.client.get(f'/labels/{id}/update/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        response = self.client.get(f'/labels/{id}/delete/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

    def test_show_labels(self):
        self.client.login(username="user_label", password="pass_label")

        response = self.client.get('/labels/')
        content = response.content.decode()
        self.assertIn('One label', content)

    def test_work_labels(self):
        self.client.login(username="user_label", password="pass_label")
# Checking label creation.
        response_redirect = self.client.post('/labels/create/',
                                             {'name': 'create new label'})
        response = self.client.get('/labels/')
        content = response.content.decode()
        self.assertIn('Label successfully created', content)
        self.assertIn('create new label', content)
        self.assertRedirects(response_redirect, '/labels/', 302, 200)
# Checking the uniqueness of the label name.
        response = self.client.post('/labels/create/',
                                    {'name': 'create new label'})
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        new_label_id = Label.objects.get(name='create new label').id
# Checking for label changes.
        response_redirect = self.client.post(f'/labels/{new_label_id}/update/',
                                             {'name': 'change new label'})
        response = self.client.get('/labels/')
        content = response.content.decode()
        self.assertIn('Label successfully changed', content)
        self.assertIn('change new label', content)
        self.assertRedirects(response_redirect, '/labels/', 302, 200)
# Checking that the label is removed.
        response_redirect = self.client.post(f'/labels/{new_label_id}/delete/')
        response = self.client.get('/labels/')
        content = response.content.decode()
        self.assertIn('Label deleted successfully', content)
        self.assertNotIn('change new label', content)
        self.assertRedirects(response_redirect, '/labels/', 302, 200)
