from flask import Blueprint, request, jsonify
import sys
import os
from pathlib import Path

# Add the classification model to the path - more robust approach
current_file = Path(__file__).resolve()
api_dir = current_file.parent  # api directory
ml_api_dir = api_dir.parent    # ml_api directory
packages_dir = ml_api_dir.parent  # packages directory
project_root = packages_dir.parent  # project root directory

# Add both project root and packages directory to path
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(packages_dir))

print(f"Current file: {current_file}")
print(f"Project root: {project_root}")
print(f"Looking for classification_model in: {project_root / 'classification_model'}")

try:
    from classification_model.predict import make_prediction
    from classification_model import __version__ as model_version
    print("✓ Successfully imported classification_model")
except ImportError as e:
    print(f"✗ Failed to import classification_model: {e}")
    print(f"Python path: {sys.path}")
    # Try alternative path
    alt_path = project_root.parent / "classification_model"
    if alt_path.exists():
        sys.path.insert(0, str(project_root.parent))
        try:
            from classification_model.predict import make_prediction
            from classification_model import __version__ as model_version
            print(f"✓ Successfully imported from alternative path: {alt_path}")
        except ImportError as e2:
            print(f"✗ Alternative import also failed: {e2}")
            raise e
    else:
        raise e

from api.config import get_logger
from api.validation import validate_inputs

# Import version directly to avoid circular import
api_version = "0.1.0"

_logger = get_logger(logger_name=__name__)

prediction_app = Blueprint('prediction_app', __name__)


@prediction_app.route("/health", methods=['GET'])
def health():
    """Health check endpoint."""
    if request.method == 'GET':
        _logger.info('Health status OK')
        return 'ok'


@prediction_app.route('/version', methods=['GET'])
def version():
    """Version information endpoint."""
    if request.method == 'GET':
        return jsonify({
            'model_version': model_version,
            'api_version': api_version
        })


@prediction_app.route("/v1/predict/classification", methods=['POST'])
def predict():
    """Make predictions on welding quality."""
    if request.method == 'POST':
        json_data = request.get_json()
        _logger.debug(f"Inputs: {json_data}")

        input_data, errors = validate_inputs(input_data=json_data)
        
        if errors:
            return jsonify({
                "predictions": None,
                "version": model_version,
                "errors": errors
            }), 400

        result = make_prediction(input_data=input_data)
        _logger.debug(f"Outputs: {result}")

        predictions = result.get('predictions')
        prediction_probs = result.get('prediction_probabilities')
        version = result.get('version')

        return jsonify({
            "predictions": predictions,
            "prediction_probabilities": prediction_probs,
            "version": version,
            "errors": errors
        })