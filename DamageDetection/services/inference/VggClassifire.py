from .BaseModel import BaseModel
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np

class VggClassifire(BaseModel):

    model = None
    results = None
    class_names = ['minor', 'moderate', 'severe']

    def load_model(self, path):
        self.model = load_model(path)
        print("VGG16 classifier loaded")

    def predict(self, image):
        if self.model is None:
            raise ValueError("Model is not loaded. Call load_model() before prediction.")
        
        predictions = self.model.predict(image)  # Use preprocessed image
        predicted_class_idx = np.argmax(predictions, axis=1)[0]
        predicted_class_name = self.class_names[predicted_class_idx]

        return {
            "class_index": predicted_class_idx,
            "class_name": predicted_class_name,
            "confidence_scores": predictions.tolist()
        }