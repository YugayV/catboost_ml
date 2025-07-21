import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from pydantic import BaseModel
from strictyaml import YAML, load, Map, Str, Int, Float, Seq, Bool

import classification_model

# Project Directories
PACKAGE_ROOT = Path(classification_model.__file__).resolve().parent
ROOT = PACKAGE_ROOT.parent
CONFIG_FILE_PATH = PACKAGE_ROOT / "config.yml"
DATASET_DIR = PACKAGE_ROOT / "datasets"
TRAINED_MODEL_DIR = PACKAGE_ROOT / "trained_models"


class AppConfig(BaseModel):
    """
    Application-level config.
    """
    package_name: str
    training_data_file: str
    pipeline_name: str
    pipeline_save_file: str


class ModelConfig(BaseModel):
    """
    All configuration relevant to model
    training and feature engineering.
    """
    target: str
    features: List[str]
    test_size: float
    random_state: int
    categorical_features: List[str] = []  # Default to empty list
    numerical_vars: List[str]
    catboost_params: Dict
    feature_ranges: Dict


class Config(BaseModel):
    """Master config object."""
    app_config: AppConfig
    ml_model_config: ModelConfig  # Переименовано из model_config


def find_config_file() -> Path:
    """Locate the configuration file."""
    if CONFIG_FILE_PATH.is_file():
        return CONFIG_FILE_PATH
    raise Exception(f"Config not found at {CONFIG_FILE_PATH!r}")


def fetch_config_from_yaml(cfg_path: Path = None) -> YAML:
    """Parse YAML containing the package configuration."""
    if not cfg_path:
        cfg_path = find_config_file()

    # Define schema for proper type parsing
    schema = Map({
        "app_config": Map({
            "package_name": Str(),
            "training_data_file": Str(),
            "pipeline_name": Str(),
            "pipeline_save_file": Str(),
        }),
        "model_config": Map({
            "target": Str(),
            "features": Seq(Str()),
            "test_size": Float(),
            "random_state": Int(),
            "numerical_vars": Seq(Str()),
            "catboost_params": Map({
                "iterations": Int(),
                "learning_rate": Float(),
                "depth": Int(),
                "l2_leaf_reg": Int(),
                "border_count": Int(),
                "thread_count": Int(),
                "random_seed": Int(),
                "verbose": Bool(),
                "eval_metric": Str(),
                "early_stopping_rounds": Int(),
            }),
            "feature_ranges": Map({
                "DV_R": Map({"min": Int(), "max": Int()}),
                "DA_R": Map({"min": Int(), "max": Int()}),
                "AV_R": Map({"min": Int(), "max": Int()}),
                "AA_R": Map({"min": Int(), "max": Int()}),
                "PM_R": Map({"min": Int(), "max": Int()}),
            }),
        }),
    })

    if cfg_path:
        with open(cfg_path, "r") as conf_file:
            parsed_config = load(conf_file.read(), schema)
            return parsed_config
    raise OSError(f"Did not find config file at path: {cfg_path}")


def create_and_validate_config(parsed_config: YAML = None) -> Config:
    """Run validation on config values."""
    if parsed_config is None:
        parsed_config = fetch_config_from_yaml()

    data = parsed_config.data
    _config = Config(
        app_config=AppConfig(**data["app_config"]),
        ml_model_config=ModelConfig(**data["model_config"]),
    )

    return _config


config = create_and_validate_config()