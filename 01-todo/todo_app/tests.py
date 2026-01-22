from django.test import TestCase, Client
from django.urls import reverse
from .models import Todo
from datetime import date

class TodoModelTest(TestCase):
    def test_todo_creation(self):
        todo = Todo.objects.create(title="Test Todo", description="Test Description")
        self.assertEqual(todo.title, "Test Todo")
        self.assertEqual(todo.description, "Test Description")
        self.assertFalse(todo.is_resolved)

class TodoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.todo = Todo.objects.create(title="Test Todo", due_date=date.today())

    def test_todo_list_view(self):
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Todo")

    def test_todo_create_view(self):
        response = self.client.post(reverse('todo_create'), {
            'title': 'New Todo',
            'description': 'New Description',
            'due_date': '2023-12-31'
        })
        self.assertEqual(response.status_code, 302) # Redirects after success
        self.assertEqual(Todo.objects.count(), 2)

    def test_todo_update_view(self):
        response = self.client.post(reverse('todo_update', args=[self.todo.pk]), {
            'title': 'Updated Todo',
            'description': 'Updated Description',
            'due_date': '2023-12-31',
            'is_resolved': 'on'
        })
        self.assertEqual(response.status_code, 302)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Todo')
        self.assertTrue(self.todo.is_resolved)

    def test_todo_delete_view(self):
        response = self.client.get(reverse('todo_delete', args=[self.todo.pk])) # Using GET for delete as per implementation (link)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Todo.objects.count(), 0)
