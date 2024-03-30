from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.form_data = {
            'title': 'form_data',
            'text': 'form_data',
            'slug': 'form_data',
        }
        cls.form_data1 = {
            'title': 'form_data1',
            'text': 'form_data1',
            'slug': 'form_data',
        }
        cls.form_data2 = {
            'title': 'форм_дата2',
            'text': 'form_data2',
            'slug': '',
        }

    def test_anonymous_user_cant_create_comment(self):
        url = reverse('notes:add')
        self.client.post(url, data=self.form_data)
        note = Note.objects.count()
        self.assertEqual(note, 0)

    def test_user_can_create_comment(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.client.post(url, data=self.form_data)
        note = Note.objects.count()
        self.assertEqual(note, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, 'form_data')
        self.assertEqual(note.text, 'form_data')
        self.assertEqual(note.slug, 'form_data')

    def test_notes_and_slugs(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.client.post(url, data=self.form_data)
        self.client.post(url, data=self.form_data1)
        notes = Note.objects.count()
        self.assertEqual(notes, 1)

    def test_empty_slug(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.client.post(url, data=self.form_data2)
        note = Note.objects.get()
        self.assertEqual(note.slug, 'formdata2')


class TestNoteEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
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
        cls.new_form_data = {
            'title': 'new_form_data',
            'text': 'new_form_data',
            'slug': 'new_form_data',
        }

    def test_author_can_delete_note(self):
        notes = Note.objects.count()
        self.assertEqual(notes, 2)
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.delete(url)
        note = Note.objects.get()
        self.assertEqual(note.title, 'note1')

    def test_author_cant_delete_note_of_another_user(self):
        notes = Note.objects.count()
        self.assertEqual(notes, 2)
        self.client.force_login(self.author1)
        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.delete(url)
        notes = Note.objects.count()
        self.assertEqual(notes, 2)

    def test_author_can_edit_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.post(url, data=self.new_form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'new_form_data')
        self.assertEqual(self.note.text, 'new_form_data')
        self.assertEqual(self.note.slug, 'new_form_data')

    def test_author_cant_edit_note_of_another_user(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note1.slug,))
        response = self.client.post(url, data=self.new_form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note1.title, 'note1')
        self.assertEqual(self.note1.text, 'note1')
        self.assertEqual(self.note1.slug, 'note1')
