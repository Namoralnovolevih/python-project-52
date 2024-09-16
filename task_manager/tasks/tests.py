from django.test import TestCase, Client
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
from ..statuses.models import Status
from ..labels.models import Label
from .models import Task


class TasksTests(TestCase):
    @staticmethod
    def get_model_id_by_name(model: ('Users', Status, Label, Task), # noqa
                             name: str) -> int:
        if model == 'Users':
            return get_user_model().objects.get(username=name).id
        return model.objects.get(name=name).id

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
        cls.user_author = user_model.objects.create_user(
            username='author_tasks',
            password='pass',
            first_name='Author',
            last_name='Tasks'
        )
        cls.user_executor = user_model.objects.create_user(
            username='executor_tasks',
            password='pass',
            first_name='Executor',
            last_name='Tasks'
        )
        cls.user_delete = user_model.objects.create_user(
            username='user_for_delete',
            password='pass',
            first_name='User for',
            last_name='Delete'
        )

        cls.status_check = Status.objects.create(name='Status for check')
        cls.status_update = Status.objects.create(name='Status for update')
        cls.status_delete = Status.objects.create(name='Status for delete')

        cls.label_check_1m = Label.objects.create(name='First label for check')
        cls.label_check_2m = Label.objects.create(
            name='Second label for check'
        )
        cls.label_delete = Label.objects.create(name='Label for delete')

        cls.task_check = Task.objects.create(name='Test task',
                                             status=cls.status_check,
                                             description='Test description',
                                             executor=cls.user_executor,
                                             author=cls.user_author)
        cls.task_check.labels.add(cls.label_check_1m, cls.label_check_2m)

    def test_error_access(self):
        response_redirect = self.client.get('/tasks/')
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.get('/tasks/create/')
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.get('/tasks/1/update/')
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.get('/tasks/1/delete/')
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        user_executor_id = self.get_model_id_by_name('Users', 'executor_tasks')
        status_id = self.get_model_id_by_name(Status, 'Status for check')

        response_redirect = self.client.post(
            '/tasks/create/',
            {'name': 'Test task',
             'status': status_id,
             'description': 'This is somethong',
             'executor': user_executor_id,
             'author': self.user_author}
        )
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        task_id = self.get_model_id_by_name(Task, 'Test task')

        response_redirect = self.client.post(f'/tasks/{task_id}/update/',
                                             {'name': 'task1',
                                              'status': status_id,
                                              'description': 'Fuh1',
                                              'executor': user_executor_id,
                                              'author': self.user_author})
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

        response_redirect = self.client.post(f'/tasks/{task_id}/update/')
        response = self.client.get('/login/')
        content = response.content.decode()
        self.assertIn('You are not authorized! Please come in.', content)
        self.assertRedirects(response_redirect, '/login/', 302, 200)

    def test_successfull_access(self):
        self.client.login(username="author_tasks", password="pass")
        task_id = self.get_model_id_by_name(Task, 'Test task')

        response = self.client.get('/tasks/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)
        content = response.content.decode()
        self.assertIn('Test task', content)
        self.assertIn('Status for check', content)
        self.assertIn('Author Tasks', content)
        self.assertIn('Executor Tasks', content)

        response = self.client.get(f'/tasks/{task_id}/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)
        content = response.content.decode()
        self.assertIn('Test task', content)
        self.assertIn('Status for check', content)
        self.assertIn('Author Tasks', content)
        self.assertIn('Executor Tasks', content)
        self.assertIn('First label for check', content)
        self.assertIn('Second label for check', content)

        response = self.client.get('/tasks/create/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        response = self.client.get(f'/tasks/{task_id}/update/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        response = self.client.get(f'/tasks/{task_id}/delete/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

    def test_work_tasks(self):
        self.client.login(username="author_tasks", password="pass")
        user_delete_id = self.get_model_id_by_name('Users', 'user_for_delete')
        status_update_id = self.get_model_id_by_name(Status,
                                                     'Status for update')
        status_delete_id = self.get_model_id_by_name(Status,
                                                     'Status for delete')
        label_id_1 = self.get_model_id_by_name(Label, 'First label for check')
        label_id_delete = self.get_model_id_by_name(Label, 'Label for delete')
# Checking the creation of the task.
        response_redirect = self.client.post(
            '/tasks/create/',
            {'name': 'New work',
             'status': status_delete_id,
             'description': 'Sleep',
             'executor': user_delete_id,
             'labels': (label_id_1, label_id_delete)}
        )
        response = self.client.get('/tasks/')
        content = response.content.decode()
        self.assertIn('New work', content)
        self.assertIn('Status for delete', content)
        self.assertIn('User for Delete', content)
        self.assertRedirects(response_redirect, '/tasks/', 302, 200)
# Checking the creation of a task of the same name.
        response = self.client.post('/tasks/create/',
                                    {'name': 'New work',
                                     'status': status_update_id,
                                     'labels': label_id_1})
        status_code = response.status_code
        self.assertEqual(status_code, 200)

        new_task_id = self.get_model_id_by_name(Task, 'New work')
# Checking the presence of labels in the task.
        response = self.client.get(f'/tasks/{new_task_id}/')
        content = response.content.decode()
        self.assertIn('First label for check', content)
        self.assertIn('Label for delete', content)
# Checks that the label in use cannot be deleted.
        response_redirect = self.client.post(
            f'/labels/{label_id_delete}/delete/'
        )
        response = self.client.get('/labels/')
        content = response.content.decode()
        self.assertIn('The label cannot be deleted because it is in use.',
                      content)
        self.assertIn('Label for delete', content)
        self.assertRedirects(response_redirect, '/labels/', 302, 200)
# Checks that the status in use cannot be deleted.
        response_redirect = self.client.post(
            f'/statuses/{status_delete_id}/delete/'
        )
        response = self.client.get('/statuses/')
        content = response.content.decode()
        self.assertIn('The status cannot be deleted because it is in use.',
                      content)
        self.assertIn('Status for delete', content)
        self.assertRedirects(response_redirect, '/statuses/', 302, 200)
# Checks that the user in use cannot be deleted.
        self.client.login(username="user_for_delete", password="pass")
        response_redirect = self.client.post(f'/users/{user_delete_id}/delete/')
        response = self.client.get('/users/')
        content = response.content.decode()
        self.assertIn('The user cannot be deleted because it is in use.',
                      content)
        self.assertIn('User for Delete', content)
        self.assertRedirects(response_redirect, '/users/', 302, 200)
        self.client.login(username="author_tasks", password="pass")
# Checking the task update.
        response_redirect = self.client.post(f'/tasks/{new_task_id}/update/',
                                             {'name': 'task2 update',
                                              'status': status_update_id,
                                              'labels': label_id_1})
        response = self.client.get('/tasks/')
        content = response.content.decode()
        self.assertIn('task2 update', content)
        self.assertRedirects(response_redirect, '/tasks/', 302, 200)
# Check that the label can be removed.
        response_redirect = self.client.post(
            f'/labels/{label_id_delete}/delete/'
        )
        response = self.client.get('/labels/')
        content = response.content.decode()
        self.assertIn('Label deleted successfully', content)
        self.assertNotIn('Label for delete', content)
        self.assertRedirects(response_redirect, '/labels/', 302, 200)
# Check that the status can be removed.
        response_redirect = self.client.post(
            f'/statuses/{status_delete_id}/delete/'
        )
        response = self.client.get('/statuses/')
        content = response.content.decode()
        self.assertIn('Status deleted successfully', content)
        self.assertNotIn('Status for delete', content)
        self.assertRedirects(response_redirect, '/statuses/', 302, 200)
# Check that the user can be removed.
        self.client.login(username="user_for_delete", password="pass")
        response_redirect = self.client.post(f'/users/{user_delete_id}/delete/')
        response = self.client.get('/users/')
        content = response.content.decode()
        self.assertIn('User deleted successfully', content)
        self.assertNotIn('User for Delete', content)
        self.assertRedirects(response_redirect, '/users/', 302, 200)
        self.client.login(username="author_tasks", password="pass")
# Check that the task can be removed.
        response_redirect = self.client.post(f'/tasks/{new_task_id}/delete/')
        response = self.client.get('/tasks/')
        content = response.content.decode()
        self.assertNotIn('task2 update', content)
        self.assertRedirects(response_redirect, '/tasks/', 302, 200)

    def test_filter_task(self):
        self.client.login(username="user_for_delete", password="pass")

        user_delete_id = self.get_model_id_by_name('Users', 'user_for_delete')

        status_check_id = self.get_model_id_by_name(Status, 'Status for check')
        status_update_id = self.get_model_id_by_name(Status,
                                                     'Status for update')

        label_id_1 = self.get_model_id_by_name(Label, 'First label for check')
        label_id_delete = self.get_model_id_by_name(Label, 'Label for delete')

        self.client.post('/tasks/create/',
                         {'name': 'Check',
                          'status': status_check_id,
                          'labels': label_id_1})
        self.client.post('/tasks/create/',
                         {'name': 'Update delete',
                          'status': status_update_id,
                          'labels': label_id_delete})
        self.client.post('/tasks/create/',
                         {'name': 'Executor delete',
                          'status': status_check_id,
                          'executor': user_delete_id,
                          'labels': label_id_1})

        response = self.client.get('/tasks/')
        content = response.content.decode()
        self.assertIn('Test task', content)
        self.assertIn('Check', content)
        self.assertIn('Update delete', content)
        self.assertIn('Executor delete', content)

        response = self.client.get(f'/tasks/?status={status_check_id}')
        content = response.content.decode()
        self.assertIn('Test task', content)
        self.assertIn('Check', content)
        self.assertNotIn('Update delete', content)
        self.assertIn('Executor delete', content)

        response = self.client.get(f'/tasks/?label={label_id_delete}')
        content = response.content.decode()
        self.assertNotIn('Test task', content)
        self.assertNotIn('Check', content)
        self.assertIn('Update delete', content)
        self.assertNotIn('Executor delete', content)

        response = self.client.get(f'/tasks/?executor={user_delete_id}')
        content = response.content.decode()
        self.assertNotIn('Test task', content)
        self.assertNotIn('Check', content)
        self.assertNotIn('Update delete', content)
        self.assertIn('Executor delete', content)

        response = self.client.get('/tasks/?self_tasks=on')
        content = response.content.decode()
        self.assertNotIn('Test task', content)
        self.assertIn('Check', content)
        self.assertIn('Update delete', content)
        self.assertIn('Executor delete', content)

        url = (
            '/tasks/',
            f'?status={status_check_id}',
            f'&executor={user_delete_id}',
            f'&label={label_id_delete}',
            '&self_tasks=on',
        )
        response = self.client.get(url)
        content = response.content.decode()
        self.assertNotIn('Test task', content)
        self.assertNotIn('Check', content)
        self.assertNotIn('Update delete', content)
        self.assertNotIn('Executor delete', content)
