import cv2
import numpy as np

# Define HSV color ranges
COLOR_RANGES = {
    "red": [(0, 100, 50), (10, 255, 255)],
    "red_alt": [(170, 100, 50), (180, 255, 255)],  
    "blue": [(90, 100, 50), (130, 255, 255)],  
    "green": [(35, 100, 50), (85, 255, 255)],  
    "white": [(0, 0, 200), (180, 40, 255)],  
    "black": [(0, 0, 0), (180, 255, 50)],  
    "yellow": [(20, 100, 100), (35, 255, 255)],  
    "gray": [(0, 0, 50), (180, 20, 200)],  
    "silver": [(0, 0, 100), (180, 20, 255)]
}

def preprocess_image(image):
    """ Apply advanced preprocessing techniques to enhance color detection. """

    # Convert to LAB color space for better color representation
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to the L channel
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))

    # Convert back to BGR
    enhanced_image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # Apply Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(enhanced_image, (5,5), 0)

    return blurred

def detect_vehicle_color(image_path):
    """ Detect the dominant color of the vehicle by analyzing the center area of the image with preprocessing. """
    
    # Read image
    image = cv2.imread(image_path)

    if image is None:
        return "error: invalid image"

    # Get image dimensions
    height, width, _ = image.shape

    # Define center region (50% width and height)
    center_x, center_y = width // 2, height // 2
    region_width, region_height = width // 2, height // 2

    # Crop the center area
    x1, y1 = center_x - region_width // 2, center_y - region_height // 2
    x2, y2 = center_x + region_width // 2, center_y + region_height // 2
    cropped_image = image[y1:y2, x1:x2]

    # Apply preprocessing
    processed_image = preprocess_image(cropped_image)

    # Convert processed image to HSV
    hsv = cv2.cvtColor(processed_image, cv2.COLOR_BGR2HSV)

    # Check each color range
    for color_name, (lower, upper) in COLOR_RANGES.items():
        lower = np.array(lower, dtype=np.uint8)
        upper = np.array(upper, dtype=np.uint8)

        # Create a mask for the color
        mask = cv2.inRange(hsv, lower, upper)

        # Calculate the percentage of the detected color in the center region
        percentage = (np.count_nonzero(mask) / mask.size) * 100

        if percentage > 20:  # If more than 20% of the center region matches the color
            return color_name

    return "Unknown"
