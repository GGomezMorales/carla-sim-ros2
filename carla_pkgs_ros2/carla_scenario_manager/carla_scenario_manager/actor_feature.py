from .adapter_contract import ScenarioAdapterContract
from .core_context import ManagerContext, OperationResult


class ActorFeature:
    """
    Handles high-level business logic for actor operations within the CARLA environment.

    This class coordinates the spawning, destruction, and listing of simulation actors
    by orchestrating calls to the underlying CARLA adapter and tracking execution health
    via a shared manager context.
    """

    def __init__(self, adapter: ScenarioAdapterContract, context: ManagerContext):
        """
        Initialize the actor feature with its required system dependencies.

        Args:
            adapter (ScenarioAdapterContract): The concrete CARLA simulator adapter 
                used to execute low-level actions.
            context (ManagerContext): The shared state tracking and diagnostic utility 
                used to format standardized results.
        """
        self._adapter: ScenarioAdapterContract = adapter
        self._context: ManagerContext = context

    def SpawnVehicle(self, spawn_config: dict[str, object]) -> OperationResult:
        """
        Spawn a vehicle actor in the CARLA world using a specific placement configuration.

        Args:
            spawn_config (dict[str, object]): Parameters detailing the vehicle type, 
                blueprint attributes, and spatial transform coordinates.

        Returns:
            OperationResult: A success result wrapping the newly generated 'actor_id' 
                on success, or a failure result tracking the caught simulator exception.
        """
        try:
            actor_id: int = self._adapter.SpawnVehicle(spawn_config)
        except Exception as exc:
            return self._context._failure(
                f'[CARLA ROS2 - FAILURE!] Failed to spawn vehicle: {exc}'
            )

        return self._context._success(
            f'[CARLA ROS2 - SUCCESS!] Vehicle spawned with actor id {actor_id}.',
            {'actor_id': actor_id}
        )

    def DestroyActor(self, actor_id: int) -> OperationResult:
        """
        Destroy and remove a specific CARLA actor from the active world by its identifier.

        Args:
            actor_id (int): The unique identification number of the target actor. 
                Must be a positive integer greater than zero.

        Returns:
            OperationResult: A standardized result object. Returns a failure if the 
                ID is invalid, if an exception occurs, or if the actor did not exist. 
                Returns success upon verified removal from the simulator.
        """
        if actor_id <= 0:
            return self._context._failure(
                '[CARLA ROS2 - FAILURE!] target_actor_id must be greater than zero.'
            )

        try:
            destroyed: bool = self._adapter.DestroyActor(actor_id)
        except Exception as exc:
            return self._context._failure(
                f'[CARLA ROS2 - FAILURE!] Failed to destroy actor: {exc}'
            )

        if not destroyed:
            return self._context._failure(
                f'[CARLA ROS2 - FAILURE!] Actor id {actor_id} was not destroyed. It may not exist.',
                {'actor_id': actor_id}
            )

        return self._context._success(
            f'[CARLA ROS2 - SUCCESS!] Actor id {actor_id} destroyed.',
            {'actor_id': actor_id}
        )

    def ListActors(self) -> OperationResult:
        """
        Gather and compile a text summary overview of all active actors in the CARLA world.

        Queries the adapter for current simulation elements, constructs a concise telemetry 
        string, and safely caps the preview text representation to the first ten items.

        Returns:
            OperationResult: A success result including a human-readable summary string, 
                the total integer 'count', and the raw 'actors' list inside the details payload.
        """
        try:
            actors: list[str] = self._adapter.ListActors()
        except Exception as exc:
            return self._context._failure(
                f'[CARLA ROS2 - FAILURE!] Failed to list actors: {exc}'
            )

        count: int = len(actors)
        preview: str = ', '.join(actors[:10])
        summary: str = f'{count} actor(s) found.'
        if preview:
            summary: str = f'{summary} Preview: {preview}'

        return self._context._success(
            f'[CARLA ROS2 - SUCCESS!] {summary}',
            {'count': count, 'actors': actors}
        )
