import pytest
from django.urls import reverse
from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


def test_news_list(news_list, author_client):
    url = reverse('news:home')
    response = author_client.get(url)
    object_list = response.context['object_list']
    assert object_list.count() <= NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.parametrize(
    'parametrized_client, news_in_list',
    (
        (pytest.lazy_fixture('author_client'), None),
    )
)
def test_news_order(
        news_list, parametrized_client, news_in_list
):
    url = reverse('news:home')
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.parametrize(
    'parametrized_client, news_in_list',
    (
        (pytest.lazy_fixture('author_client'), None),
    )
)
def test_comments_order(
        news, comment_list, parametrized_client, news_in_list, news_id_for_args
):
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
        (pytest.lazy_fixture('another_anonymous_user_client'), True),
    )
)
def test_form_for_auth_client(parametrized_client, response, news_id_for_args):
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
def test_form_for_anonymous(parametrized_client, response, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    response = parametrized_client.get(url)
    assert 'form' not in response.context
