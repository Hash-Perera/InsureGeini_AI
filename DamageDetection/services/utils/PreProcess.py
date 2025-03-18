#Add the preprocessing code
#Search what preprocessings are need
import io
import cv2
import numpy as np
import matplotlib.pyplot as plt
import boto3
import io
from PIL import Image
from fastapi import UploadFile
from utils.AwsFiles.s3_upload import upload_single_file
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.vgg16 import preprocess_input

class PreProcess:
    @staticmethod
    def preprocess(image):

        #Pre processing for VGG16 classification
        IMG_SIZE = (224, 224)

        # ✅ Convert PIL Image to `io.BytesIO` before passing to `load_img`
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")  # ✅ Save image in memory as bytes
        image_bytes.seek(0)  # ✅ Move cursor to the beginning of the file

        img = load_img(image_bytes, target_size=IMG_SIZE)
        img_array = img_to_array(img) / 255.0  # Normalize
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension

        #Add pre processing for the yolov8 if needed

        return {
            "tensorflow" : img_array
        }
    
    @staticmethod
    # Function to crop detected damaged parts before classification
    def preprocess_cropped_images(image_path, detections, padding_ratio=0.4):

        
        # Load the original image
        # image = cv2.imread(image_path)
        # ✅ Convert PIL image to OpenCV format (NumPy array)
        image = np.array(image_path)  # ✅ Convert to NumPy array
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # ✅ Convert RGB to BGR (OpenCV format)
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert for correct display
        original_height, original_width = image.shape[:2]

        cropped_data = []  # Store preprocessed images

        for i, (bbox, part_label) in enumerate(detections):
            x_min, y_min, x_max, y_max = bbox  # Extract bounding box

            # Compute padding (percentage of bounding box size)
            padding_x = int((x_max - x_min) * padding_ratio)
            padding_y = int((y_max - y_min) * padding_ratio)

            # Expand bounding box with padding, ensuring it stays within image limits
            x_min = max(0, x_min - padding_x)
            y_min = max(0, y_min - padding_y)
            x_max = min(original_width, x_max + padding_x)
            y_max = min(original_height, y_max + padding_y)

            x_min, y_min, x_max, y_max = int(x_min), int(y_min), int(x_max), int(y_max)

            # Crop the damaged part from the image
            cropped_part = image[y_min:y_max, x_min:x_max]

            # Resize for VGG16 input (224x224)
            resized_part = cv2.resize(cropped_part, (224, 224))

            # Convert image for VGG16 model
            image_array = img_to_array(resized_part)
            image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension
            image_array = preprocess_input(image_array)  # Normalize for VGG16

            # Store results for classification
            cropped_data.append((image_array, part_label, cropped_part))  # Include original cropped image for visualization

        return cropped_data

    @staticmethod
    def upload_to_s3(image_np, file_name):
        pass


    @staticmethod
    async def upload_cropped_images(cropped_images,claimId):
        uploaded_images = []

        for i, (image_array, part_label, cropped_part) in enumerate(cropped_images):
            # Convert BGR (OpenCV) to RGB for PIL
            cropped_part_rgb = cv2.cvtColor(cropped_part, cv2.COLOR_BGR2RGB)

            # Save the cropped face to a temporary file
            cropped_path = "utils/temp/croppped_part.jpg"
            cv2.imwrite(cropped_path, cropped_part_rgb)

            # Open the saved image file and read it as bytes
            with open(cropped_path, "rb") as file:
                image_bytes = io.BytesIO(file.read())

            # Create an UploadFile object
            cropped_face_file = UploadFile(filename="cropped_damaged_part.jpg", file=image_bytes)

            folder_path = f"cropped_parts/{claimId}/{part_label}_{i}"
            # Upload to S3
            s3_url = await upload_single_file(cropped_face_file, folder_path)

            print(s3_url)

            # # Define file name and upload
            # file_name = f"cropped_parts/{part_label}_{i}.jpg"
            # #s3_url = PreProcess.upload_to_s3(cropped_part_rgb, file_name)
            # s3_url = f"https://s3.amazonaws.com/{file_name}"

            uploaded_images.append((s3_url, part_label))

        return uploaded_images

