import re

from flask import Blueprint, jsonify, request, url_for

from .extensions import db
from .models import URLMap
from .utils import get_unique_short_id

api_bp = Blueprint("api", __name__, url_prefix="/api")
api_bp.strict_slashes = False

CUSTOM_ID_RE = re.compile(r"^[A-Za-z0-9]+$")
RESERVED_SHORT_IDS = {"files"}


def error(message: str, status_code: int):
    return jsonify({"message": message}), status_code


@api_bp.post("/id")
@api_bp.post("/id/")
def create_id():
    data = request.get_json(silent=True)

    if data is None:
        return error("Отсутствует тело запроса", 400)

    if "url" not in data:
        return error('"url" является обязательным полем!', 400)

    original = data.get("url")
    custom_id = data.get("custom_id")
    if isinstance(custom_id, str) and custom_id.strip() == "":
        custom_id = None

    if custom_id is not None:
        if (
            not isinstance(custom_id, str)
            or len(custom_id) > 16
            or not CUSTOM_ID_RE.fullmatch(custom_id)
            or custom_id in RESERVED_SHORT_IDS
        ):
            return error("Указано недопустимое имя для короткой ссылки", 400)

        if URLMap.query.filter_by(short=custom_id).first():
            return error(
                "Предложенный вариант короткой ссылки уже существует.", 400)

        short_id = custom_id
    else:
        short_id = get_unique_short_id()

    url_map = URLMap(original=original, short=short_id)
    db.session.add(url_map)
    db.session.commit()

    return (jsonify({"url": original, "short_link": url_for(
        "main.redirect_view", short_id=short_id, _external=True), }), 201, )


@api_bp.get("/id/<string:short_id>")
@api_bp.get("/id/<string:short_id>/")
def get_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        return error("Указанный id не найден", 404)

    return jsonify({"url": url_map.original}), 200