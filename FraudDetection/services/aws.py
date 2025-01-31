# import boto3
# import os

# def download_file_from_s3(object_key: str ) -> str:
#     """
#     Downloads a file from S3 and returns the local file path.

#     Args:
#         object_key (str): Key (path) of the file in S3.
#         local_dir (str): Directory where the file will be saved (default: "temp").

#     Returns:
#         str: The local file path of the downloaded file.
#     """
#     local_dir: str = "temp"
#     # Create the directory if it doesn't exist
#     os.makedirs(local_dir, exist_ok=True)

#     # Generate the local file path
#     local_file_path = os.path.join(local_dir, os.path.basename(object_key))

#     # Initialize the S3 client
#     s3 = boto3.client("s3", region_name="us-east-1")  # Replace "your-region" with your AWS region

#     try:
#         # Download the file from S3
#         s3.download_file('insure-geini-s3', object_key, local_file_path)
#         print(f"File downloaded: {local_file_path}")
#         return local_file_path
#     except Exception as e:
#         raise Exception(f"Failed to download file from S3: {e}")


import requests
import os

def download_file_from_url(file_url: str, local_dir: str = "temp") -> str:
    """
    Downloads a file from a public URL and saves it locally.

    Args:
        file_url (str): Public URL of the file.
        local_dir (str): Directory where the file will be saved (default: "temp").

    Returns:
        str: The local file path of the downloaded file.
    """
    # Create the directory if it doesn't exist
    os.makedirs(local_dir, exist_ok=True)

    # Extract the file name from the URL
    file_name = os.path.basename(file_url)

    # Create the local file path
    local_file_path = os.path.join(local_dir, file_name)

    try:
        # Send a GET request to download the file
        response = requests.get(file_url, stream=True)
        response.raise_for_status()  # Raise an error for HTTP issues

        # Write the file locally
        with open(local_file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"File downloaded: {local_file_path}")
        return local_file_path
    except Exception as e:
        raise Exception(f"Failed to download file from URL: {e}")
