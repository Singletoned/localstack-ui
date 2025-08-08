import json
from datetime import datetime
from typing import Dict, List, Optional

from botocore.exceptions import ClientError

from ..aws_client import aws_client_factory


class StepFunctionsServiceError(Exception):
    """Custom exception for Step Functions service operations."""

    pass


class StepFunctionsService:
    """Service for Step Functions read-only operations."""

    def __init__(self):
        self.client = aws_client_factory.get_stepfunctions_client()

    def list_state_machines(self) -> List[Dict]:
        """
        List all Step Functions state machines.

        Returns:
            List of state machine dictionaries with basic information
        """
        try:
            response = self.client.list_state_machines()
            state_machines = []

            for sm in response.get("stateMachines", []):
                state_machines.append(
                    {
                        "name": sm.get("name", ""),
                        "arn": sm.get("stateMachineArn", ""),
                        "type": sm.get("type", "STANDARD"),
                        "status": sm.get("status", "ACTIVE"),
                        "creation_date": sm.get("creationDate", ""),
                    }
                )

            # Sort by name for consistent display
            state_machines.sort(key=lambda x: x["name"].lower())
            return state_machines

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            raise StepFunctionsServiceError(f"Failed to list state machines ({error_code}): {e}")
        except Exception as e:
            raise StepFunctionsServiceError(f"Unexpected error listing state machines: {e}")

    def describe_state_machine(self, state_machine_arn: str) -> Optional[Dict]:
        """
        Get detailed information about a Step Functions state machine.

        Args:
            state_machine_arn: ARN of the state machine

        Returns:
            State machine details dictionary or None if not found
        """
        try:
            response = self.client.describe_state_machine(stateMachineArn=state_machine_arn)

            state_machine_info = {
                "name": response.get("name", ""),
                "arn": response.get("stateMachineArn", ""),
                "status": response.get("status", "ACTIVE"),
                "definition": response.get("definition", "{}"),
                "role_arn": response.get("roleArn", ""),
                "type": response.get("type", "STANDARD"),
                "creation_date": response.get("creationDate", ""),
                "logging_configuration": response.get("loggingConfiguration", {}),
                "tracing_configuration": response.get("tracingConfiguration", {}),
            }

            # Parse and format the definition
            try:
                definition_dict = json.loads(state_machine_info["definition"])
                state_machine_info["definition_formatted"] = json.dumps(
                    definition_dict, indent=2, sort_keys=True
                )
                state_machine_info["definition_dict"] = definition_dict
            except json.JSONDecodeError:
                state_machine_info["definition_formatted"] = state_machine_info["definition"]
                state_machine_info["definition_dict"] = {}

            return state_machine_info

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "StateMachineDoesNotExist":
                return None
            raise StepFunctionsServiceError(
                f"Failed to describe state machine '{state_machine_arn}' ({error_code}): {e}"
            )
        except Exception as e:
            raise StepFunctionsServiceError(
                f"Unexpected error describing state machine '{state_machine_arn}': {e}"
            )

    def list_executions(self, state_machine_arn: str, max_items: int = 10) -> List[Dict]:
        """
        List recent executions for a state machine.

        Args:
            state_machine_arn: ARN of the state machine
            max_items: Maximum number of executions to return

        Returns:
            List of execution dictionaries
        """
        try:
            response = self.client.list_executions(
                stateMachineArn=state_machine_arn, maxResults=max_items
            )

            executions = []
            for execution in response.get("executions", []):
                executions.append(
                    {
                        "arn": execution.get("executionArn", ""),
                        "name": execution.get("name", ""),
                        "status": execution.get("status", "UNKNOWN"),
                        "start_date": execution.get("startDate", ""),
                        "stop_date": execution.get("stopDate"),
                    }
                )

            return executions

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            raise StepFunctionsServiceError(
                f"Failed to list executions for '{state_machine_arn}' ({error_code}): {e}"
            )
        except Exception as e:
            raise StepFunctionsServiceError(
                f"Unexpected error listing executions for '{state_machine_arn}': {e}"
            )

    def format_date(self, date_value) -> str:
        """Format date for display."""
        if not date_value:
            return "N/A"

        if isinstance(date_value, datetime):
            return date_value.strftime("%Y-%m-%d %H:%M")
        elif isinstance(date_value, (int, float)):
            return datetime.fromtimestamp(date_value).strftime("%Y-%m-%d %H:%M")
        else:
            return str(date_value)[:19]

    def get_state_count(self, definition_dict: Dict) -> int:
        """Count the number of states in a state machine definition."""
        states = definition_dict.get("States", {})
        return len(states)

    def get_state_types(self, definition_dict: Dict) -> List[str]:
        """Get unique state types from a state machine definition."""
        states = definition_dict.get("States", {})
        state_types = set()

        for state in states.values():
            state_type = state.get("Type", "Unknown")
            state_types.add(state_type)

        return sorted(list(state_types))

    def extract_state_machine_name_from_arn(self, arn: str) -> str:
        """Extract state machine name from ARN."""
        if ":stateMachine:" in arn:
            return arn.split(":stateMachine:")[-1]
        return arn


# Global instance
stepfunctions_service = StepFunctionsService()
