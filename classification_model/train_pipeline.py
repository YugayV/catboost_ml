import sys
from pathlib import Path

# Add the package root to Python path 
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PACKAGE_ROOT))

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

from classification_model import __version__ as _version
from classification_model.config.core import config
from classification_model.processing.data_manager import load_dataset, save_pipeline
from classification_model.pipeline import classification_pipe

def run_training() -> None:
    """Train the model."""

    #Read the dataset
    data = load_dataset(file_name=config.app_config.training_data_file)

    # Remove PIPE_NO as it's just an identifier 
    if "PIPE_NO" in data.columns:
        data = data.drop(columns=["PIPE_NO"], axis=1)

    # Split data into train and test
    X_train, X_test, y_train, y_test = train_test_split(
        data[config.model_config.features],
        data[config.model_config.target],
        test_size=config.model_config.test_size,
        random_state=config.model_config.random_state, 
        stratify=data[config.model_config.target]
    )

    # Train the model
    classification_pipe.fit(X_train, y_train)

    # Evaluate the model
    y_pred = classification_pipe.predict(X_test)
    y_pred_proba = classification_pipe.predict_proba(X_test)[:, 1]

    #Print evaluation metrics
    print(classification_report(y_test, y_pred))
    print(f"ROC AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")


    # Persist the trained model
    save_pipeline(pipeline_to_persist=classification_pipe) 
    print(f"Model trained and saved successfully. Version: {_version}")

    if __name__ == "__main__":
        run_training()
        