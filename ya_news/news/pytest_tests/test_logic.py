from http import HTTPStatus

import pytest
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects


@pytest.mark.django_db
def test_anonymous_cant_create_comment(client, form_data, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_note(author_client, form_data, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    author_client.post(url, data=form_data)
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news_id_for_args):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(author_client, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    author_client.post(url, {'text': 'Новый Новый текст'})
    comment = Comment.objects.get()
    assert comment.text == 'Новый Новый текст'


def test_author_can_delete_comment(author_client, news_id_for_args):
    url = reverse('news:delete', args=news_id_for_args)
    author_client.post(url)
    assert Comment.objects.count() == 0


def test_author_cant_edit_user_comment(
        author_client,
        another_comment_id_for_args
):
    url = reverse('news:edit', args=another_comment_id_for_args)
    author_client.post(url, {'text': 'Новый Новый текст'})
    another_comment = Comment.objects.get()
    assert another_comment.text != 'Новый Новый текст'


def test_author_cant_delete_user_comment(
        author_client,
        another_comment_id_for_args
):
    url = reverse('news:delete', args=another_comment_id_for_args)
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
