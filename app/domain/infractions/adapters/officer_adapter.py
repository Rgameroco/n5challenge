# app/domain/infractions/adapters/vehicle_adapter.py
from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel

from app.domain.users.services.officer_service import get_officer_by_unique_identifier
from app.infrastructure.logger import app_logger


class OfficerDTO(BaseModel):
    id: int
    name: str
    unique_identifier: str


class BaseOfficerAdapter(ABC):
    @abstractmethod
    def get_officer(self, unique_identifier: str) -> OfficerDTO:
        pass


class OfficerAdapter(BaseOfficerAdapter):
    @staticmethod
    def get_officer(unique_identifier: str) -> Optional[OfficerDTO]:
        """
        Retrieve an officer by their unique identifier.

        Args:
            unique_identifier (str): Unique identifier of the officer to find.

        Returns:
            An instance of OfficerDTO if the officer is found, otherwise None.
        """
        officer = get_officer_by_unique_identifier(unique_identifier=unique_identifier)
        if officer:
            app_logger.info("officer is True")
            return OfficerDTO(
                id=officer.id,
                name=officer.name,
                unique_identifier=officer.unique_identifier,
            )
        return None


class FakeOfficerAdapter(BaseOfficerAdapter):
    def get_officer(self, unique_identifier: str) -> OfficerDTO:
        """
        Simulate retrieving an officer using their unique identifier.
        """
        return OfficerDTO(id=1, name="John Doe", unique_identifier=unique_identifier)
