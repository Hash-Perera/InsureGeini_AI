from unittest.mock import patch
from services.inference.YoloV8Detector import YoloV8Detector

def test_yolov8_detector():
    mocked_output = [
         ([100.0, 200.0, 300.0, 400.0], "door"),
         ([120.0, 220.0, 320.0, 420.0], "fender")
    ]

    with patch.object(YoloV8Detector, 'predict', return_value=mocked_output):
        detector = YoloV8Detector("mock_model_path.pt")
        result = detector.predict("mock_image.jpg")

        assert result == mocked_output
        assert result[0][1] == "door"
        assert result[1][1] == "fender"
        assert len(result) == 2
        assert result[0][0] == ([100.0, 200.0, 300.0, 400.0])
        assert result[1][0] == ([120.0, 220.0, 320.0, 420.0])