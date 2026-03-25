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


def register_model(model_path, history, params):
    """
    Register a trained model in MLflow.

    Args:
        model_path: Path to the SavedModel directory
        history: Keras training history object
        params: Dict with training parameters (epochs, batch_size, image_size)

    Returns:
        The new version number
    """
    mlflow.set_tracking_uri(TRACKING_URI)

    mlflow.set_experiment("potato_disease_detection")

    with mlflow.start_run():
        # Log training parameters
        mlflow.log_param("epochs", params.get("epochs"))
        mlflow.log_param("batch_size", params.get("batch_size"))
        mlflow.log_param("image_size", params.get("image_size"))

        # Log final metrics from training history
        final_epoch = len(history.history["accuracy"]) - 1
        mlflow.log_metric("train_accuracy", history.history["accuracy"][final_epoch])
        mlflow.log_metric("train_loss", history.history["loss"][final_epoch])
        mlflow.log_metric("val_accuracy", history.history["val_accuracy"][final_epoch])
        mlflow.log_metric("val_loss", history.history["val_loss"][final_epoch])

        # Log the model artifact
        mlflow.log_artifacts(model_path, artifact_path="model")

        # Register model
        model_uri = f"runs:/{mlflow.active_run().info.run_id}/model"
        result = mlflow.register_model(model_uri, MODEL_NAME)

        # Transition to Production
        client = MlflowClient()
        client.transition_model_version_stage(
            name=MODEL_NAME,
            version=result.version,
            stage="Production",
        )

        print(f"Model registered as version {result.version} (Production)")
        return int(result.version)
