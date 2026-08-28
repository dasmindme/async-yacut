from flask import Flask

from .config import Config
from .extensions import db, migrate
from flask import render_template


def create_app():
    app = Flask(
        __name__,
        template_folder="../html",
        static_folder="../html",
        static_url_path="",
    )
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  # noqa: F401

    from .views import bp as main_bp
    app.register_blueprint(main_bp)

    from .api_views import api_bp
    app.register_blueprint(api_bp)

    from .error_handlers import register_error_handlers
    register_error_handlers(app)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("500.html"), 500

    return app


app = create_app()