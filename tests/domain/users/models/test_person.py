# tests/domain/users/test_users.py
import pytest

from app.domain.users.models import Officer, Person
from app.domain.vehicles.models import Vehicle
from tests.conftest import db


def test_create_person(db):
    """Test creating a person and saving it to the database."""
    # Crear primero el vehículo
    vehicle = Vehicle(
        license_plate="ABC123", make="Toyota", model="Corolla", color="Red"
    )

    # Crear la persona y asignarle el vehículo creado
    person = Person(name="John Doe", email="john.doe@example.com", vehicles=[vehicle])

    # Añadir la persona y el vehículo a la sesión de la base de datos
    db.session.add(person)
    db.session.commit()

    # Asegurarse de que hay exactamente una persona en la base de datos
    assert Person.query.count() == 1
    # Asegurarse de que el nombre de la persona guardada es correcto
    assert Person.query.first().name == "John Doe"
    # Asegurarse de que la persona tiene exactamente un vehículo y es el correcto
    assert len(Person.query.first().vehicles) == 1
    assert Person.query.first().vehicles[0].license_plate == "ABC123"


def test_person_representation(db):
    """Test the string representation of the Person model."""
    person = Person(name="John Doe", email="john.doe@example.com")
    db.session.add(person)
    db.session.commit()
    assert str(person) == "<Person John Doe>"
