from typing import List, Optional, Tuple
from marshmallow import Schema, fields, ValidationError
import pandas as pd


class WeldingDataRequestSchema(Schema):
    """Schema for validating welding data prediction requests."""
    DV_R = fields.Float(required=True)
    DA_R = fields.Float(required=True)
    AV_R = fields.Float(required=True)
    AA_R = fields.Float(required=True)
    PM_R = fields.Float(required=True)


def _filter_error_rows(errors: dict, validated_input: pd.DataFrame) -> pd.DataFrame:
    """Remove input data rows with errors."""
    indexes = errors.keys()
    # Delete rows with errors
    validated_input.drop(index=indexes, inplace=True)
    return validated_input


def validate_inputs(*, input_data):
    """Check prediction request inputs."""
    
    errors = None
    validated_input = None
    
    try:
        if isinstance(input_data, dict):
            if 'inputs' in input_data:
                # Multiple inputs format
                inputs = input_data['inputs']
            else:
                # Single input format
                inputs = [input_data]
        else:
            inputs = input_data
            
        # Validate each input
        schema = WeldingDataRequestSchema()
        validated_inputs = []
        
        for i, input_item in enumerate(inputs):
            try:
                validated_item = schema.load(input_item)
                validated_inputs.append(validated_item)
            except ValidationError as exc:
                errors = f"Input {i}: {exc.messages}"
                break
                
        if not errors:
            validated_input = pd.DataFrame(validated_inputs)
            
    except Exception as error:
        errors = str(error)

    return validated_input, errors