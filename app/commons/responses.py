from typing import Any, Dict, Optional, Tuple

from flask import Response, jsonify


def handle_api_response(
    data: Optional[Dict[str, Any]] = None,
    error: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
) -> Response:
    """Utility function to handle API responses.

    Args:
        data (Optional[Dict[str, Any]]): Data to be included in the response, defaults to None.
        error (Optional[Dict[str, Any]]): Error message to be included in the response, defaults to None.
        status_code (int): HTTP status code for the response, defaults to 200.

    Returns:
        Response: A Flask response object with the specified data, error message, and status code.
    """
    if error:
        return jsonify({"error": error}), status_code
    return jsonify(data), status_code
