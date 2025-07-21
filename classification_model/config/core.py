import logging
import sys
from typing import Optional, Dict, List, Sequence
from pathlib import Path

from pydantic import BaseModel
from strictyaml import YAML, load

import classification_model

# Project root directory
PACKAGE_ROOT = Path(classification_model.__file__).resolve().parent
ROOT = PACKAGE_ROOT.parent
CONFIG_FILE_PATH = PACKAGE_ROOT / "config.yml"
DATASET_DIR = PACKAGE_ROOT / "datasets"
TRAINED_MODELS_DIR = PACKAGE_ROOT / "trained_models"


class AppConfig(BaseModel): 
    """Application level configuration."""
    package_name: str
    training_data_file: str
    pipeline_name: str 
    pipeline_save_file: str


class ModelConfig(BaseModel):
    """All configuration relevant to model training and feature engineering."""
    target: str
    features: List[str]
    test_size: float
    random_state: int
    numerical_vars: List[str]
    catboost_params: Dict[str, Optional[float]]
    catboost_params: Dict
    feature_ranges: Dict

class Config(BaseModel):
    """Master config object."""
    app_config: AppConfig
    model_config: ModelConfig

def find_config_file() -> Path:
    """Find the configuration file."""
    if CONFIG_FILE_PATH.exists():
        return CONFIG_FILE_PATH
    else:
        raise FileNotFoundError(f"Configuration file not found at {CONFIG_FILE_PATH}")
    
def create_and_validate_config() -> Path:
     """Locate the configuration file."""
    if CONFIG_FILE_PATH.is_file():
        return CONFIG_FILE_PATH
    raise Exception(f"Config not found at {CONFIG_FILE_PATH!r}")


def fetch_config_from_yaml(cfg_path: Path = None) -> YAML:
    """Parse YAML containing the package configuration."""
    if not cfg_path:
        cfg_path = find_config_file()

    if cfg_path:
        with open(cfg_path, "r") as conf_file:
            parsed_config = load(conf_file.read())
            return parsed_config
    raise OSError(f"Did not find config file at path: {cfg_path}")


def create_and_validate_config(parsed_config: YAML = None) -> Config:
    """Run validation on config values."""
    if parsed_config is None:
        parsed_config = fetch_config_from_yaml()

    _config = Config(
        app_config=AppConfig(**parsed_config.data),
        model_config=ModelConfig(**parsed_config.data),
    )

    return _config


config = create_and_validate_config()

### Шаг 3: Создание препроцессоров

# classification_model/processing/preprocessors.py
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class DataValidator(BaseEstimator, TransformerMixin):
    """Validates input data ranges and types."""

    def __init__(self, feature_ranges=None):
        self.feature_ranges = feature_ranges or {}

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        """Validate and clean input data."""
        X = X.copy()

        # Check for required features
        required_features = ['DV_R', 'DA_R', 'AV_R', 'AA_R', 'PM_R']
        missing_features = set(required_features) - set(X.columns)
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")

        # Validate data ranges
        for feature, ranges in self.feature_ranges.items():
            if feature in X.columns:
                min_val, max_val = ranges['min'], ranges['max']
                # Clip values to valid range
                X[feature] = np.clip(X[feature], min_val, max_val)

        # Handle missing values
        X = X.fillna(X.median())

        return X