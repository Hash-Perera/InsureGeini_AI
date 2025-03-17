import boto3
import logging
from botocore.exceptions import ClientError
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class S3Client:
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, region_name='us-east-1'):
        """
        Initialize S3 client with optional credentials
        If credentials are not provided, boto3 will look for credentials in the default locations
        (environment variables, AWS credentials file, or IAM role)
        """
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    def download_file(self, bucket_name: str, s3_key: str, local_path: str) -> bool:
        """
        Download a file from S3
        
        Args:
            bucket_name (str): Name of the S3 bucket
            s3_key (str): Path to the file in S3
            local_path (str): Local path where the file should be saved
            
        Returns:
            bool: True if download was successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Download the file
            self.s3_client.download_file(bucket_name, s3_key, local_path)
            logger.info(f"Successfully downloaded {s3_key} from {bucket_name} to {local_path}")
            return True
            
        except ClientError as e:
            logger.error(f"Error downloading file from S3: {e}")
            return False

    def download_directory(self, bucket_name: str, prefix: str, local_dir: str) -> bool:
        """
        Download all files from an S3 directory
        
        Args:
            bucket_name (str): Name of the S3 bucket
            prefix (str): S3 prefix (directory) to download from
            local_dir (str): Local directory to save files to
            
        Returns:
            bool: True if all downloads were successful, False if any failed
        """
        try:
            # Create local directory if it doesn't exist
            Path(local_dir).mkdir(parents=True, exist_ok=True)
            
            # List all objects in the prefix
            paginator = self.s3_client.get_paginator('list_objects_v2')
            objects = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
            
            success = True
            for page in objects:
                if 'Contents' not in page:
                    continue
                    
                for obj in page['Contents']:
                    # Skip if the object is a directory
                    if obj['Key'].endswith('/'):
                        continue
                        
                    # Calculate relative path
                    relative_path = obj['Key'][len(prefix):].lstrip('/')
                    local_file_path = str(Path(local_dir) / relative_path)
                    
                    # Ensure the directory exists
                    Path(local_file_path).parent.mkdir(parents=True, exist_ok=True)
                    
                    # Download the file
                    if not self.download_file(bucket_name, obj['Key'], local_file_path):
                        success = False
                        
            return success
            
        except ClientError as e:
            logger.error(f"Error downloading directory from S3: {e}")
            return False

    def list_files(self, bucket_name: str, prefix: str = '') -> list:
        """
        List all files in an S3 bucket with given prefix
        
        Args:
            bucket_name (str): Name of the S3 bucket
            prefix (str): S3 prefix to list files from
            
        Returns:
            list: List of file keys in the bucket/prefix
        """
        try:
            files = []
            paginator = self.s3_client.get_paginator('list_objects_v2')
            objects = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
            
            for page in objects:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        if not obj['Key'].endswith('/'):  # Skip directories
                            files.append(obj['Key'])
            
            return files
            
        except ClientError as e:
            logger.error(f"Error listing files from S3: {e}")
            return []
