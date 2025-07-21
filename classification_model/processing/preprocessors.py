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
      
      #Validate data ranges
      for feature, ranges in self.feature_ranges.items(): 
         if feature in X.columns: 
            # Convert to numeric values in case they're strings
            min_val = float(ranges['min'])
            max_val = float(ranges['max'])
            #Clip values to valid range
            X[feature] = np.clip(X[feature], min_val, max_val)

      X = X.fillna(X.median())

      return X 
   
class FeatureEngineer(BaseEstimator, TransformerMixin): 
   """Creates additional features from existing ones."""

   def fit(self, X, y=None): 
      return self
   
   def transform(self, X): 
      """Create engineered features."""
      X = X.copy()

      #Power efficiency ratio
      X['power_efficiency'] = X['PM_R'] / (X['DV_R'] * X['DA_R'] / 1000)

      X['wire_feed_ratio'] = X['AV_R'] / X['AA_R']

      X['voltage_current_ratio'] = X['DV_R'] / X['DA_R']

      return X