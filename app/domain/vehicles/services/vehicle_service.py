from typing import Optional

from pydantic import BaseModel, Field

from app.domain.vehicles.models import Vehicle
from app.extensions import db
from app.infrastructure.logger import app_logger
from sqlalchemy.exc import SQLAlchemyError

########################################
#             Exceptions               #
########################################


class VehicleError(Exception):
    """Base class for vehicle-related exceptions."""


class VehicleNotFoundError(VehicleError):
    """Exception raised when a vehicle cannot be found."""

    def __init__(self, vehicle_id=None, license_plate=None):
        if vehicle_id:
            self.message = f"Vehicle with ID {vehicle_id} not found."
        elif license_plate:
            self.message = f"Vehicle with license plate {license_plate} not found."
        else:
            self.message = "Vehicle not found."
        super().__init__(self.message)


class VehicleCreationError(VehicleError):
    """Exception raised when there is a problem creating a vehicle."""

    def __init__(self, reason="Unknown reason"):
        self.message = f"Failed to create vehicle: {reason}"
        super().__init__(self.message)


class VehicleUpdateError(VehicleError):
    """Exception raised when there is a problem updating a vehicle."""

    def __init__(self, vehicle_id, reason="Unknown reason"):
        self.message = f"Failed to update vehicle with ID {vehicle_id}: {reason}"
        super().__init__(self.message)


class VehicleDeletionError(VehicleError):
    """Exception raised when there is a problem deleting a vehicle."""

    def __init__(self, vehicle_id):
        self.message = f"Failed to delete vehicle with ID {vehicle_id}"
        super().__init__(self.message)


########################################
#                 DTOs                 #
########################################


class VehicleDTO(BaseModel):
    license_plate: str = Field(..., min_length=1, strip_whitespace=True)
    make: str = Field(..., min_length=1, strip_whitespace=True)
    model: str = Field(..., min_length=1, strip_whitespace=True)
    color: str = Field(..., min_length=1, strip_whitespace=True)
    owner_id: Optional[int] = Field(...)


class VehicleUpdateDTO(BaseModel):
    license_plate: Optional[str] = Field(None, min_length=1, strip_whitespace=True)
    make: Optional[str] = Field(None, min_length=1, strip_whitespace=True)
    model: Optional[str] = Field(None, min_length=1, strip_whitespace=True)
    color: Optional[str] = Field(None, min_length=1, strip_whitespace=True)
    owner_id: Optional[int] = None


class VehicleResponseDTO(BaseModel):
    license_plate: Optional[str] = Field(None, min_length=1, strip_whitespace=True)
    make: Optional[str] = Field(None, min_length=1, strip_whitespace=True)
    model: Optional[str] = Field(None, min_length=1, strip_whitespace=True)
    color: Optional[str] = Field(None, min_length=1, strip_whitespace=True)
    owner_id: Optional[int] = None


########################################
#               Services               #
########################################


def create_vehicle(vehicle_dto: VehicleDTO) -> Vehicle:
    """
    Create a new vehicle in the database using the provided VehicleDTO.

    Args:
        vehicle_dto (VehicleDTO): Data transfer object containing all the necessary vehicle details.

    Returns:
        Vehicle: The newly created Vehicle object.

    Raises:
        VehicleCreationError: If there is any database error during vehicle creation.
    """
    try:
        vehicle = Vehicle(**vehicle_dto.dict())
        db.session.add(vehicle)
        db.session.commit()
        app_logger.info(
            f"Vehicle created successfully with license plate: {vehicle.license_plate}"
        )
        return vehicle
    except SQLAlchemyError as e:
        app_logger.error(f"Error creating vehicle: {e}")
        raise VehicleCreationError(reason=str(e))


def update_vehicle(vehicle_id: int, vehicle_dto: VehicleUpdateDTO) -> Optional[Vehicle]:
    """
    Update an existing vehicle's details in the database.

    Args:
        vehicle_id (int): The ID of the vehicle to update.
        vehicle_dto (VehicleUpdateDTO): Data transfer object containing the updated vehicle details.

    Returns:
        Optional[Vehicle]: The updated Vehicle object, or None if the vehicle does not exist.

    Raises:
        VehicleNotFoundError: If no vehicle with the specified ID was found.
        VehicleUpdateError: If there is an error during the update process.
    """
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        app_logger.warning(f"Vehicle with ID {vehicle_id} not found for update.")
        raise VehicleNotFoundError(vehicle_id=vehicle_id)
    try:
        update_data = vehicle_dto.dict(exclude_unset=True, exclude_none=True)
        for key, value in update_data.items():
            setattr(vehicle, key, value)
        db.session.commit()
        app_logger.info(f"Vehicle with ID {vehicle_id} updated successfully.")
        return vehicle
    except SQLAlchemyError as e:
        app_logger.error(f"Error updating vehicle with ID {vehicle_id}: {e}")
        raise VehicleUpdateError(vehicle_id, reason=str(e))


def delete_vehicle(vehicle_id: int) -> bool:
    """
    Delete a vehicle from the database.

    Args:
        vehicle_id (int): The ID of the vehicle to delete.

    Returns:
        bool: True if the vehicle was successfully deleted, False otherwise.

    Raises:
        VehicleNotFoundError: If the vehicle cannot be found.
        VehicleDeletionError: If there is a problem during the deletion process.
    """
    app_logger.info(f"Vehicle with ID {vehicle_id}.")
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        app_logger.warning(f"Vehicle with ID {vehicle_id} not found for deletion.")
        raise VehicleNotFoundError(vehicle_id=vehicle_id)
    try:
        db.session.delete(vehicle)
        db.session.commit()
        app_logger.info(f"Vehicle with ID {vehicle_id} deleted successfully.")
        return True
    except SQLAlchemyError as e:
        app_logger.error(f"Error deleting vehicle with ID {vehicle_id}: {e}")
        raise VehicleDeletionError(vehicle_id)


def get_vehicle(vehicle_id: int) -> Optional[VehicleResponseDTO]:
    """
    Retrieve a vehicle by its ID from the database.

    Args:
        vehicle_id (int): The ID of the vehicle to retrieve.

    Returns:
        Optional[Vehicle]: The retrieved Vehicle object, or None if the vehicle does not exist.

    Raises:
        VehicleNotFoundError: If no vehicle with the specified ID was found.
    """
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        app_logger.info(f"Attempted to retrieve non-existent vehicle ID: {vehicle_id}")
        raise VehicleNotFoundError(vehicle_id=vehicle_id)

    vehicle_dto = VehicleResponseDTO(
        license_plate=vehicle.license_plate,
        make=vehicle.make,
        model=vehicle.model,
        color=vehicle.color,
        owner_id=vehicle.owner_id,
    )
    return vehicle_dto


def get_vehicle_by_license_plate(license_plate: str) -> Vehicle:
    """
    Retrieve a vehicle by its license plate from the database.

    Args:
        license_plate (str): The license plate of the vehicle to retrieve.

    Returns:
        Vehicle: The vehicle object if found, raises an error otherwise.

    Raises:
        VehicleNotFoundError: If no vehicle with the specified license plate is found.
    """
    vehicle = Vehicle.query.filter_by(license_plate=license_plate).first()
    if not vehicle:
        app_logger.info(f"Vehicle with license plate {license_plate} not found.")
        raise VehicleNotFoundError(license_plate=license_plate)
    return vehicle
