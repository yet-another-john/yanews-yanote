import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse
from http import HTTPStatus
from news.models import News, Comment
from pytest_django.asserts import assertRedirects, assertFormError
from news.forms import WARNING, BAD_WORDS


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news_id_for_args):
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


def test_author_cant_edit_user_comment(author_client, id_for_args1):
    url = reverse('news:edit', args=id_for_args1)
    author_client.post(url, {'text': 'Новый Новый текст'})
    comment1 = Comment.objects.get()
    assert comment1.text != 'Новый Новый текст'


def test_author_cant_delete_user_comment(author_client, id_for_args1):
    url = reverse('news:delete', args=id_for_args1)
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
