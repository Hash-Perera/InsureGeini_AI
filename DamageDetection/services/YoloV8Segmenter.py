from BaseModel import BaseModel
from ultralytics import YOLO

class YoloV8Segmenter(BaseModel):

    model = None
    results = None

    def load_model(self, path):
        self.model = YOLO(path)
        print("Segmenter Model Loaded")

    def predict(self, image):
        self.results = self.model(image)
        #print(self.results)
        return("Segmenter model results")
