# app/domain/infractions/adapters/vehicle_adapter.py
from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel

from app.domain.vehicles.services.vehicle_service import get_vehicle_by_license_plate


class VehicleDTO(BaseModel):
    id: str
    license_plate: str
    make: str
    model: str
    color: str
    owner_id: int


class BaseVehicleAdapter(ABC):
    @abstractmethod
    def get_vehicle(self, license_plate: str) -> VehicleDTO:
        pass


class VehicleAdapter(BaseVehicleAdapter):
    @staticmethod
    def get_vehicle(license_plate: str) -> Optional[VehicleDTO]:
        """
        Retrieve a vehicle by its license plate through the vehicle service.

        Args:
            license_plate (str): License plate of the vehicle to find.

        Returns:
            An instance of the Vehicle model or None if the vehicle is not found.
        """
        vehicle_obj = get_vehicle_by_license_plate(license_plate)

        if vehicle_obj is None:
            return None

        return VehicleDTO(
            id=str(vehicle_obj.id),
            license_plate=vehicle_obj.license_plate,
            make=vehicle_obj.make,
            model=vehicle_obj.model,
            color=vehicle_obj.color,
            owner_id=vehicle_obj.owner_id,
        )


class FakeVehicleAdapter(BaseVehicleAdapter):
    def get_vehicle(self, license_plate: str) -> VehicleDTO:
        return VehicleDTO(
            license_plate=license_plate, make="Test", model="Car", color="Blue"
        )
