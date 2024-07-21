import logging
import os

# Configuración básica de logging para el módulo de configuración
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///default.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOGGING_LOCATION = "app.log"
    LOGGING_LEVEL = logging.INFO


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOGGING_LEVEL = logging.DEBUG  # Más detalle en desarrollo


class ProductionConfig(Config):
    DEBUG = False
    LOGGING_LEVEL = logging.ERROR  # Solo errores en producción


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    LOGGING_LEVEL = logging.DEBUG  # Detallado para tests


config_by_name = dict(dev=DevelopmentConfig, prod=ProductionConfig, test=TestingConfig)
