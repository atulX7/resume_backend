# logging_config.py
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # keep any loggers already defined
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "app_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",  # ensure the logs/ directory exists
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "standard",
        },
        "celery_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/celery.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "standard",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        # Logger for your FastAPI app
        "app": {
            "handlers": ["app_file_handler", "console"],
            "level": "INFO",
            "propagate": False,
        },
        # Logger for Celery tasks (or worker-specific logs)
        "celery": {
            "handlers": ["celery_file_handler", "console"],
            "level": "INFO",
            "propagate": False,
        },
        # Root logger (optional)
        "": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
