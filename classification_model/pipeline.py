import sys
from pathlib import Path

# Add the package root to Python path
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PACKAGE_ROOT))

import numpy as np
import pandas as pd 
from catboost import CatBoostClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from classification_model.config.core import config
from classification_model.processing import preprocessors as pp 

classification_pipe = Pipeline([ 
    ('data_validator', pp.DataValidator( 
        feature_ranges=config.ml_model_config.feature_ranges
    )), 

    ('scaler', StandardScaler()), 
    ('classifier', CatBoostClassifier( 
        **config.ml_model_config.catboost_params
    ))
])