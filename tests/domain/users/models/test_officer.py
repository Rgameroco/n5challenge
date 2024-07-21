import uuid

import pytest

from app.domain.users.models import Officer, Person
from tests.conftest import db


def test_create_officer(db):
    """Test creating an officer and saving it to the database."""
    unique_id = str(uuid.uuid4())
    officer = Officer(name="Jane Doe", unique_identifier=unique_id)
    db.session.add(officer)
    db.session.commit()
    assert Officer.query.count() == 1
    assert Officer.query.first().name == "Jane Doe"


def test_officer_representation(db):
    """Test the string representation of the Officer model."""
    unique_id = str(uuid.uuid4())
    officer = Officer(name="Jane Doe", unique_identifier=unique_id)
    db.session.add(officer)
    db.session.commit()
    assert str(officer) == "<Officer Jane Doe>"
