# app/domain/vehicles/entrypoint/handler
from flask import Blueprint, request
from pydantic import ValidationError

from app.commons.responses import handle_api_response
from app.domain.vehicles.services.vehicle_service import (
    VehicleDTO,
    create_vehicle,
    delete_vehicle,
    get_vehicle,
    update_vehicle,
    VehicleNotFoundError,
)

vehicle_blueprint = Blueprint("vehicles", __name__)


@vehicle_blueprint.route("/", methods=["POST"])
def add_vehicle():
    try:
        vehicle_dto = VehicleDTO(**request.json)
        vehicle = create_vehicle(vehicle_dto)
        return handle_api_response(
            data={"message": "Vehicle created successfully", "id": vehicle.id},
            status_code=201,
        )
    except ValidationError as e:
        return handle_api_response(error={"errors": e.errors()}, status_code=400)


@vehicle_blueprint.route("/<int:vehicle_id>", methods=["GET"])
def retrieve_vehicle(vehicle_id):
    try:
        vehicle_dto = get_vehicle(vehicle_id)
        return handle_api_response(
            data=vehicle_dto.model_dump()
        )  # Updated to use `model_dump`
    except VehicleNotFoundError as e:
        return handle_api_response(error={"message": str(e)}, status_code=404)
    except Exception as e:
        return handle_api_response(error={"errors": str(e)}, status_code=500)


@vehicle_blueprint.route("/<int:vehicle_id>", methods=["PUT"])
def modify_vehicle(vehicle_id):
    try:
        vehicle_dto = VehicleDTO(**request.json)
        vehicle = update_vehicle(vehicle_id, vehicle_dto)
        if vehicle:
            return handle_api_response(data={"message": "Vehicle updated successfully"})
    except ValidationError as e:
        return handle_api_response(error={"errors": e.errors()}, status_code=400)
    return handle_api_response(error={"message": "Vehicle not found"}, status_code=404)


@vehicle_blueprint.route("/<int:vehicle_id>", methods=["DELETE"])
def delete_vehicles(vehicle_id):
    bool_response = delete_vehicle(vehicle_id=vehicle_id)
    if bool_response:
        return handle_api_response(data={"message": "Vehicle deleted successfully"})
    return handle_api_response(error={"message": "Vehicle not found"}, status_code=404)
