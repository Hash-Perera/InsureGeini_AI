from BaseModel import BaseModel
from ultralytics import YOLO

class YoloV8Detector(BaseModel):

    model = None
    results = None

    def load_model(self, path):
        self.model = YOLO(path)
        print("Detector Model Loaded")

#Remaining filter out and return only the required, search what is only needed.
    def predict(self, image):
        self.results = self.model(image)
        #print(self.results)
        return {"detections": "Object detection results"}
    