from typing import Optional

from flask_jwt_extended import create_access_token
from pydantic import BaseModel, Field
from werkzeug.security import check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from app.domain.users.models import Officer
from app.extensions import db
from app.infrastructure.logger import app_logger

########################################
#             Exceptions               #
########################################


class OfficerError(Exception):
    """Base class for officer-related exceptions."""

    pass


class OfficerNotFoundError(OfficerError):
    """Exception raised when an officer cannot be found."""

    def __init__(self, officer_id):
        self.message = f"Officer with ID {officer_id} not found."
        super().__init__(self.message)


class OfficerCreationError(OfficerError):
    """Exception raised when an officer cannot be created."""

    def __init__(self, reason):
        self.message = f"Failed to create officer: {reason}"
        super().__init__(self.message)


class OfficerUpdateError(OfficerError):
    """Exception raised when an officer cannot be updated."""

    def __init__(self, officer_id, reason):
        self.message = f"Failed to update officer with ID {officer_id}: {reason}"
        super().__init__(self.message)


class OfficerDeletionError(OfficerError):
    """Exception raised when an officer cannot be deleted."""

    def __init__(self, officer_id, reason):
        self.message = f"Failed to delete officer with ID {officer_id}: {reason}"
        super().__init__(self.message)


class AuthenticationError(OfficerError):
    """Exception raised during authentication failures."""

    def __init__(self, identifier):
        self.message = (
            f"Authentication failed for officer with identifier {identifier}."
        )
        super().__init__(self.message)


########################################
#                  DTO                 #
########################################


class OfficerDTO(BaseModel):
    name: Optional[str] = Field(
        None, min_length=1, strip_whitespace=True, description="Name of the officer."
    )
    unique_identifier: Optional[str] = Field(
        None,
        min_length=1,
        strip_whitespace=True,
        description="Unique identifier for the officer.",
    )
    password: Optional[str] = Field(
        None,
        min_length=6,
        description="Password for the officer account.",
        example="securepassword123",
    )


class OfficerResponseDTO(BaseModel):
    name: str = Field(..., description="Name of the officer.")
    unique_identifier: str = Field(
        ..., description="Unique identifier for the officer."
    )

    class Config:
        orm_mode = True
        from_attributes = True


########################################
#                Services              #
########################################


def create_officer(officer_dto: OfficerDTO) -> int:
    """
    Creates a new officer record in the database using the provided officer data transfer object (DTO).

    Args:
        officer_dto (OfficerDTO): The data transfer object containing all required fields to create an officer.

    Returns:
        int: The ID of the newly created officer, indicating successful creation.
    """
    try:
        officer = Officer(
            name=officer_dto.name, unique_identifier=officer_dto.unique_identifier
        )
        officer.set_password(officer_dto.password)
        db.session.add(officer)
        db.session.commit()
        app_logger.info(
            f"Officer created successfully with ID: {officer.unique_identifier}"
        )
        return officer.id
    except Exception as e:
        app_logger.error(f"Failed to create officer: {e}")
        raise OfficerCreationError(reason=str(e))


def update_officer(officer_id: int, officer_dto: OfficerDTO) -> Optional[int]:
    """
    Updates an existing officer record identified by the officer_id with the details provided in the officer DTO.
    Only the fields provided in the DTO will be updated.

    Args:
        officer_id (int): The unique identifier of the officer to update.
        officer_dto (OfficerDTO): Data Transfer Object containing updated details for the officer.

    Returns:
        Optional[int]: The ID of the updated officer if the update was successful, or None if no officer was found.
    """
    try:
        officer = Officer.query.get(officer_id)
        if not officer:
            raise OfficerNotFoundError(officer_id)

        # Actualizar solo los campos proporcionados en el DTO
        for key, value in officer_dto.dict(exclude_unset=True).items():
            if hasattr(officer, key) and getattr(officer, key) != value:
                setattr(officer, key, value)

        # Si se proporciona una contraseña nueva, actualizarla también
        if "password" in officer_dto.dict(exclude_unset=True):
            officer.set_password(officer_dto.password)

        db.session.commit()
        return officer.id
    except OfficerNotFoundError as e:
        app_logger.warning(e.message)
        raise
    except Exception as e:
        app_logger.error(f"Failed to update officer with ID {officer_id}: {e}")
        raise OfficerUpdateError(officer_id, reason=str(e))


def get_officer_by_id(officer_id: int) -> Optional[OfficerResponseDTO]:
    """
    Retrieves the details of an officer by their unique identifier, excluding sensitive information like password.

    Args:
        officer_id (int): The unique identifier of the officer to retrieve.

    Returns:
        Optional[OfficerResponseDTO]: An officer response DTO containing non-sensitive data if the officer exists, otherwise None.
    """
    try:
        officer = Officer.query.get(officer_id)
        if not officer:
            raise OfficerNotFoundError(officer_id)
        officer_dto = OfficerResponseDTO.model_validate(officer)
        return officer_dto
    except OfficerNotFoundError as e:
        app_logger.warning(e.message)
        raise
    except Exception as e:
        app_logger.error(f"Failed to retrieve officer with ID {officer_id}: {e}")
        raise OfficerError(f"An error occurred while retrieving officer: {e}")


def delete_officer(officer_id: int) -> bool:
    """
    Deletes an officer record from the database based on the officer's unique identifier.

    Args:
        officer_id (int): The unique identifier of the officer to be deleted.

    Returns:
        None: Indicates successful deletion of the officer.
    """
    try:
        officer = Officer.query.get(officer_id)
        if not officer:
            raise OfficerNotFoundError(officer_id)
        db.session.delete(officer)
        db.session.commit()
        return True
    except OfficerNotFoundError as e:
        app_logger.warning(e.message)
        raise
    except Exception as e:
        app_logger.error(f"Failed to delete officer with ID {officer_id}: {e}")
        raise OfficerDeletionError(officer_id, reason=str(e))


def authenticate_officer(unique_identifier: str, password: str) -> Optional[str]:
    """
    Authenticates an officer using their unique identifier and password.

    Args:
        unique_identifier (str): The unique identifier of the officer.
        password (str): The password for the officer.

    Returns:
        Optional[str]: Returns a JWT access token if authentication is successful, otherwise None.
    """
    try:
        officer = Officer.query.filter_by(unique_identifier=unique_identifier).first()
        if not officer or not check_password_hash(officer.password_hash, password):
            raise AuthenticationError(unique_identifier)
        return create_access_token(identity=unique_identifier)
    except AuthenticationError as e:
        app_logger.warning(e.message)
        raise
    except Exception as e:
        app_logger.error(f"Authentication error for officer {unique_identifier}: {e}")
        raise AuthenticationError(unique_identifier)


def get_officer_by_unique_identifier(
    unique_identifier: str,
) -> Optional[Officer]:
    """
    Retrieves the details of an officer by their unique identifier, excluding sensitive information like password.

    Args:
        unique_identifier (str): The unique identifier of the officer to retrieve.

    Returns:
        Optional[Officer]: An officer response DTO containing non-sensitive data if the officer exists, otherwise None.
    """
    try:
        officer = Officer.query.filter_by(unique_identifier=unique_identifier).first()
        if not officer:
            raise OfficerNotFoundError(unique_identifier)
        return officer
    except OfficerNotFoundError as e:
        app_logger.warning(e.message)
        raise
    except Exception as e:
        app_logger.error(
            f"Failed to retrieve officer with unique identifier {unique_identifier}: {e}"
        )
        raise OfficerError(f"An error occurred while retrieving officer: {e}")
