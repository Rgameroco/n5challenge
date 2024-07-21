from flask import Blueprint, request
from pydantic import ValidationError

from app.commons.responses import handle_api_response
from app.domain.users.services.officer_service import (
    OfficerDTO,
    authenticate_officer,
    create_officer,
    delete_officer,
    get_officer_by_id,
    update_officer,
)
from app.infrastructure.logger import app_logger

officer_blueprint = Blueprint("officers", __name__)


@officer_blueprint.route("/", methods=["POST"])
def add_officer():
    """Endpoint to create a new officer."""
    try:
        officer_dto = OfficerDTO(**request.json)
        officer_id = create_officer(officer_dto)
        app_logger.info(f"Officer created successfully with ID {officer_id}")
        return handle_api_response(
            data={"message": "Officer created successfully", "officer_id": officer_id},
            status_code=201,
        )
    except ValidationError as e:
        app_logger.warning(
            "Validation error occurred while creating an officer.", exc_info=True
        )
        return handle_api_response(error={"errors": e.errors()}, status_code=400)
    except Exception as e:
        app_logger.error(
            "Unexpected error occurred while creating an officer.", exc_info=True
        )
        return handle_api_response(error={"message": str(e)}, status_code=500)


@officer_blueprint.route("/<int:officer_id>", methods=["PUT"])
def edit_officer(officer_id):
    """Endpoint to update an existing officer."""
    try:
        officer_dto = OfficerDTO(**request.json)
        updated_officer_id = update_officer(officer_id, officer_dto)
        if updated_officer_id:
            app_logger.info(f"Officer with ID {officer_id} updated successfully.")
            return handle_api_response(
                data={"message": "Officer updated successfully"}, status_code=200
            )
        else:
            app_logger.warning(f"Officer with ID {officer_id} not found.")
            return handle_api_response(
                error={"message": "Officer not found"}, status_code=404
            )
    except ValidationError as e:
        app_logger.warning(
            "Validation error occurred while updating an officer.", exc_info=True
        )
        return handle_api_response(error={"errors": e.errors()}, status_code=400)
    except Exception as e:
        app_logger.error(
            "Unexpected error occurred while updating an officer.", exc_info=True
        )
        return handle_api_response(error={"message": str(e)}, status_code=500)


@officer_blueprint.route("/<int:officer_id>", methods=["GET"])
def get_officer(officer_id):
    """Endpoint to retrieve an officer by ID."""
    try:
        officer_response_dto = get_officer_by_id(officer_id)
        if officer_response_dto:
            return handle_api_response(data=officer_response_dto.dict())
        else:
            app_logger.warning(f"Officer with ID {officer_id} not found.")
            return handle_api_response(
                error={"message": "Officer not found"}, status_code=404
            )
    except Exception as e:
        app_logger.error(
            "Unexpected error occurred while retrieving an officer.", exc_info=True
        )
        return handle_api_response(error={"message": str(e)}, status_code=500)


@officer_blueprint.route("/<int:officer_id>", methods=["DELETE"])
def remove_officer(officer_id):
    """Endpoint to delete an officer."""
    try:
        success = delete_officer(officer_id)
        if success:
            app_logger.info(f"Officer with ID {officer_id} deleted successfully.")
            return handle_api_response(data={"message": "Officer deleted successfully"})
        else:
            app_logger.warning(f"Officer with ID {officer_id} not found.")
            return handle_api_response(
                error={"message": "Officer not found"}, status_code=404
            )
    except Exception as e:
        app_logger.error(
            "Unexpected error occurred while deleting an officer.", exc_info=True
        )
        return handle_api_response(error={"message": str(e)}, status_code=500)


@officer_blueprint.route("/login_officer", methods=["POST"])
def login_officer():
    """
    Endpoint for officer login. Expects JSON containing 'unique_identifier' and 'password'.
    Returns a JWT token if the credentials are valid.
    """
    unique_identifier = request.json.get("unique_identifier")
    password = request.json.get("password")
    try:
        token = authenticate_officer(unique_identifier, password)
        if token:
            app_logger.info(f"Officer {unique_identifier} logged in successfully.")
            return handle_api_response(data={"access_token": token})
        else:
            app_logger.warning(f"Invalid credentials for officer {unique_identifier}.")
            return handle_api_response(
                error={"msg": "Invalid credentials"}, status_code=401
            )
    except Exception as e:
        app_logger.error(
            "Unexpected error occurred during officer login.", exc_info=True
        )
        return handle_api_response(error={"message": str(e)}, status_code=500)
