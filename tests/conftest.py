import pytest
import pandas as pd


@pytest.fixture
def sample_input_data():
    """Sample input data for testing."""
    return {
        "inputs": [
            {
                "DV_R": 318,
                "DA_R": 7798,
                "AV_R": 365,
                "AA_R": 7177,
                "PM_R": 9507
            }
        ]
    }


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing."""
    return pd.DataFrame({
        "DV_R": [318, 316, 309],
        "DA_R": [7798, 8479, 7603],
        "AV_R": [365, 380, 351],
        "AA_R": [7177, 8846, 5726],
        "PM_R": [9507, 9484, 9840]
    })