from datetime import datetime
from typing import Dict, Optional, Tuple, Any

from pydantic import BaseModel, Field, field_validator

from app.domain.infractions.adapters.person_adapter import BasePersonAdapter
from app.domain.infractions.adapters.vehicle_adapter import BaseVehicleAdapter
from app.domain.infractions.adapters.officer_adapter import BaseOfficerAdapter
from app.domain.infractions.models import Infraction
from app.extensions import db
from app.infrastructure.logger import app_logger

########################################
#             Exceptions               #
########################################


class InfractionError(Exception):
    """Base class for infraction-related exceptions."""


class InfractionNotFoundError(InfractionError):
    """Exception raised when an infraction is not found."""

    def __init__(self, infraction_id):
        super().__init__(f"Infraction with ID {infraction_id} not found.")


class InfractionCreationError(InfractionError):
    """Exception raised when an infraction cannot be created."""

    def __init__(self, reason):
        super().__init__(f"Failed to create infraction: {reason}")


class InfractionUpdateError(InfractionError):
    """Exception raised when an infraction cannot be updated."""

    def __init__(self, infraction_id, reason):
        super().__init__(
            f"Failed to update infraction with ID {infraction_id}: {reason}"
        )


class InfractionDeletionError(InfractionError):
    """Exception raised when an infraction cannot be deleted."""

    def __init__(self, infraction_id, reason):
        super().__init__(
            f"Failed to delete infraction with ID {infraction_id}: {reason}"
        )


########################################
#                  DTO                 #
########################################


class InfractionDTO(BaseModel):
    license_plate: str = Field(alias="placa_patente")
    timestamp: datetime
    comments: Optional[str] = Field(alias="comentarios")
    officer_unique_identifier: str

    @field_validator("timestamp")
    def validate_timestamp(cls, value):
        today = datetime.now().date()
        if value.date() != today:
            raise ValueError("El timestamp debe ser del día de hoy.")
        return value


class VehicleResponseDTO(BaseModel):
    license_plate: str
    make: str
    model: str
    color: Optional[str]
    owner_id: int


class OfficerResponseDTO(BaseModel):
    id: int
    name: str
    unique_identifier: str


class InfractionResponseDTO(BaseModel):
    license_plate: str
    timestamp: datetime
    comments: Optional[str]
    vehicle: VehicleResponseDTO
    officer: OfficerResponseDTO


########################################
#                Services              #
########################################


def create_infraction(
    infraction_dto: InfractionDTO,
    vehicle_adapter: BaseVehicleAdapter,
    officer_adapter: BaseOfficerAdapter,
) -> Tuple[Dict[str, str], int]:
    vehicle = vehicle_adapter.get_vehicle(license_plate=infraction_dto.license_plate)
    if not vehicle:
        app_logger.error("Vehicle not found during infraction creation")
        raise InfractionCreationError(
            "Vehicle not found, please register the vehicle first"
        )

    officer = officer_adapter.get_officer(
        unique_identifier=infraction_dto.officer_unique_identifier
    )
    if not officer:
        app_logger.error("Officer not found during infraction creation")
        raise InfractionCreationError(
            "Officer not found, please create the officer first"
        )

    try:
        new_infraction = Infraction(
            license_plate=vehicle.license_plate,
            timestamp=infraction_dto.timestamp,
            comments=infraction_dto.comments,
            officer_id=officer.id,
        )
        db.session.add(new_infraction)
        db.session.commit()
        app_logger.info("Infraction created successfully")
        return {"message": "Infraction logged successfully"}, 200
    except Exception as e:
        app_logger.error(f"Failed to log infraction: {e}")
        raise InfractionCreationError(str(e))


def get_infraction(infraction_id: int) -> InfractionResponseDTO:

    infraction = Infraction.query.get(infraction_id)
    if not infraction:
        app_logger.error(f"Infraction not found: ID {infraction_id}")
        raise InfractionNotFoundError(infraction_id)

    vehicle_dto = VehicleResponseDTO(
        license_plate=infraction.vehicle.license_plate,
        make=infraction.vehicle.make,
        model=infraction.vehicle.model,
        color=infraction.vehicle.color,
        owner_id=infraction.vehicle.owner_id,
    )

    officer_dto = OfficerResponseDTO(
        id=infraction.officer.id,
        name=infraction.officer.name,
        unique_identifier=infraction.officer.unique_identifier,
    )
    app_logger.info(infraction.license_plate)
    return InfractionResponseDTO(
        license_plate=infraction.license_plate,
        timestamp=infraction.timestamp,
        comments=infraction.comments,
        vehicle=vehicle_dto,
        officer=officer_dto,
    )


def update_infraction(
    infraction_id: int, infraction_dto: InfractionDTO
) -> Optional[Infraction]:
    infraction = Infraction.query.get(infraction_id)
    if not infraction:
        app_logger.error(f"Infraction not found for update: ID {infraction_id}")
        raise InfractionNotFoundError(infraction_id)
    try:
        infraction.license_plate = infraction_dto.license_plate
        infraction.timestamp = infraction_dto.timestamp
        infraction.comments = infraction_dto.comments
        db.session.commit()
        return infraction
    except Exception as e:
        app_logger.error(f"Failed to update infraction: ID {infraction_id}, Error: {e}")
        raise InfractionUpdateError(infraction_id, str(e))


def delete_infraction(infraction_id: int) -> bool:
    infraction = Infraction.query.get(infraction_id)
    if not infraction:
        app_logger.error(f"Infraction not found for deletion: ID {infraction_id}")
        raise InfractionNotFoundError(infraction_id)
    try:
        db.session.delete(infraction)
        db.session.commit()
        return True
    except Exception as e:
        app_logger.error(f"Failed to delete infraction: ID {infraction_id}, Error: {e}")
        raise InfractionDeletionError(infraction_id, str(e))


def generate_report(email: str, person_adapter: BasePersonAdapter) -> Dict[str, Any]:
    """
    Generates a report of all infractions for vehicles owned by the person with the given email.

    Args:
        email (str): Email address of the person to retrieve infractions for.
        person_adapter (BasePersonAdapter): Adapter to retrieve person and vehicle data.

    Returns:
        Dict[str, Any]: A dictionary containing the person's details and a list of their infractions.
    """
    try:
        person = person_adapter.get_person_by_email(email)
        if not person:
            app_logger.error(f"No person found with email: {email}")
            return {"error": "No person found with this email."}

        infractions = []
        for vehicle in person.vehicles:
            vehicle_infractions = Infraction.query.filter_by(
                license_plate=vehicle.license_plate
            ).all()
            for infraction in vehicle_infractions:
                infractions.append(
                    {
                        "license_plate": vehicle.license_plate,
                        "timestamp": infraction.timestamp,
                        "comments": infraction.comments,
                    }
                )

        if not infractions:
            app_logger.info(
                f"No infractions found for vehicles owned by the person with email: {email}"
            )
            return {"message": "No infractions found for this person's vehicles."}

        report = {
            "person": {
                "name": person.name,
                "email": person.email,
            },
            "infractions": infractions,
        }

        app_logger.info(f"Report generated for person with email: {email}")
        return report

    except Exception as e:
        app_logger.error(f"Failed to generate report for email {email}: {e}")
        return {"error": "Failed to generate report due to an internal error."}
