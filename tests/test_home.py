from datetime import timedelta

import pytest

import main


@pytest.fixture(autouse=True)
def isolate_application_state():
    main.app.config.update(TESTING=True, APP_TIMEZONE='UTC')
    main.items.clear()
    main.users.clear()
    yield
    main.items.clear()
    main.users.clear()


@pytest.fixture
def client():
    with main.app.test_client() as test_client:
        with test_client.session_transaction() as session:
            session['user'] = 'test-user'
        yield test_client


def test_unauthenticated_post_redirects_to_login():
    with main.app.test_client() as client:
        response = client.post('/', data={'newItem': 'Task', 'duedate': '2099-01-01'})

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/login')
    assert main.items == []


@pytest.mark.parametrize(
    ('data', 'message'),
    [
        ({}, b'Enter a task name.'),
        ({'newItem': 'Task'}, b'Enter a due date.'),
        ({'newItem': '   ', 'duedate': '2099-01-01'}, b'Enter a task name.'),
        ({'newItem': 'Task', 'duedate': '01-01-2099'}, b'Enter a valid calendar date.'),
        ({'newItem': 'Task', 'duedate': '2099-02-30'}, b'Enter a valid calendar date.')
    ]
)
def test_invalid_posts_are_re_rendered_without_persistence(client, data, message):
    response = client.post('/', data=data)

    assert response.status_code == 200
    assert message in response.data
    assert main.items == []


def test_today_and_past_dates_are_rejected_without_persistence(client):
    today = main.application_now().date()

    for due_date in (today, today - timedelta(days=1)):
        response = client.post(
            '/',
            data={'newItem': 'Task', 'duedate': due_date.isoformat()}
        )

        assert response.status_code == 200
        assert b'Choose a due date later than today.' in response.data
        assert main.items == []


def test_future_date_redirects_and_persists_task(client):
    due_date = main.application_now().date() + timedelta(days=1)

    response = client.post(
        '/',
        data={'newItem': 'Future task', 'duedate': due_date.isoformat()}
    )

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')
    assert main.items == [
        {
            'id': 1,
            'content': 'Future task',
            'due_date': {
                'year': due_date.year,
                'month': due_date.month,
                'day': due_date.day
            }
        }
    ]


def test_configured_application_timezone_controls_date_validation(client):
    main.app.config['APP_TIMEZONE'] = 'Pacific/Kiritimati'
    today = main.application_now().date()

    invalid_response = client.post(
        '/',
        data={'newItem': 'Today', 'duedate': today.isoformat()}
    )
    valid_response = client.post(
        '/',
        data={'newItem': 'Tomorrow', 'duedate': (today + timedelta(days=1)).isoformat()}
    )

    assert b'Choose a due date later than today.' in invalid_response.data
    assert valid_response.status_code == 302
    assert len(main.items) == 1