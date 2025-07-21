from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from pydantic import BaseModel, ValidationError

from classification_model.config.core import config


def drop_na_inputs(*, input_data: pd.DataFrame) -> pd.DataFrame:
    """Check model inputs for na values and filter."""
    validated_data = input_data.copy()
    if input_data.isnull().any().any():
        validated_data = input_data.dropna()
    return validated_data


def validate_inputs(*, input_data: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[dict]]:
    """Check model inputs for unprocessable values."""
    
    relevant_data = input_data[config.ml_model_config.features].copy()
    validated_data = drop_na_inputs(input_data=relevant_data)
    errors = None

    try:
        # Check for required features
        if not all(feature in validated_data.columns for feature in config.ml_model_config.features):
            missing_features = set(config.ml_model_config.features) - set(validated_data.columns)
            errors = f"Missing features: {missing_features}"
            
        # Check data types
        for feature in config.ml_model_config.numerical_vars:
            if feature in validated_data.columns:
                if not pd.api.types.is_numeric_dtype(validated_data[feature]):
                    errors = f"Feature {feature} must be numeric"
                    
        # Check for reasonable value ranges
        for feature, ranges in config.ml_model_config.feature_ranges.items():
            if feature in validated_data.columns:
                min_val, max_val = ranges['min'], ranges['max']
                out_of_range = (
                    (validated_data[feature] < min_val) | 
                    (validated_data[feature] > max_val)
                ).any()
                if out_of_range:
                    errors = f"Feature {feature} has values outside expected range [{min_val}, {max_val}]"
                    
    except Exception as error:
        errors = error

    return validated_data, errors


class WeldingDataInputSchema(BaseModel):
    """Schema for validating welding data inputs."""
    DV_R: Optional[float]
    DA_R: Optional[float] 
    AV_R: Optional[float]
    AA_R: Optional[float]
    PM_R: Optional[float]


class MultipleWeldingDataInputs(BaseModel):
    """Schema for validating multiple welding data inputs."""
    inputs: List[WeldingDataInputSchema]