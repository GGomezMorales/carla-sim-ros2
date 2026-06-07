from .adapter_contract import ScenarioAdapterContract
from .core_context import ManagerContext, ManagerState, OperationResult


class WorldFeature:
    """
    Handles core environmental simulation maps, including world reset and reload sequences.

    Ensures that whenever maps swap or refresh, lifecycle metrics cascade back down 
    to baseline parameters safely, invalidating outdated scenario state records.
    """

    def __init__(self, adapter: ScenarioAdapterContract, context: ManagerContext):
        """
        Initialize world feature dependencies.

        Args:
            adapter (ScenarioAdapterContract): The concrete CARLA simulator adapter 
                used to execute low-level actions.
            context (ManagerContext): The shared state tracking and diagnostic utility 
                used to format standardized results.
        """
        self._adapter: ScenarioAdapterContract = adapter
        self._context: ManagerContext = context

    def ResetWorld(self) -> OperationResult:
        """
        Reset the currently active map level, clearing instances and stepping back down to IDLE state.

        Returns:
            OperationResult: Standard success payload tracking the renewed map name identifier, 
                or failure detailing underlying simulator adapter communication issues.
        """
        try:
            world_name: str = self._adapter.ResetWorld()
        except Exception as exc:
            return self._context._failure(
                f'[CARLA ROS2 - FAILURE!] Failed to reset world: {exc}.'
            )

        self._context._state = ManagerState.IDLE
        self._context._active_scenario = ''
        return self._context._success(
            '[CARLA ROS2 - SUCCESS!] World reset completed.',
            {'world_name': world_name}
        )

    def ReloadWorld(self, town: str) -> OperationResult:
        """
        Load a specified map level or layout asset tracking file by its town name.

        Args:
            town (str): Formal map naming schema key target (e.g., 'Town04').

        Returns:
            OperationResult: Standard success payload logging new system configurations, 
                or validation failures tracing missing inputs/simulator rejections.
        """
        if not town:
            return self._context._failure(
                '[CARLA ROS2 - FAILURE!] target_town must not be empty.'
            )

        try:
            world_name: str = self._adapter.ReloadWorld(town)
        except Exception as exc:
            return self._context._failure(
                f'[CARLA ROS2 - FAILURE!] Failed to reload world: {exc}.'
            )

        self._context._state = ManagerState.IDLE
        self._context._active_scenario = ''
        return self._context._success(
            f'[CARLA ROS2 - SUCCESS!] World reloaded to {town}.',
            {'world_name': world_name, 'town': town}
        )
