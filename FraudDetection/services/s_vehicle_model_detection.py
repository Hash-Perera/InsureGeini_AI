# import tensorflow as tf
# import numpy as np
# import io
# from PIL import Image

# # Constants
# IMAGE_HEIGHT, IMAGE_WIDTH = 224, 224  # Ensure this matches your model's input size
# CLASS_NAMES = ['Fit', 'Vezel', 'WagonR']  # Replace with your class names

# # Load the trained model
# model = tf.keras.models.load_model('./ML_Models/ModelCNN_V4.keras')  # Update with your model's path

# # Function to preprocess input images
# def preprocess_image(image: Image.Image):
#     """
#     Preprocess an input image for model prediction:
#     - Resizes it to match the model input size.
#     - Normalizes pixel values.
#     """
#     image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT))  # Resize image
#     image = np.array(image) / 255.0  # Normalize pixel values to [0, 1]
#     image = np.expand_dims(image, axis=0)  # Add batch dimension
#     return image

# # Service layer function for prediction
# def predict_vehicle_class(image: Image.Image):
#     """
#     Processes an image and returns the predicted class with confidence.
#     """
#     processed_image = preprocess_image(image)
#     predictions = model.predict(processed_image)
#     predicted_class = CLASS_NAMES[np.argmax(predictions)]
#     confidence = float(np.max(predictions) * 100)
#     return {"predicted_class": predicted_class, "confidence": confidence}