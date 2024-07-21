# tests/test_domain/vehicles/test_models.py
import pytest
from sqlalchemy.exc import IntegrityError

from app.domain.vehicles.models import Vehicle
from tests.conftest import db


def test_create_vehicle(db):
    """Test creating a new Vehicle instance."""
    vehicle = Vehicle(
        license_plate="123ABC", make="Toyota", model="Corolla", color="Blue", owner_id=1
    )
    db.session.add(vehicle)
    db.session.commit()
    assert Vehicle.query.count() == 1
    assert Vehicle.query.first().license_plate == "123ABC"


def test_vehicle_license_plate_uniqueness(db):
    """Test that the license plate must be unique."""
    vehicle1 = Vehicle(
        license_plate="UNIQUE123",
        make="Toyota",
        model="Corolla",
        color="Green",
        owner_id=1,
    )
    db.session.add(vehicle1)
    db.session.commit()

    vehicle2 = Vehicle(
        license_plate="UNIQUE123", make="Honda", model="Civic", color="Red", owner_id=2
    )
    db.session.add(vehicle2)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_vehicle_representation(db):
    """Test the string representation of the Vehicle model."""
    vehicle = Vehicle(
        license_plate="123ABC", make="Toyota", model="Corolla", color="Blue", owner_id=1
    )
    db.session.add(vehicle)
    db.session.commit()
    assert str(vehicle) == "<Vehicle 123ABC - Toyota Corolla>"
