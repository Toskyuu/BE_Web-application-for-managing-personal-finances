from minio import Minio
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the Minio client with credentials from environment variables
minio_client = Minio(
    "minio:9000",  # The Minio service is running on port 9000 in docker-compose
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False  # Disable SSL, as you're using it locally
)

# Function to create a bucket if it doesn't exist
def create_bucket(bucket_name: str):
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created")
    else:
        print(f"Bucket '{bucket_name}' already exists")
