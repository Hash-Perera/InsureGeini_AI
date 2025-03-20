import boto3
import io
from PIL import Image
import requests

# AWS S3 Configuration
S3_BUCKET_NAME = "insure-geini-s3"
AWS_REGION = "us-east-1"
AWS_ACCESS_KEY = "your-access-key"
AWS_SECRET_KEY = "your-secret-key"

# Initialize S3 Client
s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# Function to Extract S3 Key and Download Image
def download_image_from_s3(image_url: str):
    """Extracts the S3 key from the image URL and downloads the image."""
    try:
        # Extract S3 Key from URL
        s3_key = "/".join(image_url.split("/")[3:])
        
        # Download image from S3
        s3_response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        image_bytes = s3_response["Body"].read()

        # Open Image using PIL
        image = Image.open(io.BytesIO(image_bytes))
        return image

    except Exception as e:
        return {"error": str(e)}
    
def get_image_from_s3(image_url: str):
    try:
        response = requests.get(image_url, timeout=10)  # Fetch image from URL
        response.raise_for_status()  # Check for HTTP errors
        image_bytes = response.content  # Get image data
        image = Image.open(io.BytesIO(image_bytes))  # Open image with PIL

        return image
    
    except Exception as e:
        return {"error": str(e)}