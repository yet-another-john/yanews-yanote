from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='reader')
        cls.author = User.objects.create(username='author')
        cls.author1 = User.objects.create(username='author1')
        cls.note = Note.objects.create(
            title='note',
            text='note',
            author=cls.author,
            slug='note'
        )
        cls.note1 = Note.objects.create(
            title='note1',
            text='note1',
            author=cls.author1,
            slug='note1'
        )

    def test_note_in_object_list(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertIn(self.note, response.context['object_list'])

    def test_list_of_notes_for_user(self):
        url = reverse('notes:list')
        self.client.force_login(self.author)
        response = self.client.get(url)
        self.client.force_login(self.author1)
        response1 = self.client.get(url)
        self.assertNotIn(
            response.context['object_list'], response1.context['object_list'])
        self.assertNotIn(
            response1.context['object_list'], response.context['object_list'])

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
