from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from app.commons.responses import handle_api_response
from app.domain.infractions.adapters.vehicle_adapter import VehicleAdapter
from app.domain.infractions.adapters.officer_adapter import OfficerAdapter
from app.domain.infractions.adapters.person_adapter import PersonAdapter
from app.domain.infractions.services.infraction_service import (
    InfractionDTO,
    create_infraction,
    delete_infraction,
    get_infraction,
    update_infraction,
    generate_report,
    InfractionNotFoundError,
    InfractionCreationError,
    InfractionDeletionError,
    InfractionUpdateError,
)

infraction_blueprint = Blueprint("infractions", __name__)


@infraction_blueprint.route("/recording_infraction", methods=["POST"])
@jwt_required()
def add_infraction():
    try:
        infraction_dto = InfractionDTO(**request.json)
        vehicle_adapter = VehicleAdapter()
        officer_adapter = OfficerAdapter()
        message, status_code = create_infraction(
            infraction_dto=infraction_dto,
            vehicle_adapter=vehicle_adapter,
            officer_adapter=officer_adapter,
        )
        return handle_api_response(data={"message": message}, status_code=status_code)
    except ValidationError as e:
        return handle_api_response(error={"errors": str(e)}, status_code=400)
    except InfractionCreationError as e:
        return handle_api_response(error={"message": str(e)}, status_code=404)


@infraction_blueprint.route("/<int:infraction_id>", methods=["GET"])
@jwt_required()
def retrieve_infraction(infraction_id):
    try:
        infraction = get_infraction(infraction_id)
        return handle_api_response(data=infraction.dict())
    except InfractionNotFoundError as e:
        return handle_api_response(error={"message": str(e)}, status_code=404)


@infraction_blueprint.route("/<int:infraction_id>", methods=["PUT"])
@jwt_required()
def modify_infraction(infraction_id):
    try:
        infraction_dto = InfractionDTO(**request.json)
        infraction = update_infraction(infraction_id, infraction_dto)
        return handle_api_response(data={"message": "Infraction updated successfully"})
    except ValidationError as e:
        return handle_api_response(error={"errors": e.errors()}, status_code=400)
    except InfractionNotFoundError as e:
        return handle_api_response(error={"message": str(e)}, status_code=404)
    except InfractionUpdateError as e:
        return handle_api_response(error={"message": str(e)}, status_code=500)


@infraction_blueprint.route("/<int:infraction_id>", methods=["DELETE"])
@jwt_required()
def delete_infraction_endpoint(infraction_id):
    try:
        success = delete_infraction(infraction_id)
        if success:
            return handle_api_response(
                data={"message": "Infraction deleted successfully"}
            )
    except InfractionNotFoundError as e:
        return handle_api_response(error={"message": str(e)}, status_code=404)
    except InfractionDeletionError as e:
        return handle_api_response(error={"message": str(e)}, status_code=500)


@infraction_blueprint.route("/generate_report/<string:email>", methods=["GET"])
@jwt_required()
def generate_report_endpoint(email):
    person_adapter = PersonAdapter()
    try:
        report = generate_report(email, person_adapter)
        if "error" in report:
            return handle_api_response(
                error={"message": report["error"]}, status_code=404
            )
        return handle_api_response(data=report, status_code=200)
    except Exception as e:
        return handle_api_response(error={"message": str(e)}, status_code=500)
