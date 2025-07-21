import logging
import sys
from typing import List
import os

class Config: 
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get("0775f88cb42061d8955f56f17560ff4b5d3a882f8e9e91e1e5e9517d071aeda8")
    SERVER_PORT = 5000

class ProductionConfig(Config): 
    DEBUG = False
    SERVER_PORT = 5000

class DevelopmentConfig(Config): 
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config): 
    TESTING = True


def get_logger(*, logger_name: str) -> logging.Logger: 
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers: 
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter( 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger