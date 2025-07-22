import pytest
import pandas as pd
from classification_model.predict import make_prediction


def test_make_prediction(sample_dataframe):
    """Test making predictions."""
    # Given
    expected_no_errors = None
    
    # When
    result = make_prediction(input_data=sample_dataframe)
    
    # Then
    assert result is not None
    assert result["errors"] == expected_no_errors
    assert len(result["predictions"]) == 3
    assert all(pred in [0, 1] for pred in result["predictions"])
    assert "prediction_probabilities" in result
    assert "version" in result


def test_make_prediction_with_invalid_data():
    """Test prediction with invalid data."""
    # Given
    invalid_data = pd.DataFrame({
        "DV_R": [1000],  # Out of range
        "DA_R": [7798],
        "AV_R": [365],
        "AA_R": [7177],
        "PM_R": [9507]
    })
    
    # When
    result = make_prediction(input_data=invalid_data)
    
    # Then
    assert result is not None
    # Should still work due to clipping in preprocessor
    assert result["predictions"] is not None