from unittest.mock import MagicMock
from services.inference.YoloV8Segmenter import YoloV8Segmenter
import numpy as np

def test_yolov8_segmenter_predict_mocked():
    # Step 1: Create fake detection output (like YOLO format)
    mock_detections = np.array([
        [100, 200, 300, 400, 0.95, 0],  # bbox + confidence + class_id
        [120, 220, 320, 420, 0.90, 1]
    ])

    # Step 2: Instantiate the segmenter
    segmenter = YoloV8Segmenter("mock_model_path.pt")

    # Step 3: Mock the model inside the segmenter
    segmenter.model = MagicMock()
    segmenter.model.names = {0: "dent", 1: "scratch"}

    # Step 4: Mock the result object returned by model(image)
    mock_result = MagicMock()
    mock_result.boxes.data.cpu().numpy.return_value = mock_detections
    segmenter.model.return_value = [mock_result]

    # Step 5: Call predict with any image input (ignored due to mock)
    result = segmenter.predict("dummy_image.jpg")

    # Step 6: Assertions
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0][1] == "dent"
    assert result[1][1] == "scratch"
    assert result[0][0] == [100.0, 200.0, 300.0, 400.0]
