from django.test import TestCase, Client
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
from .models import Status


def get_status_id_by_name(name: str) -> int:
    return Status.objects.get(name=name).id


class StatusesTests(TestCase):

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
        cls.user = user_model.objects.create_user(username='user_status',
                                                  password='pass_status')

        cls.status1 = Status.objects.create(name='first status')
        cls.status2 = Status.objects.create(name='second status')

    def test_error_access(self):
        id = get_status_id_by_name('first status')

        response_redirect = self.client.get('/statuses/')
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.get('/statuses/create/')
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.get(f'/statuses/{id}/update/')
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.get(f'/statuses/{id}/delete/')
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.post('/statuses/create/',
                                             {'name': 'test status'})
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.post(f'/statuses/{id}/update/',
                                             {'name': 'test status'})
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.post(f'/statuses/{id}/delete/')
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

    def test_successfull_access(self):
        self.client.login(username="user_status", password="pass_status")
        id = get_status_id_by_name('first status')

        response = self.client.get('/statuses/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        response = self.client.get('/statuses/create/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        response = self.client.get(f'/statuses/{id}/update/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        response = self.client.get(f'/statuses/{id}/delete/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

    def test_work_statuses(self):
        self.client.login(username="user_status", password="pass_status")
# Checking the display of statuses.
        response = self.client.get('/statuses/')
        content = response.content.decode()
        self.assertIn('first status', content)
        self.assertIn('second status', content)
# Checking the creation of status.
        response_redirect = self.client.post('/statuses/create/',
                                             {'name': 'test status'})
        response = self.client.get('/statuses/')
        content = response.content.decode()
        self.assertIn('Status successfully created', content)
        self.assertIn('test status', content)
        self.assertRedirects(response_redirect, '/statuses/', 302, 200)
# We check the creation of a second identical status.
        response = self.client.post('/statuses/create/',
                                    {'name': 'test status'})
        status_code = response.status_code
        self.assertEqual(status_code, 200)
        count_statuses = len(Status.objects.all())
        self.assertEqual(count_statuses, 3)

        new_status_id = get_status_id_by_name('test status')
# Checking the status update.
        response_redirect = self.client.post(
            f'/statuses/{new_status_id}/update/',
            {'name': 'test status rename'})
        response = self.client.get('/statuses/')
        content = response.content.decode()
        self.assertIn('Status successfully changed', content)
        self.assertIn('test status rename', content)
        self.assertRedirects(response_redirect, '/statuses/', 302, 200)
# Checking status deletion.
        response_redirect = self.client.post(
            f'/statuses/{new_status_id}/delete/'
        )
        response = self.client.get('/statuses/')
        content = response.content.decode()
        self.assertIn('Status deleted successfully', content)
        self.assertNotIn('test status rename', content)
        self.assertRedirects(response_redirect, '/statuses/', 302, 200)
