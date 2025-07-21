from flask import Flask

from api.config import get_logger 
from api.controller import prediction_app

_logger = get_logger(logger_name=__name__)  

def create_app(*, config_object) -> Flask:
    """Create a flask app instance."""

    flask_app = Flask(__name__)
    flask_app.config.from_object(config_object)

    #Register blueprints
    flask_app.register_blueprint(prediction_app)
    _logger.debug("Application instance created")

    return flask_app
