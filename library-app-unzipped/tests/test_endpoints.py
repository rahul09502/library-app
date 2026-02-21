import pytest
from app import app

# Import create_db to ensure database and sample data exist
import create_db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as c:
        yield c


def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Department Library' in rv.data


def test_search_api(client):
    rv = client.get('/api/search')
    assert rv.status_code == 200
    data = rv.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_student_login_and_dashboard_and_borrow(client):
    # login with sample student from create_db
    resp = client.post('/student/login', data={'email': 'student@example.com', 'password': 'student123'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Welcome' in resp.data or b'Logged in' in resp.data

    # get a book from API
    js = client.get('/api/search').get_json()
    book_id = js[0]['id']
    title = js[0]['title']

    # borrow the book
    resp = client.post(f'/student/borrow/{book_id}', follow_redirects=True)
    assert resp.status_code == 200
    # dashboard should show borrowed title
    dash = client.get('/student/dashboard')
    assert title.encode() in dash.data

    # return the borrow entry (find borrow id)
    # simple way: search dashboard page for 'Return' forms and assume one exists
    assert b'Return' in dash.data