import time
from typing import Optional

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError

from .settings import settings


class AWSClientError(Exception):
    """Custom exception for AWS client errors."""

    pass


class AWSClientFactory:
    """Factory for creating AWS service clients configured for LocalStack."""

    def __init__(self):
        self._clients = {}

    def _create_client(self, service_name: str):
        """Create a boto3 client for the specified service."""
        try:
            client = boto3.client(
                service_name,
                endpoint_url=settings.LOCALSTACK_ENDPOINT,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            return client
        except (ClientError, NoCredentialsError) as e:
            raise AWSClientError(f"Failed to create {service_name} client: {e}")

    def get_s3_client(self):
        """Get or create S3 client."""
        if "s3" not in self._clients:
            self._clients["s3"] = self._create_client("s3")
        return self._clients["s3"]

    def get_lambda_client(self):
        """Get or create Lambda client."""
        if "lambda" not in self._clients:
            self._clients["lambda"] = self._create_client("lambda")
        return self._clients["lambda"]

    def get_stepfunctions_client(self):
        """Get or create Step Functions client."""
        if "stepfunctions" not in self._clients:
            self._clients["stepfunctions"] = self._create_client("stepfunctions")
        return self._clients["stepfunctions"]

    def health_check(self, max_retries: int = 3, retry_delay: float = 1.0) -> dict:
        """
        Check the health of LocalStack services.

        Returns:
            dict: Health status for each service
        """
        services = {
            "s3": self.get_s3_client,
            "lambda": self.get_lambda_client,
            "stepfunctions": self.get_stepfunctions_client,
        }

        health_status = {}

        for service_name, client_factory in services.items():
            for attempt in range(max_retries):
                try:
                    client = client_factory()

                    if service_name == "s3":
                        # Test S3 by listing buckets
                        client.list_buckets()
                    elif service_name == "lambda":
                        # Test Lambda by listing functions
                        client.list_functions(MaxItems=1)
                    elif service_name == "stepfunctions":
                        # Test Step Functions by listing state machines
                        client.list_state_machines(maxResults=1)

                    health_status[service_name] = {
                        "status": "healthy",
                        "error": None,
                        "attempt": attempt + 1,
                    }
                    break

                except EndpointConnectionError as e:
                    error_msg = f"Cannot connect to LocalStack endpoint: {e}"
                    if attempt == max_retries - 1:
                        health_status[service_name] = {
                            "status": "unhealthy",
                            "error": error_msg,
                            "attempt": attempt + 1,
                        }
                    else:
                        time.sleep(retry_delay)

                except ClientError as e:
                    error_code = e.response.get("Error", {}).get("Code", "Unknown")
                    error_msg = f"AWS API error ({error_code}): {e}"
                    if attempt == max_retries - 1:
                        health_status[service_name] = {
                            "status": "unhealthy",
                            "error": error_msg,
                            "attempt": attempt + 1,
                        }
                    else:
                        time.sleep(retry_delay)

                except Exception as e:
                    error_msg = f"Unexpected error: {e}"
                    if attempt == max_retries - 1:
                        health_status[service_name] = {
                            "status": "unhealthy",
                            "error": error_msg,
                            "attempt": attempt + 1,
                        }
                    else:
                        time.sleep(retry_delay)

        return health_status

    def is_healthy(self) -> bool:
        """Check if all services are healthy."""
        health_status = self.health_check()
        return all(service["status"] == "healthy" for service in health_status.values())


# Global instance
aws_client_factory = AWSClientFactory()