import asyncio

import aiohttp
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from .extensions import db
from .forms import FileUploadForm, URLMapForm
from .models import URLMap
from .utils import get_unique_short_id
from .yadisk import ensure_dir, get_download_link, get_upload_link, upload

bp = Blueprint("main", __name__)

RESERVED_SHORT_IDS = {"files"}


@bp.route("/", methods=["GET", "POST"])
def index():
    form = URLMapForm()
    short_link = None

    if form.validate_on_submit():
        original = form.original_link.data
        custom = (form.custom_id.data or "").strip()

        if not custom:
            existing = URLMap.query.filter_by(original=original).first()
            if existing is not None:
                short_link = url_for(
                    "main.redirect_view",
                    short_id=existing.short,
                    _external=True,
                )
                return render_template(
                    "index.html", form=form, short_link=short_link)

            short_id = get_unique_short_id()
        else:
            if custom == "files" or URLMap.query.filter_by(
                    short=custom).first():
                flash("Предложенный вариант короткой ссылки уже существует.")
                return render_template("index.html", form=form)

            short_id = custom

        url_map = URLMap(original=original, short=short_id)
        db.session.add(url_map)
        db.session.commit()

        short_link = url_for(
            "main.redirect_view",
            short_id=short_id,
            _external=True)

    return render_template(
        "index.html",
        form=form,
        short_link=short_link,
    )


@bp.get("/<string:short_id>")
def redirect_view(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)


@bp.route("/files", methods=["GET", "POST"])
def files():
    form = FileUploadForm()
    results = []

    if request.method == "POST":
        file_list = request.files.getlist("files")
        if not file_list or (
                len(file_list) == 1 and file_list[0].filename == ""):
            form.files.errors.append("Выбери хотя бы один файл")
            return render_template("files.html", form=form, results=results)

        token = current_app.config.get("DISK_TOKEN")
        if not token:
            form.files.errors.append("DISK_TOKEN не задан")
            return render_template("files.html", form=form, results=results)

        async def upload_all():
            async with aiohttp.ClientSession() as session:
                if current_app.config.get("YADISK_MKDIR"):
                    await ensure_dir(session, token, "app:/yacut")

                async def upload_one(file_storage):
                    disk_path = f"app:/yacut/{file_storage.filename}"

                    file_storage.stream.seek(0)
                    file_bytes = file_storage.read()

                    href = await get_upload_link(session, token, disk_path)
                    await upload(session, href, file_bytes)
                    download_href = await get_download_link(
                        session,
                        token,
                        disk_path,
                    )

                    return {
                        "filename": file_storage.filename,
                        "download_url": download_href}

                tasks = [upload_one(f) for f in file_list]
                return await asyncio.gather(*tasks)

        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            uploaded = loop.run_until_complete(upload_all())
        finally:
            loop.close()
            asyncio.set_event_loop(None)

        for item in uploaded:
            short_id = get_unique_short_id()
            db.session.add(
                URLMap(
                    original=item["download_url"],
                    short=short_id))

            results.append(
                {
                    "filename": item["filename"],
                    "short_link": url_for(
                        "main.redirect_view",
                        short_id=short_id,
                        _external=True,
                    ),
                }
            )

        db.session.commit()

    return render_template("files.html", form=form, results=results)