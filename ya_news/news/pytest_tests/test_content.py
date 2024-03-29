import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from news.forms import CommentForm


@pytest.mark.parametrize(
    'parametrized_client, news_in_list',
    (
        (pytest.lazy_fixture('author_client'), 10),
    )
)
def test_news_list(
        news_list, parametrized_client, news_in_list
):
    url = reverse('news:home')
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    assert object_list.count() <= news_in_list


@pytest.mark.parametrize(
    'parametrized_client, news_in_list',
    (
        (pytest.lazy_fixture('author_client'), None),
    )
)
def test_news_order(
        news, comment_list, parametrized_client, news_in_list, news_id_for_args
):
    now = timezone.now()
    for comment in comment_list:
        comment.created = now + timedelta(days=comment.id)
        comment.save()
    url = reverse('news:detail', args=(news_id_for_args))
    response = parametrized_client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_client, response',
    (
        (pytest.lazy_fixture('anonymous_user1_client'), True),
    )
)
def test_form_availability_for_auth_client(parametrized_client, response, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    response = parametrized_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.parametrize(
    'parametrized_client, response',
    (
        (pytest.lazy_fixture('client'), False),
    )
)
def test_form_availability_for_anonymous_client(parametrized_client, response, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    response = parametrized_client.get(url)
    assert 'form' not in response.context
