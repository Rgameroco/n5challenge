from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.users.services.person_services import get_person_by_email
from app.infrastructure.logger import app_logger
from pydantic import BaseModel, EmailStr, Field


class NoVehiclesFoundError(Exception):
    """Exception raised when no vehicles are associated with a retrieved person."""

    def __init__(self, person_id: str):
        message = f"No vehicles found for person with ID: {person_id}"
        super().__init__(message)


class VehicleDTO(BaseModel):
    license_plate: str = Field(..., description="The vehicle's license plate.")
    make: str = Field(..., description="The make of the vehicle.")
    model: str = Field(..., description="The model of the vehicle.")
    color: str = Field(..., description="The color of the vehicle.")


class PersonDTO(BaseModel):
    name: str = Field(..., description="The full name of the person.")
    email: EmailStr = Field(..., description="The email address of the person.")
    vehicles: List[VehicleDTO] = Field(
        default=[], description="List of vehicles associated with the person."
    )


class BasePersonAdapter(ABC):
    @abstractmethod
    def get_person_by_email(self, email: str) -> Optional[PersonDTO]:
        """Retrieve a person by their email address and return a PersonDTO."""
        pass


class PersonAdapter(BasePersonAdapter):
    def get_person_by_email(self, email: str) -> Optional[PersonDTO]:
        """
        Retrieves a person by their email address from the database and returns a PersonDTO.
        Args:
            email (str): The email address of the person to retrieve.
        Returns:
            Optional[PersonDTO]: The retrieved person DTO if found; None otherwise.
        """
        person = get_person_by_email(email=email)
        if not person:
            app_logger.warning(f"No person found with email: {email}")
            return None

        app_logger.info(f"{person.model_dump()}")
        if not person.vehicles:
            app_logger.error(f"No vehicles found for person with email: {email}")
            raise NoVehiclesFoundError(person_id=person.id)

        person_dto = PersonDTO(
            name=person.name,
            email=person.email,
            vehicles=[
                VehicleDTO(
                    license_plate=v.license_plate,
                    make=v.make,
                    model=v.model,
                    color=v.color,
                )
                for v in person.vehicles
            ],
        )
        app_logger.info(f"Person with email {email} retrieved successfully.")
        return person_dto
