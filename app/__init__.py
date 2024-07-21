# app/__init__.py
import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_admin import Admin
from app.domain.infractions.models import Infraction
from app.domain.users.models import Officer, Person
from app.domain.vehicles.models import Vehicle
from app.extensions import db
from flask_admin.contrib.sqla import ModelView
from app.infrastructure.logger import app_logger


def get_config():
    return {
        "SQLALCHEMY_DATABASE_URI": os.environ.get(
            "DATABASE_URL", "sqlite:///default.db"
        ),
        "SECRET_KEY": os.environ.get("SECRET_KEY", "fallback_secret_key"),
    }


def create_app():
    app = Flask(__name__)
    app.config.update(get_config())

    db.init_app(app)

    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    app.logger.handlers = app_logger.handlers
    app.logger.setLevel(app_logger.level)

    admin = Admin(app, name="Mi Panel de Administración", template_mode="bootstrap3")
    admin.add_view(ModelView(Officer, db.session, category="Usuarios"))
    admin.add_view(ModelView(Person, db.session, category="Usuarios"))
    admin.add_view(ModelView(Infraction, db.session, category="Infracciones"))
    admin.add_view(ModelView(Vehicle, db.session, category="Vehículos"))
    return app
