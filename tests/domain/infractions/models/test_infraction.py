from datetime import datetime, timezone

import pytest

from app.domain.infractions.models import Infraction
from app.domain.users.models import Officer
from app.domain.vehicles.models import Vehicle


@pytest.fixture
def sample_vehicle(db):
    vehicle = Vehicle(
        license_plate="ABC123", make="Toyota", model="Corolla", color="Blue"
    )
    db.session.add(vehicle)
    db.session.commit()
    return vehicle


@pytest.fixture
def sample_officer(db):
    officer = Officer(name="Officer Jane", unique_identifier="XYZ789")
    db.session.add(officer)
    db.session.commit()
    return officer


def test_create_infraction(db, sample_vehicle, sample_officer):
    """Test creating an infraction and saving it to the database."""
    timestamp = datetime.now(timezone.utc)  # timezone-aware UTC datetime
    infraction = Infraction(
        license_plate=sample_vehicle.license_plate,
        timestamp=timestamp,
        comments="Speeding in a school zone",
        officer_id=sample_officer.id,
    )
    db.session.add(infraction)
    db.session.commit()
    assert Infraction.query.count() == 1
    assert Infraction.query.first().comments == "Speeding in a school zone"


def test_infraction_relationships(db, sample_vehicle, sample_officer):
    """Test the relationships of Infraction to Vehicle and Officer."""
    infraction = Infraction(
        license_plate=sample_vehicle.license_plate,
        timestamp=datetime.now(timezone.utc),
        comments="Parking violation",
        officer_id=sample_officer.id,
    )
    db.session.add(infraction)
    db.session.commit()

    # Fetch the infraction back from the database
    retrieved_infraction = Infraction.query.first()

    # Validate relationships
    assert retrieved_infraction.vehicle == sample_vehicle
    assert retrieved_infraction.officer == sample_officer
    assert sample_vehicle.infractions.count() == 1
    assert sample_officer.infractions.count() == 1


def test_infraction_representation(db, sample_vehicle, sample_officer):
    """Test the string representation of the Infraction model."""
    infraction = Infraction(
        license_plate=sample_vehicle.license_plate,
        timestamp=datetime.now(timezone.utc),
        comments="No seat belt",
        officer_id=sample_officer.id,
    )
    db.session.add(infraction)
    db.session.commit()
    retrieved_infraction = Infraction.query.first()
    assert str(retrieved_infraction).startswith("<Infraction ")
