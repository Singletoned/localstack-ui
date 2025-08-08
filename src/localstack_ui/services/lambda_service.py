from typing import Dict, List, Optional

from botocore.exceptions import ClientError

from ..aws_client import aws_client_factory


class LambdaServiceError(Exception):
    """Custom exception for Lambda service operations."""

    pass


class LambdaService:
    """Service for Lambda read-only operations."""

    def __init__(self):
        self.client = aws_client_factory.get_lambda_client()

    def list_functions(self) -> List[Dict]:
        """
        List all Lambda functions.

        Returns:
            List of function dictionaries with basic information
        """
        try:
            response = self.client.list_functions()
            functions = []

            for func in response.get("Functions", []):
                functions.append(
                    {
                        "function_name": func["FunctionName"],
                        "runtime": func.get("Runtime", "Unknown"),
                        "memory_size": func.get("MemorySize", 0),
                        "timeout": func.get("Timeout", 0),
                        "last_modified": func.get("LastModified", ""),
                        "description": func.get("Description", ""),
                        "handler": func.get("Handler", ""),
                        "role": func.get("Role", ""),
                        "code_size": func.get("CodeSize", 0),
                        "state": func.get("State", "Unknown"),
                        "version": func.get("Version", "$LATEST"),
                    }
                )

            # Sort by function name for consistent display
            functions.sort(key=lambda x: x["function_name"].lower())
            return functions

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            raise LambdaServiceError(f"Failed to list Lambda functions ({error_code}): {e}")
        except Exception as e:
            raise LambdaServiceError(f"Unexpected error listing Lambda functions: {e}")

    def get_function(self, function_name: str) -> Optional[Dict]:
        """
        Get detailed information about a Lambda function.

        Args:
            function_name: Name of the function

        Returns:
            Function details dictionary or None if not found
        """
        try:
            response = self.client.get_function(FunctionName=function_name)
            config = response.get("Configuration", {})
            code = response.get("Code", {})

            function_info = {
                "function_name": config.get("FunctionName", ""),
                "function_arn": config.get("FunctionArn", ""),
                "runtime": config.get("Runtime", "Unknown"),
                "role": config.get("Role", ""),
                "handler": config.get("Handler", ""),
                "description": config.get("Description", ""),
                "timeout": config.get("Timeout", 0),
                "memory_size": config.get("MemorySize", 0),
                "last_modified": config.get("LastModified", ""),
                "code_sha256": config.get("CodeSha256", ""),
                "version": config.get("Version", "$LATEST"),
                "state": config.get("State", "Unknown"),
                "state_reason": config.get("StateReason", ""),
                "state_reason_code": config.get("StateReasonCode", ""),
                "package_type": config.get("PackageType", "Zip"),
                "architectures": config.get("Architectures", []),
                "environment_variables": config.get("Environment", {}).get("Variables", {}),
                "code_size": config.get("CodeSize", 0),
                "repository_type": code.get("RepositoryType", ""),
                "location": code.get("Location", ""),
            }

            return function_info

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "ResourceNotFoundException":
                return None
            raise LambdaServiceError(
                f"Failed to get Lambda function '{function_name}' ({error_code}): {e}"
            )
        except Exception as e:
            raise LambdaServiceError(
                f"Unexpected error getting Lambda function '{function_name}': {e}"
            )

    def format_memory_size(self, memory_mb: int) -> str:
        """Format memory size for display."""
        if memory_mb < 1024:
            return f"{memory_mb} MB"
        else:
            return f"{memory_mb / 1024:.1f} GB"

    def format_timeout(self, timeout_seconds: int) -> str:
        """Format timeout for display."""
        if timeout_seconds < 60:
            return f"{timeout_seconds}s"
        elif timeout_seconds < 3600:
            minutes = timeout_seconds // 60
            seconds = timeout_seconds % 60
            if seconds == 0:
                return f"{minutes}m"
            else:
                return f"{minutes}m {seconds}s"
        else:
            hours = timeout_seconds // 3600
            remaining = timeout_seconds % 3600
            minutes = remaining // 60
            return f"{hours}h {minutes}m"

    def format_code_size(self, size_bytes: int) -> str:
        """Format code size for display."""
        if size_bytes == 0:
            return "0 B"

        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


# Global instance
lambda_service = LambdaService()
