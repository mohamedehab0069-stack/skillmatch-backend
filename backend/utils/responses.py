from flask import jsonify


def success(data: dict | list, status: int = 200):
    return jsonify({"success": True, "data": data}), status


def error(message: str, status: int = 400, details: dict = None):
    body = {"success": False, "error": message}
    if details:
        body["details"] = details
    return jsonify(body), status
