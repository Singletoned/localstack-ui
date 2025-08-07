import re
from typing import Dict, List, Optional, Tuple

from botocore.exceptions import ClientError

from ..aws_client import aws_client_factory
from ..settings import settings


class S3ServiceError(Exception):
    """Custom exception for S3 service operations."""

    pass


class S3Service:
    """Service for managing S3 operations."""

    def __init__(self):
        self.client = aws_client_factory.get_s3_client()

    def list_buckets(self) -> List[Dict]:
        """
        List all S3 buckets.

        Returns:
            List of bucket dictionaries with name and creation_date
        """
        try:
            response = self.client.list_buckets()
            buckets = []

            for bucket in response.get("Buckets", []):
                buckets.append(
                    {
                        "name": bucket["Name"],
                        "creation_date": bucket["CreationDate"],
                    }
                )

            # Sort by name for consistent display
            buckets.sort(key=lambda x: x["name"])
            return buckets

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            raise S3ServiceError(f"Failed to list buckets ({error_code}): {e}")
        except Exception as e:
            raise S3ServiceError(f"Unexpected error listing buckets: {e}")

    def create_bucket(self, bucket_name: str) -> Tuple[bool, Optional[str]]:
        """
        Create an S3 bucket.

        Args:
            bucket_name: Name of the bucket to create

        Returns:
            Tuple of (success, error_message)
        """
        # Validate bucket name
        validation_error = self._validate_bucket_name(bucket_name)
        if validation_error:
            return False, validation_error

        try:
            self.client.create_bucket(Bucket=bucket_name)
            return True, None

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "BucketAlreadyExists":
                return False, f"Bucket '{bucket_name}' already exists"
            elif error_code == "BucketAlreadyOwnedByYou":
                return False, f"You already own bucket '{bucket_name}'"
            else:
                return False, f"Failed to create bucket ({error_code}): {e}"
        except Exception as e:
            return False, f"Unexpected error creating bucket: {e}"

    def delete_bucket(self, bucket_name: str) -> Tuple[bool, Optional[str]]:
        """
        Delete an S3 bucket.

        Args:
            bucket_name: Name of the bucket to delete

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Check if bucket exists and is empty
            try:
                objects_response = self.client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                if objects_response.get("Contents"):
                    return False, f"Bucket '{bucket_name}' is not empty"
            except ClientError:
                # Bucket might not exist, let the delete operation handle it
                pass

            # Delete the bucket
            self.client.delete_bucket(Bucket=bucket_name)
            return True, None

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "NoSuchBucket":
                return False, f"Bucket '{bucket_name}' does not exist"
            elif error_code == "BucketNotEmpty":
                return False, f"Bucket '{bucket_name}' is not empty"
            else:
                return False, f"Failed to delete bucket ({error_code}): {e}"
        except Exception as e:
            return False, f"Unexpected error deleting bucket: {e}"

    def _validate_bucket_name(self, bucket_name: str) -> Optional[str]:
        """
        Validate S3 bucket name according to AWS rules.

        Args:
            bucket_name: Name to validate

        Returns:
            Error message if invalid, None if valid
        """
        if not bucket_name:
            return "Bucket name cannot be empty"

        if len(bucket_name) < 3 or len(bucket_name) > 63:
            return "Bucket name must be between 3 and 63 characters long"

        # Check if name starts and ends with lowercase letter or number
        if not re.match(r"^[a-z0-9]", bucket_name):
            return "Bucket name must start with a lowercase letter or number"

        if not re.match(r"[a-z0-9]$", bucket_name):
            return "Bucket name must end with a lowercase letter or number"

        # Check if name contains only allowed characters
        if not re.match(r"^[a-z0-9.-]+$", bucket_name):
            return "Bucket name can only contain lowercase letters, numbers, hyphens, and periods"

        # Check for consecutive periods
        if ".." in bucket_name:
            return "Bucket name cannot contain consecutive periods"

        # Check for period-hyphen combinations
        if ".-" in bucket_name or "-." in bucket_name:
            return "Bucket name cannot contain periods adjacent to hyphens"

        # Check if it looks like an IP address
        if re.match(r"^\d+\.\d+\.\d+\.\d+$", bucket_name):
            return "Bucket name cannot be formatted as an IP address"

        return None

    def list_objects(self, bucket_name: str, prefix: str = "") -> List[Dict]:
        """
        List objects in an S3 bucket.

        Args:
            bucket_name: Name of the bucket
            prefix: Prefix to filter objects (for folders)

        Returns:
            List of object dictionaries with key, size, last_modified
        """
        try:
            response = self.client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            objects = []

            for obj in response.get("Contents", []):
                objects.append(
                    {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                        "etag": obj["ETag"].strip('"'),
                    }
                )

            # Sort by key for consistent display
            objects.sort(key=lambda x: x["key"])
            return objects

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            raise S3ServiceError(f"Failed to list objects in '{bucket_name}' ({error_code}): {e}")
        except Exception as e:
            raise S3ServiceError(f"Unexpected error listing objects in '{bucket_name}': {e}")

    def upload_file(
        self, bucket_name: str, file_key: str, file_data: bytes
    ) -> Tuple[bool, Optional[str]]:
        """
        Upload a file to an S3 bucket.

        Args:
            bucket_name: Name of the bucket
            file_key: Key (name) of the file
            file_data: Binary data of the file

        Returns:
            Tuple of (success, error_message)
        """
        # Validate file size
        if len(file_data) > settings.MAX_FILE_SIZE_BYTES:
            error_msg = (
                f"File size ({len(file_data)} bytes) exceeds limit of {settings.MAX_FILE_SIZE_MB}MB"
            )
            return False, error_msg

        # Validate file key
        if not file_key or file_key.strip() == "":
            return False, "File name cannot be empty"

        try:
            self.client.put_object(Bucket=bucket_name, Key=file_key, Body=file_data)
            return True, None

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "NoSuchBucket":
                return False, f"Bucket '{bucket_name}' does not exist"
            else:
                return False, f"Failed to upload file ({error_code}): {e}"
        except Exception as e:
            return False, f"Unexpected error uploading file: {e}"

    def download_file(
        self, bucket_name: str, file_key: str
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Download a file from an S3 bucket.

        Args:
            bucket_name: Name of the bucket
            file_key: Key (name) of the file

        Returns:
            Tuple of (success, file_data, error_message)
        """
        try:
            response = self.client.get_object(Bucket=bucket_name, Key=file_key)
            file_data = response["Body"].read()
            return True, file_data, None

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "NoSuchKey":
                return False, None, f"File '{file_key}' not found in bucket '{bucket_name}'"
            elif error_code == "NoSuchBucket":
                return False, None, f"Bucket '{bucket_name}' does not exist"
            else:
                return False, None, f"Failed to download file ({error_code}): {e}"
        except Exception as e:
            return False, None, f"Unexpected error downloading file: {e}"

    def delete_file(self, bucket_name: str, file_key: str) -> Tuple[bool, Optional[str]]:
        """
        Delete a file from an S3 bucket.

        Args:
            bucket_name: Name of the bucket
            file_key: Key (name) of the file

        Returns:
            Tuple of (success, error_message)
        """
        try:
            self.client.delete_object(Bucket=bucket_name, Key=file_key)
            return True, None

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "NoSuchBucket":
                return False, f"Bucket '{bucket_name}' does not exist"
            else:
                return False, f"Failed to delete file ({error_code}): {e}"
        except Exception as e:
            return False, f"Unexpected error deleting file: {e}"

    def get_file_info(
        self, bucket_name: str, file_key: str
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Get metadata about a file in an S3 bucket.

        Args:
            bucket_name: Name of the bucket
            file_key: Key (name) of the file

        Returns:
            Tuple of (success, file_info, error_message)
        """
        try:
            response = self.client.head_object(Bucket=bucket_name, Key=file_key)
            file_info = {
                "size": response.get("ContentLength", 0),
                "last_modified": response.get("LastModified"),
                "content_type": response.get("ContentType", "application/octet-stream"),
                "etag": response.get("ETag", "").strip('"'),
            }
            return True, file_info, None

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "NotFound":
                return False, None, f"File '{file_key}' not found in bucket '{bucket_name}'"
            elif error_code == "NoSuchBucket":
                return False, None, f"Bucket '{bucket_name}' does not exist"
            else:
                return False, None, f"Failed to get file info ({error_code}): {e}"
        except Exception as e:
            return False, None, f"Unexpected error getting file info: {e}"

    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"

        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


# Global instance
s3_service = S3Service()
