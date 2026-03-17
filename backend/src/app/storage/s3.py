import os
import aioboto3
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict
from app.config import BaseAPIConfig

class S3BucketManager:
    """
    Manages connections and transactions for AWS S3 Storage using boto3/aioboto3.
    It's used to push temporal logic out of local volumes.
    """
    def __init__(self):
        settings = BaseAPIConfig.get_settings()
        self.bucket_name = settings.aws_s3_bucket_name
        self.region = settings.aws_region
        
        # In a real environment, rely on IAM Roles rather than hardcoded keys.
        self.session = aioboto3.Session(
            aws_access_key_id=settings.aws_access_key_id if settings.aws_access_key_id else None,
            aws_secret_access_key=settings.aws_secret_access_key if settings.aws_secret_access_key else None,
            region_name=self.region
        )
        
        # Sync boto3 client for quick synchronous methods if needed (e.g., presigned URLs generation is locally computed)
        self.sync_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id if settings.aws_access_key_id else None,
            aws_secret_access_key=settings.aws_secret_access_key if settings.aws_secret_access_key else None,
            region_name=self.region,
            config=boto3.session.Config(signature_version='s3v4')
        )

    async def upload_file_to_s3(self, local_file_path: str, object_name: Optional[str] = None, metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Uploads local raw or processed files directly to S3.
        """
        if object_name is None:
            object_name = os.path.basename(local_file_path)

        extra_args = {"ServerSideEncryption": "AES256"}
        if metadata:
            extra_args["Metadata"] = metadata

        try:
            async with self.session.client('s3') as s3:
                await s3.upload_file(local_file_path, self.bucket_name, object_name, ExtraArgs=extra_args)
            return f"s3://{self.bucket_name}/{object_name}"
        except ClientError as e:
            print(f"Error uploading file {local_file_path} to S3: {e}")
            raise

    def generate_presigned_url(self, object_name: str, expiration_seconds: int = 3600) -> Optional[str]:
        """
        Generates a temporary Pre-Signed URL so the frontend or external API
        can download/view the invoice securely.
        """
        try:
            response = self.sync_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_name
                },
                ExpiresIn=expiration_seconds
            )
            return response
        except ClientError as e:
            print(f"Error generating presigned URL for {object_name}: {e}")
            return None

    async def delete_blob_s3(self, object_name: str) -> bool:
        """
        Deletes standard processed blocks from the bucket.
        """
        try:
            async with self.session.client('s3') as s3:
                await s3.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError as e:
            print(f"Error deleting blob {object_name}: {e}")
            return False
