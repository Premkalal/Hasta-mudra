"""
models/model_loader.py — ML Model Loader (Semester 4)
Placeholder for loading trained scikit-learn or TensorFlow models.
"""

from pathlib import Path


def load_model(model_path: str):
    """
    Load a serialised ML model from disk.
    Implement in Semester 4 once training pipeline is ready.

    Supported formats:
        .pkl  → scikit-learn (joblib)
        .h5   → Keras/TensorFlow
        .onnx → ONNX Runtime

    Example:
        model = load_model("models/mudra_classifier.pkl")
        label = model.predict([feature_vector])
    """
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    suffix = path.suffix.lower()

    if suffix == ".pkl":
        import joblib
        return joblib.load(path)

    if suffix in (".h5", ".keras"):
        from tensorflow import keras
        return keras.models.load_model(path)

    if suffix == ".onnx":
        import onnxruntime as ort
        return ort.InferenceSession(str(path))

    raise ValueError(f"Unsupported model format: {suffix}")
