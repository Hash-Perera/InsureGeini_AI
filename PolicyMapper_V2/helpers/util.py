import os
from dotenv import load_dotenv
from external.aws import S3Client
from core.logger import Logger

logger = Logger()

load_dotenv()

s3_client = S3Client(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)
logger.info(f"S3 client initialized")

async def extract_metadata_from_audio_file_url(url: str) -> dict:
    logger.info(f"Extracting metadata from audio file url: {url}")
    try:
        url: list[str] = url.split("/")
        metadata: dict = {
        "base_url": f"{url[0]}//{url[2]}",
        "user_id": url[3],
        "claim_number": url[4],
        "audio_file_name": url[5],
        }
        logger.info(f"Metadata extracted: {metadata}")
        return metadata
    except Exception as e:
        logger.error(f"Error extracting metadata from audio file url: {e}")
        return None

async def download_audio_file(url_metadata: dict, local_path: str) -> str |None:
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        if s3_client.download_file(
            bucket_name=os.getenv("AWS_BUCKET_NAME"),
            s3_key=f"{url_metadata.get('user_id')}/{url_metadata.get('claim_number')}/{url_metadata.get('audio_file_name')}",
            local_path=local_path,
        ):
            return local_path
    except Exception as e:
        logger.error(f"Error downloading audio file: {e}")
        return None

async def upload_pdf_to_s3(pdf_path: str, s3_key: str) -> bool:
    try:
        logger.info(f"Uploading pdf to s3: {pdf_path} to {s3_key}")
        return s3_client.upload_file(
            bucket_name=os.getenv("AWS_BUCKET_NAME"),
            s3_key=s3_key,
            local_path=pdf_path,
        )
    except Exception as e:
        logger.error(f"Error uploading pdf to s3: {e}")
        return False
