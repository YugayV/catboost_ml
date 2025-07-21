import typing as t
from pathlib import Path

import numpy as np
import pandas as pd

from classification_model import __version__ as _version
from classification_model.config.core import config
from classification_model.processing.data_manager import load_pipeline
from classification_model.processing.validation import validate_inputs

pipeline_file_name = f"{config.app_config.pipeline_save_file}{_version}.pkl"
_classification_pipe = load_pipeline(file_name=pipeline_file_name)


def make_prediction(
    *,
    input_data: t.Union[pd.DataFrame, dict],
) -> dict:
    """Make a prediction using a saved model pipeline."""
    
    data = pd.DataFrame(input_data)
    validated_data, errors = validate_inputs(input_data=data)
    results = {"predictions": None, "version": _version, "errors": errors}

    if not errors:
        predictions = _classification_pipe.predict(
            X=validated_data[config.ml_model_config.features]
        )
        
        predictions_proba = _classification_pipe.predict_proba(
            X=validated_data[config.ml_model_config.features]
        )
        results = {
            "predictions": predictions.tolist(),
            "prediction_probabilities": predictions_proba.tolist(),
            "version": _version,
            "errors": errors,
        }

    return results