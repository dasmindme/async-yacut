from flask import jsonify, render_template, request

from .exceptions import InvalidAPIUsage


def wants_json_response() -> bool:
    if request.path.startswith("/api/"):
        return True
    accept = (request.headers.get("Accept") or "").lower()
    return "application/json" in accept


def register_error_handlers(app):
    @app.errorhandler(InvalidAPIUsage)
    def handle_invalid_api_usage(error):
        return jsonify({"message": error.message}), error.status_code

    @app.errorhandler(404)
    def page_not_found(error):
        if wants_json_response():
            return jsonify({"message": "Указанный id не найден"}), 404
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        if wants_json_response():
            return jsonify({"message": "Внутренняя ошибка сервера"}), 500
        return render_template("500.html"), 500