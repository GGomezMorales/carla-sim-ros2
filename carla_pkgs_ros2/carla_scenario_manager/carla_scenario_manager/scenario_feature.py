from .core_context import ManagerContext, ManagerState, OperationResult


class ScenarioFeature:
    """
    Handles scenario lifecycle transitions.

    This class coordinates starting and stopping individual simulation runs,
    safeguarding state transitions to ensure multiple scenarios do not conflict.
    """

    def __init__(self, context: ManagerContext):
        """
        Initialize scenario feature dependencies.

        Args:
            context (ManagerContext): The shared tracking state and operational 
                result factory infrastructure.
        """
        self._context: ManagerContext = context

    def StartScenario(self, scenario_name: str) -> OperationResult:
        """
        Start a named scenario lifecycle and update the manager state.

        Args:
            scenario_name (str): The unique descriptive name of the scenario to launch.

        Returns:
            OperationResult: A success result tracking the active scenario name, 
                or a failure result if the name is invalid or another scenario is running.
        """
        if not scenario_name:
            return self._context._failure(
                '[CARLA ROS2 - FAILURE!] scenario.active_name must not be empty.'
            )

        if self._context._state == ManagerState.RUNNING:
            return self._context._failure(
                f'[CARLA ROS2 - FAILURE!] Scenario already running: {self._context.active_scenario}',
                {'active_scenario': self._context.active_scenario}
            )

        self._context._state = ManagerState.RUNNING
        self._context._active_scenario = scenario_name
        return self._context._success(
            f'[CARLA ROS2 - SUCCESS!] Scenario {scenario_name} started.',
            {'active_scenario': self._context._active_scenario}
        )

    def StopScenario(self) -> OperationResult:
        """
        Stop the currently active scenario lifecycle and return the context to idle.

        Returns:
            OperationResult: A success payload tracking the stopped scenario name,
                or a failure result if there was no active scenario running.
        """
        if self._context._state != ManagerState.RUNNING:
            return self._context._failure(
                '[CARLA ROS2 - FAILURE!] No running scenario to stop.'
            )

        stopped_name: str = self._context._active_scenario
        self._context._state = ManagerState.IDLE
        self._context._active_scenario = ''
        return self._context._success(
            f'[CARLA ROS2 - SUCCESS!] Scenario {stopped_name} stopped.',
            {'stopped_scenario': stopped_name}
        )
