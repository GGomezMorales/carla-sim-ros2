from dataclasses import dataclass
from enum import Enum


class ManagerState(str, Enum):
    """
    Lifecycle tracking states exposed by the scenario manager system machine.
    """

    IDLE = 'IDLE'
    RUNNING = 'RUNNING'
    ERROR = 'ERROR'


@dataclass
class OperationResult:
    """
    Normalized payload data structure representing the outcome of an internal feature task.

    Attributes:
        success (bool): Indicates if the operation completed as expected without errors.
        message (str): A human-readable diagnostic or informational message explaining the outcome.
        details (dict[str, object] | None): Optional structured metadata or telemetry properties 
            returned by the executed function. Defaults to None.
    """

    success: bool
    message: str
    details: dict[str, object] | None = None


class ManagerContext:
    """
    Maintains mutual lifecycle states and exposes factory methods for standardized responses.
    """

    def __init__(self):
        """
        Initialize a fresh management context, defaulting lifecycle tracking to an idle state.
        """
        self._state: str = ManagerState.IDLE
        self._active_scenario: str = ''

    def _success(self, message: str, details: dict[str, object] | None = None) -> OperationResult:
        """
        Build a standardized success result structure and clear any tracked runtime error context.

        Args:
            message (str): Descriptive text outlining the successful execution behavior.
            details (dict[str, object] | None, optional): Relevant output dictionaries or 
                metadata structures from the operation. Defaults to None.

        Returns:
            OperationResult: A success data container with success set to True.
        """
        return OperationResult(True, message, details or {})

    def _failure(self, message: str, details: dict[str, object] | None = None) -> OperationResult:
        """
        Transition the manager environment into an error state and format a failure tracking payload.

        Args:
            message (str): The error details or reason string explaining why the action failed.
            details (dict[str, object] | None, optional): Any supplementary system context 
                or tracking markers. Defaults to None.

        Returns:
            OperationResult: A failure data container with success set to False.
        """
        self._state: str = ManagerState.ERROR
        return OperationResult(False, message, details or {})
