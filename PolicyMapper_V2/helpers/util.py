import os
from dotenv import load_dotenv
from external.aws import S3Client

load_dotenv()

s3_client = S3Client(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

async def extract_metadata_from_audio_file_url(url: str) -> dict:
    url: list[str] = url.split("/")
    metadata: dict = {
        "base_url": f"{url[0]}//{url[2]}",
        "user_id": url[3],
        "claim_number": url[4],
        "audio_file_name": url[5],
    }
    return metadata

async def download_audio_file(url_metadata: dict, local_path: str) -> str |None:
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    if s3_client.download_file(
        bucket_name=os.getenv("AWS_BUCKET_NAME"),
        s3_key=f"{url_metadata.get('user_id')}/{url_metadata.get('claim_number')}/{url_metadata.get('audio_file_name')}",
        local_path=local_path,
    ):
        return local_path
    return None

