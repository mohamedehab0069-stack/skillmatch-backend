import pytest
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"

def test_register_missing_fields(client):
    r = client.post("/api/auth/register",
                    data=json.dumps({"email": "test@test.com"}),
                    content_type="application/json")
    assert r.status_code == 400
    assert r.get_json()["success"] is False

def test_register_invalid_email(client):
    r = client.post("/api/auth/register",
                    data=json.dumps({
                        "name": "Test", "email": "not-an-email",
                        "password": "Test1234", "role": "student"
                    }),
                    content_type="application/json")
    assert r.status_code == 400

def test_register_weak_password(client):
    r = client.post("/api/auth/register",
                    data=json.dumps({
                        "name": "Test", "email": "test@example.com",
                        "password": "abc", "role": "student"
                    }),
                    content_type="application/json")
    assert r.status_code == 400

def test_register_invalid_role(client):
    r = client.post("/api/auth/register",
                    data=json.dumps({
                        "name": "Test", "email": "test@example.com",
                        "password": "Test1234", "role": "superuser"
                    }),
                    content_type="application/json")
    assert r.status_code == 400

def test_login_no_user(client):
    r = client.post("/api/auth/login",
                    data=json.dumps({
                        "email": "nobody@example.com", "password": "Test1234"
                    }),
                    content_type="application/json")
    assert r.status_code == 401

def test_me_no_token(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401
