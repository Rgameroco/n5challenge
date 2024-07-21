from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

from app.domain.users.models import Person
from app.extensions import db
from app.infrastructure.logger import app_logger

########################################
#             Exceptions               #
########################################


class PersonError(Exception):
    """Base exception class for Person-related errors."""


class PersonCreationError(PersonError):
    """Raised when there is an issue creating a person."""

    def __init__(self, message: str = "Failed to create person"):
        self.message = message
        super().__init__(self.message)


class PersonNotFoundError(PersonError):
    """Raised when the person cannot be found in the database."""

    def __init__(self, person_id: int):
        self.message = f"Person with ID {person_id} not found."
        super().__init__(self.message)


class PersonUpdateError(PersonError):
    """Raised when there is an issue updating a person."""

    def __init__(self, person_id: int, message: str = "Failed to update person"):
        self.message = f"{message} with ID {person_id}"
        super().__init__(self.message)


class PersonDeletionError(PersonError):
    """Raised when there is an issue deleting a person."""

    def __init__(self, person_id: int):
        self.message = f"Failed to delete person with ID {person_id}"
        super().__init__(self.message)


########################################
#                 DTOs                 #
########################################


class PersonDTO(BaseModel):
    name: str = Field(..., min_length=1, strip_whitespace=True)
    email: EmailStr


########################################
#               Services               #
########################################


def create_person(person_dto: PersonDTO) -> Person:
    try:
        new_person = Person(name=person_dto.name, email=person_dto.email)
        db.session.add(new_person)
        db.session.commit()
        return new_person
    except SQLAlchemyError as e:
        app_logger.error(f"Error creating person: {e}")
        raise PersonCreationError()


def get_person(person_id: int) -> Optional[Person]:
    person = Person.query.get(person_id)
    if not person:
        app_logger.warning(f"Person with ID {person_id} not found.")
        raise PersonNotFoundError(person_id)
    return person


def update_person(
    person_id: int, name: Optional[str] = None, email: Optional[str] = None
) -> Optional[Person]:
    try:
        person = Person.query.get(person_id)
        if not person:
            raise PersonNotFoundError(person_id)
        if name is not None and name != person.name:
            person.name = name
        if email is not None and email != person.email:
            person.email = email
        db.session.commit()
        return person
    except SQLAlchemyError as e:
        app_logger.error(f"Error updating person with ID {person_id}: {e}")
        raise PersonUpdateError(person_id)


def delete_person(person_id: int) -> bool:
    try:
        person = Person.query.get(person_id)
        if not person:
            raise PersonNotFoundError(person_id)
        db.session.delete(person)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        app_logger.error(f"Error deleting person with ID {person_id}: {e}")
        raise PersonDeletionError(person_id)
