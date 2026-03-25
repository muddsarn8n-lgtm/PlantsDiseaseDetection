import os
import mlflow
from mlflow.tracking import MlflowClient

TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "mlruns")
MODEL_NAME = "potato_disease_model"


def get_next_version():
    """Get the next model version number from MLflow registry."""
    mlflow.set_tracking_uri(TRACKING_URI)
    client = MlflowClient()

    try:
        versions = client.search_model_versions(f"name='{MODEL_NAME}'")
        if versions:
            return max(int(v.version) for v in versions) + 1
        return 1
    except Exception:
        return 1


def register_model(model_path, history, params, keras_model=None):
    """
    Register a trained model in MLflow.

    Args:
        model_path: Path to the SavedModel directory
        history: Keras training history object
        params: Dict with training parameters
        keras_model: The Keras model object (needed for MLflow registration)

    Returns:
        The new version number
    """
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment("potato_disease_detection")

    with mlflow.start_run():
        # Log training parameters
        for key, value in params.items():
            mlflow.log_param(key, value)

        # Log final metrics from training history
        final_epoch = len(history.history["accuracy"]) - 1
        mlflow.log_metric("train_accuracy", history.history["accuracy"][final_epoch])
        mlflow.log_metric("train_loss", history.history["loss"][final_epoch])
        mlflow.log_metric("val_accuracy", history.history["val_accuracy"][final_epoch])
        mlflow.log_metric("val_loss", history.history["val_loss"][final_epoch])

        # Log model
        if keras_model is not None:
            mlflow.tensorflow.log_model(
                model=keras_model,
                artifact_path="model",
                registered_model_name=MODEL_NAME,
            )
            client = MlflowClient()
            versions = client.search_model_versions(f"name='{MODEL_NAME}'")
            result = max(versions, key=lambda v: int(v.version))
            print(f"Model registered as version {result.version}")
            return int(result.version)
        else:
            # Fallback: just log artifacts without registration
            mlflow.log_artifacts(model_path, artifact_path="model")
            print(f"Model artifacts logged (no registry)")
            return 1
