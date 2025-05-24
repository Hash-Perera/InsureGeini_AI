from unittest.mock import MagicMock
from services.inference.VggClassifire import VggClassifire
import numpy as np

def test_vgg_classifier_predict_mocked():
    # Create fake prediction output (e.g., confidence scores for 3 classes)
    mock_prediction = np.array([[0.1, 0.8, 0.1]])  # means 'moderate'

    # Instantiate classifier
    classifier = VggClassifire("mock_model_path.h5")

    # Inject a mock model into the classifier
    classifier.model = MagicMock()
    classifier.model.predict.return_value = mock_prediction

    # Mock image input (doesn't matter since model.predict is mocked)
    mock_image_input = "dummy_tensor"

    result = classifier.predict(mock_image_input)

    # Assertions
    assert isinstance(result, dict)
    assert result["class_index"] == 1
    assert result["class_name"] == "moderate"
    assert isinstance(result["confidence_scores"], list)
    assert result["confidence_scores"][0][1] == 0.8
