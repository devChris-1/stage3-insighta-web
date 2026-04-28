import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client

def test_login_page_loads(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"GitHub" in resp.data

def test_dashboard_redirects_when_not_logged_in(client):
    resp = client.get("/")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]

def test_profiles_redirects_when_not_logged_in(client):
    resp = client.get("/profiles")
    assert resp.status_code == 302

def test_search_redirects_when_not_logged_in(client):
    resp = client.get("/search")
    assert resp.status_code == 302
