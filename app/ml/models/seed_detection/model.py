"""Paddy Seed Classification Model - MobileNetV2-based CNN"""
import base64
import warnings
from pathlib import Path
from typing import Any, Dict

import cv2
import numpy as np

from app.ml.base import MLModel
from app.utils.exceptions import ModelLoadError, PredictionError, InvalidInputError

# Class labels matching the notebook training (label_dict indices)
LABELS = {
    0: "BG_375",
    1: "Suwadel",
    2: "P_Perumal",
    3: "Background",
}

IMG_SIZE = (224, 224)


class SeedDetectionModel(MLModel):
    """Model for classifying paddy seed images (BG_375, Suwadel, P_Perumal, Background)"""

    def __init__(self) -> None:
        self.model = None
        self._loaded = False

    def load(self, model_path: str) -> None:
        """
        Load the Keras/TensorFlow model from .h5 file.

        Args:
            model_path: Path to the directory containing paddy_seed_classifier_new.h5
        """
        try:
            model_file = Path(model_path) / "paddy_seed_classifier_new.h5"

            if not model_file.exists():
                raise ModelLoadError(f"Model file not found: {model_file}")

            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning, module="tensorflow")
                import tensorflow as tf

                self.model = tf.keras.models.load_model(str(model_file))

            self._loaded = True

        except Exception as e:
            raise ModelLoadError(f"Failed to load seed detection model: {str(e)}")

    def is_loaded(self) -> bool:
        """Check if the model is loaded"""
        return self._loaded

    def _decode_base64_image(self, image_base64: str) -> np.ndarray:
        """
        Decode base64 string to image array (BGR, same as cv2.imread).

        Args:
            image_base64: Base64-encoded image string (with or without data URL prefix)

        Returns:
            numpy array of shape (H, W, 3) in BGR
        """
        # Strip optional data URL prefix (e.g. "data:image/jpeg;base64,")
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]

        try:
            img_bytes = base64.b64decode(image_base64)
        except Exception as e:
            raise InvalidInputError(f"Invalid base64 image data: {str(e)}")

        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            raise InvalidInputError("Could not decode image from base64. Ensure valid image format (JPEG/PNG).")

        return img

    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """
        Preprocess image for model input (same as notebook).

        - Resize to 224x224
        - Normalize to [0, 1]
        - Add batch dimension
        """
        img = cv2.resize(img, IMG_SIZE)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        return img

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify paddy seed image.

        Args:
            input_data: Dict with key "image_base64" (base64-encoded image string)

        Returns:
            Dict with:
            - predicted_class: str (BG_375, Suwadel, P_Perumal, Background)
            - confidence: float
            - class_id: int
        """
        if not self.is_loaded():
            raise PredictionError("Model is not loaded. Call load() first.")

        if "image_base64" not in input_data:
            raise InvalidInputError("Missing required field: image_base64")

        try:
            img = self._decode_base64_image(input_data["image_base64"])
            img_preprocessed = self._preprocess_image(img)

            pred = self.model.predict(img_preprocessed, verbose=0)
            class_id = int(np.argmax(pred[0]))
            confidence = float(np.max(pred[0]))

            predicted_class = LABELS.get(class_id, f"Unknown_{class_id}")

            return {
                "predicted_class": predicted_class,
                "confidence": confidence,
                "class_id": class_id,
            }
        except InvalidInputError:
            raise
        except Exception as e:
            raise PredictionError(f"Failed to predict seed class: {str(e)}")
