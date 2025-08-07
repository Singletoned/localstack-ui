import re
from typing import Dict, List, Optional, Tuple

from botocore.exceptions import ClientError

from ..aws_client import AWSClientError, aws_client_factory


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


# Global instance
s3_service = S3Service()