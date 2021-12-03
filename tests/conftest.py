import pytest
from app import app as flask_app
from application import db
from application.models import User
from datetime import datetime as dt
from werkzeug.security import generate_password_hash
from flask import session
import json


@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def populate_users():
    users = [
        {
            "email": "user_1@example.com",
            "password": "Password1234!",
        },
        {
            "email": "user_2@example.com",
            "password": "Password567890!",
        },
    ]
    for user in users:
        try:
            db.session.add(
                User(
                    email=user["email"],
                    password_hash=generate_password_hash(user["password"]),
                    created=dt.utcnow(),
                )
            )
            db.session.commit()
        except:
            db.session.rollback()


@pytest.fixture
def client(app):
    print(app.static_url_path)
    yield app.test_client()

@pytest.fixture
def fake_login(client, request):
    with client.session_transaction() as sess:
        try:
            sess["user_id"] = request.param
        except:
            sess["user_id"] = 1