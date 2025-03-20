import boto3
import os
import time
from botocore.exceptions import BotoCoreError, NoCredentialsError
from fastapi import UploadFile
from dotenv import load_dotenv
from PIL import Image
import io
from services.aws.aws_config import s3

# Load environment variables
load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")
BUCKET_REGION = os.getenv("BUCKET_REGION")

async def optimize_image(file: UploadFile):
    """
    Optimize image file by resizing it using PIL (Pillow).
    """
    try:
        image = Image.open(io.BytesIO(await file.read()))
        image.thumbnail((1080, 1920))  # Resize while maintaining aspect ratio

        buffer = io.BytesIO()
        image.save(buffer, format=image.format)
        buffer.seek(0)

        return buffer
    except Exception as e:
        print("Image optimization failed:", e)
        return io.BytesIO(await file.read())  # Return original buffer if optimization fails





async def upload_single_file(file: UploadFile, folder_path: str = None, content_type: str = "application/octet-stream"):
    """
    Upload a single file to S3 with optional folder path.
    """
    try:
        # Ensure content_type is not None
        content_type = content_type if content_type else "application/octet-stream"

        # Generate unique file key
        file_key = f"{folder_path}/{int(time.time())}-{file.filename}" if folder_path else f"{int(time.time())}-{file.filename}"

        # Optimize image if applicable
        buffer = await optimize_image(file) if content_type.startswith("image/") else io.BytesIO(await file.read())

        # Upload file to S3
        s3.upload_fileobj(
            buffer,
            BUCKET_NAME,
            file_key,
            ExtraArgs={"ContentType": content_type}
        )

        # Construct public URL
        file_url = f"https://{BUCKET_NAME}.s3.{BUCKET_REGION}.amazonaws.com/{file_key}"

        print("Upload successful:", file_url)
        return file_url

    except (BotoCoreError, NoCredentialsError) as e:
        print("Error uploading file to S3:", e)
        raise e


async def upload_multiple_files(files: list[UploadFile], folder_path: str = None):
    """
    Upload multiple files to S3.
    """
    file_urls = []
    for file in files:
        file_url = await upload_single_file(file, folder_path)
        file_urls.append(file_url)
    return file_urls

