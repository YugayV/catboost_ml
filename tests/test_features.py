import pytest
import pandas as pd
from classification_model.processing.preprocessors import DataValidator, FeatureEngineer


def test_data_validator(sample_dataframe):
    """Test data validation."""
    # Given
    feature_ranges = {
        'DV_R': {'min': 200, 'max': 500},
        'DA_R': {'min': 5000, 'max': 15000}
    }
    validator = DataValidator(feature_ranges=feature_ranges)
    
    # When
    result = validator.transform(sample_dataframe)
    
    # Then
    assert result is not None
    assert len(result) == len(sample_dataframe)
    assert all(col in result.columns for col in sample_dataframe.columns)


def test_feature_engineer(sample_dataframe):
    """Test feature engineering."""
    # Given
    engineer = FeatureEngineer()
    
    # When
    result = engineer.transform(sample_dataframe)
    
    # Then
    assert result is not None
    assert 'power_efficiency' in result.columns
    assert 'wire_feed_ratio' in result.columns
    assert 'voltage_current_ratio' in result.columns
    assert len(result) == len(sample_dataframe)