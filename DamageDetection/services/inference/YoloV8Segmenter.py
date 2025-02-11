from .BaseModel import BaseModel
from ultralytics import YOLO

class YoloV8Segmenter(BaseModel):

    model = None
    results = None

    def load_model(self, path):
        self.model = YOLO(path)
        print("Segmenter Model Loaded")

    def predict(self, image):
        self.results = self.model(image)
        # Access detections
        for result in self.results:
            detections = result.boxes.data.cpu().numpy()  # Convert to NumPy
        
        returned_list = self.get_summary_list(detections)
        return (returned_list)
    
    def get_summary_list(self,detections):
        class_labels = self.model.names
        summary_list = []
        for detection in detections:
            x_min, y_min, x_max, y_max, confidence, class_id = detection
            x_min, y_min, x_max, y_max = round(float(x_min), 3), round(float(y_min), 3), round(float(x_max), 3), round(float(y_max), 3)
            label = class_labels[class_id]
            summary_list.append(([x_min, y_min, x_max, y_max], label))
        
        return summary_list
