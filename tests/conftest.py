# tests/conftest.py
import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.extensions import db as _db  # Asegúrate de que esta importación es correcta


@pytest.fixture(scope="module")
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    _db.init_app(app)
    with app.app_context():
        _db.create_all()
    yield app


@pytest.fixture(scope="function")
def db(app):
    """Fixture that provides a database setup for tests."""
    _db.app = app
    connection = _db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    session = _db.create_scoped_session(options=options)

    _db.session = session

    yield _db

    session.remove()
    transaction.rollback()
    connection.close()
