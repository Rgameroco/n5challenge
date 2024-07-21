from flask import Blueprint, request
from pydantic import ValidationError

from app.commons.responses import handle_api_response
from app.domain.users.services.person_services import (
    PersonDTO,
    create_person,
    delete_person,
    get_person,
    update_person,
    PersonNotFoundError,
    PersonCreationError,
    PersonUpdateError,
    PersonDeletionError,
)

person_blueprint = Blueprint("persons", __name__)


@person_blueprint.route("/", methods=["POST"])
def add_person():
    try:
        person_dto = PersonDTO(**request.json)
        person = create_person(person_dto)
        return handle_api_response(
            data={"message": "User created successfully", "id": person.id},
            status_code=201,
        )
    except ValidationError as e:
        return handle_api_response(error={"errors": e.errors()}, status_code=400)
    except PersonCreationError as e:
        return handle_api_response(error={"message": str(e)}, status_code=500)


@person_blueprint.route("/<int:person_id>", methods=["GET"])
def retrieve_person(person_id):
    try:
        person = get_person(person_id)
        return handle_api_response(data={"name": person.name, "email": person.email})
    except PersonNotFoundError:
        return handle_api_response(
            error={"message": "Person not found"}, status_code=404
        )
    except Exception as e:
        return handle_api_response(error={"message": str(e)}, status_code=500)


@person_blueprint.route("/<int:person_id>", methods=["PUT"])
def modify_person(person_id):
    try:
        person_dto = PersonDTO(**request.json)
        person = update_person(person_id, **person_dto.dict())
        if person:
            return handle_api_response(data={"message": "Updated successfully"})
    except ValidationError as e:
        return handle_api_response(error={"errors": e.errors()}, status_code=400)
    except PersonNotFoundError:
        return handle_api_response(
            error={"message": "Person not found"}, status_code=404
        )
    except PersonUpdateError as e:
        return handle_api_response(error={"message": str(e)}, status_code=500)


@person_blueprint.route("/<int:person_id>", methods=["DELETE"])
def remove_person(person_id):
    try:
        if delete_person(person_id):
            return handle_api_response(data={"message": "Deleted successfully"})
    except PersonNotFoundError:
        return handle_api_response(
            error={"message": "Person not found"}, status_code=404
        )
    except PersonDeletionError as e:
        return handle_api_response(error={"message": str(e)}, status_code=500)
