from inference.YoloV8Detector import YoloV8Detector
from inference.YoloV8Segmenter import YoloV8Segmenter
from inference.VggClassifire import VggClassifire

class ModelFactory:

    @staticmethod
    def create_model(model_type, model_path):
        """Creates an instance of an AI model based on the type."""
        if model_type == "VggClassifire":
            model = VggClassifire(model_path)
        elif model_type == "YoloV8Detector":
            model = YoloV8Detector(model_path)
        elif model_type == "YoloV8Segmenter":
            model = YoloV8Segmenter(model_path)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        model.load_model()
        return model
    