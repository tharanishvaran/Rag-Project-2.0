import pytest
import os

# ─── Set test database BEFORE importing any app module ───────────────────────
os.environ['DATABASE_URL'] = 'mysql+pymysql://root:Tharanish10435@localhost:3306/smart_doc_ai_test'
os.environ['FLASK_ENV'] = 'development'

from app import create_app
from app.extensions import db as _db


def _drop_and_create(app):
    """Drop all tables and recreate them for a clean test state."""
    with app.app_context():
        _db.drop_all()
        _db.create_all()
        from app.models.category import Category, DEFAULT_CATEGORIES
        for cat_data in DEFAULT_CATEGORIES:
            _db.session.add(Category(name=cat_data['name'], description=cat_data['description']))
        _db.session.commit()


@pytest.fixture(scope='session')
def app():
    """Create Flask test app once per test session using test MySQL DB."""
    test_app = create_app()
    test_app.config.update({
        'TESTING': True,
        'JWT_SECRET_KEY': 'test-jwt-secret-key',
        'UPLOAD_FOLDER': 'test_uploads',
        'CHROMA_PERSIST_DIRECTORY': 'test_chroma_db',
    })
    yield test_app


@pytest.fixture(scope='function', autouse=True)
def clean_db(app):
    """Reset database before every test."""
    _drop_and_create(app)
    yield
    with app.app_context():
        _db.session.remove()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Register a user and return auth headers."""
    client.post('/api/auth/register', json={
        'name': 'Test Student',
        'email': 'test@college.edu',
        'password': 'TestPass1',
    })
    res = client.post('/api/auth/login', json={
        'email': 'test@college.edu',
        'password': 'TestPass1',
    })
    token = res.get_json()['data']['access_token']
    return {'Authorization': f'Bearer {token}'}


# ─── Auth Tests ──────────────────────────────────────────────────────────────

class TestAuth:
    def test_register_success(self, client):
        res = client.post('/api/auth/register', json={
            'name': 'Alice Student',
            'email': 'alice@college.edu',
            'password': 'Alice123',
        })
        assert res.status_code == 201
        data = res.get_json()
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert data['data']['user']['email'] == 'alice@college.edu'

    def test_register_duplicate_email(self, client):
        payload = {'name': 'Bob', 'email': 'bob@college.edu', 'password': 'Bob1234A'}
        client.post('/api/auth/register', json=payload)
        res = client.post('/api/auth/register', json=payload)
        assert res.status_code == 409

    def test_register_invalid_email(self, client):
        res = client.post('/api/auth/register', json={
            'name': 'Test', 'email': 'not-an-email', 'password': 'Test1234'
        })
        assert res.status_code == 400

    def test_register_weak_password(self, client):
        res = client.post('/api/auth/register', json={
            'name': 'Test', 'email': 'test2@college.edu', 'password': 'weak'
        })
        assert res.status_code == 400

    def test_login_success(self, client):
        client.post('/api/auth/register', json={
            'name': 'Login User', 'email': 'login@test.com', 'password': 'Login123'
        })
        res = client.post('/api/auth/login', json={
            'email': 'login@test.com', 'password': 'Login123'
        })
        assert res.status_code == 200
        assert 'access_token' in res.get_json()['data']

    def test_login_wrong_password(self, client):
        client.post('/api/auth/register', json={
            'name': 'User', 'email': 'user@test.com', 'password': 'Correct1'
        })
        res = client.post('/api/auth/login', json={
            'email': 'user@test.com', 'password': 'WrongPass1'
        })
        assert res.status_code == 401

    def test_get_me_authenticated(self, client, auth_headers):
        res = client.get('/api/auth/me', headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()['data']['user']['email'] == 'test@college.edu'

    def test_get_me_unauthenticated(self, client):
        res = client.get('/api/auth/me')
        assert res.status_code == 401


# ─── Category Tests ──────────────────────────────────────────────────────────

class TestCategories:
    def test_get_categories(self, client, auth_headers):
        res = client.get('/api/categories', headers=auth_headers)
        assert res.status_code == 200
        cats = res.get_json()['data']['categories']
        assert len(cats) == 5  # Default 5 categories

    def test_create_category(self, client, auth_headers):
        res = client.post('/api/categories', headers=auth_headers, json={
            'name': 'Lab Manuals', 'description': 'Lab experiment guides'
        })
        assert res.status_code == 201
        assert res.get_json()['data']['category']['name'] == 'Lab Manuals'

    def test_create_duplicate_category(self, client, auth_headers):
        client.post('/api/categories', headers=auth_headers, json={'name': 'Duplicate'})
        res = client.post('/api/categories', headers=auth_headers, json={'name': 'Duplicate'})
        assert res.status_code == 409

    def test_categories_require_auth(self, client):
        res = client.get('/api/categories')
        assert res.status_code == 401


# ─── Documents Tests ─────────────────────────────────────────────────────────

class TestDocuments:
    def test_list_documents_empty(self, client, auth_headers):
        res = client.get('/api/documents', headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()['data']['documents'] == []

    def test_documents_require_auth(self, client):
        res = client.get('/api/documents')
        assert res.status_code == 401

    def test_delete_nonexistent_document(self, client, auth_headers):
        res = client.delete('/api/documents/9999', headers=auth_headers)
        assert res.status_code == 404


# ─── Chat Tests ──────────────────────────────────────────────────────────────

class TestChat:
    def test_create_session(self, client, auth_headers):
        res = client.post('/api/chat/sessions', headers=auth_headers, json={'title': 'Test Session'})
        assert res.status_code == 201
        assert res.get_json()['data']['session']['title'] == 'Test Session'

    def test_list_sessions_empty(self, client, auth_headers):
        res = client.get('/api/chat/sessions', headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()['data']['sessions'] == []

    def test_get_session(self, client, auth_headers):
        create_res = client.post('/api/chat/sessions', headers=auth_headers, json={'title': 'My Session'})
        session_id = create_res.get_json()['data']['session']['id']
        res = client.get(f'/api/chat/sessions/{session_id}', headers=auth_headers)
        assert res.status_code == 200

    def test_delete_session(self, client, auth_headers):
        create_res = client.post('/api/chat/sessions', headers=auth_headers, json={'title': 'Delete Me'})
        session_id = create_res.get_json()['data']['session']['id']
        res = client.delete(f'/api/chat/sessions/{session_id}', headers=auth_headers)
        assert res.status_code == 200

    def test_session_isolation(self, client, auth_headers):
        """User A cannot access User B's sessions."""
        # Create session as user A
        create_res = client.post('/api/chat/sessions', headers=auth_headers, json={'title': 'Private'})
        session_id = create_res.get_json()['data']['session']['id']

        # Register user B
        client.post('/api/auth/register', json={
            'name': 'User B', 'email': 'userb@test.com', 'password': 'UserB1234'
        })
        login_res = client.post('/api/auth/login', json={
            'email': 'userb@test.com', 'password': 'UserB1234'
        })
        b_token = login_res.get_json()['data']['access_token']
        b_headers = {'Authorization': f'Bearer {b_token}'}

        # User B should NOT see user A's session
        res = client.get(f'/api/chat/sessions/{session_id}', headers=b_headers)
        assert res.status_code == 404

    def test_chat_sessions_require_auth(self, client):
        res = client.get('/api/chat/sessions')
        assert res.status_code == 401


# ─── Dashboard Tests ─────────────────────────────────────────────────────────

class TestDashboard:
    def test_dashboard_returns_stats(self, client, auth_headers):
        res = client.get('/api/dashboard', headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()['data']
        assert 'stats' in data
        assert 'recent_documents' in data
        assert 'recent_sessions' in data

    def test_dashboard_requires_auth(self, client):
        res = client.get('/api/dashboard')
        assert res.status_code == 401
