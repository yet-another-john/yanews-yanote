from datetime import datetime, timedelta
from django.utils import timezone

import pytest
from django.test.client import Client
from news.models import Comment, News


@pytest.fixture
def anonymous_user(django_user_model):
    anonymous_user = django_user_model.objects.create(
        username='Аноним пользователь')
    return anonymous_user


@pytest.fixture
def another_anonymous_user(django_user_model):
    return django_user_model.objects.create(username='Аноним пользователь #2')


@pytest.fixture
def another_anonymous_user_client(another_anonymous_user):
    client = Client()
    client.force_login(another_anonymous_user)
    return client


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def news_list(author):
    news_list = []
    today = datetime.today()
    for i in range(10):
        news_list.append(
            News.objects.create(
                title='Заголовок',
                text='Текст заметки',
                date=today - timedelta(days=i)
            )
        )
    return news_list


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news_id=news.id,
        text='Текст заметки',
        author=author,
    )
    return comment


@pytest.fixture
def another_comment(not_author, news):
    another_comment = Comment.objects.create(
        news_id=news.id,
        text='Текст заметки',
        author=not_author,
    )
    return another_comment


@pytest.fixture
def comment_list(author, news):
    comment_list = []
    for i in range(3):
        comment_list.append(
            Comment.objects.create(
                news_id=news.id,
                text='Текст заметки',
                author=author,
            )
        )
    now = timezone.now()
    for comment in comment_list:
        comment.created = now + timedelta(days=comment.id)
        comment.save()
    return comment_list


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def another_comment_id_for_args(another_comment):
    return (another_comment.id,)


@pytest.fixture
def news_id_for_args(news):
    return (news.id,)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }
