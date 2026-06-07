from .actor_feature import ActorFeature
from .adapter_contract import ScenarioAdapterContract
from .core_context import ManagerContext, ManagerState, OperationResult
from .scenario_feature import ScenarioFeature
from .weather_feature import WeatherFeature
from .world_feature import WorldFeature


class ScenarioManagerCore:
    """
    Facade class that composes and exposes all underlying scenario manager features.

    Serves as the centralized, high-level API for configuring maps, weather, 
    managing actors, and controlling the execution state lifecycle of scenarios.
    """

    def __init__(self, adapter: ScenarioAdapterContract):
        """
        Initialize feature sub-modules and inject the shared manager context framework.

        Args:
            adapter (ScenarioAdapterContract): Concrete simulation backend adapter 
                conforming to the manager contract guidelines.
        """
        self._context: ManagerContext = ManagerContext()
        self._world_feature: WorldFeature = WorldFeature(adapter, self._context)
        self._weather_feature: WeatherFeature = WeatherFeature(adapter, self._context)
        self._actor_feature: ActorFeature = ActorFeature(adapter, self._context)
        self._scenario_feature: ScenarioFeature = ScenarioFeature(self._context)

    @property
    def state(self) -> ManagerState:
        """
        Return the current system runtime lifecycle state.

        Returns:
            ManagerState: The active enum tracking state value (IDLE, RUNNING, or ERROR).
        """
        return self._context._state

    @property
    def active_scenario(self) -> str:
        """
        Return the name string of the currently active scenario.

        Returns:
            str: Active scenario metadata text or empty if none is running.
        """
        return self._context._active_scenario

    def ResetWorld(self) -> OperationResult:
        """
        Reset the currently active world/map to its initial baseline configurations.

        Returns:
            OperationResult: High-level normalized outcome payload of the reset action.
        """
        return self._world_feature.ResetWorld()

    def ReloadWorld(self, town: str) -> OperationResult:
        """
        Load or reload a world map by its formal CARLA town asset identifier name.

        Args:
            town (str): Target map asset location name string.

        Returns:
            OperationResult: High-level normalized outcome payload of the map switch sequence.
        """
        return self._world_feature.ReloadWorld(town)

    def SetWeatherProfile(self, profile: str, overrides: dict[str, object]) -> OperationResult:
        """
        Apply a predefined weather profile alongside custom attribute override fields.

        Args:
            profile (str): target preset parameter selection name.
            overrides (dict[str, object]): Fine-tuned modification keys and floating-point parameters.

        Returns:
            OperationResult: Standardized metadata result status tracking weather success.
        """
        return self._weather_feature.SetWeatherProfile(profile, overrides)

    def SpawnVehicle(self, spawn_config: dict[str, object]) -> OperationResult:
        """
        Spawn a vehicle actor into the simulation using configuration instructions.

        Args:
            spawn_config (dict[str, object]): Telemetry specifications for vehicle creation.

        Returns:
            OperationResult: Success containing the actor ID inside details, or failure metadata.
        """
        return self._actor_feature.SpawnVehicle(spawn_config)

    def DestroyActor(self, actor_id: int) -> OperationResult:
        """
        Destroy an existing active CARLA actor by processing its ID sequence.

        Args:
            actor_id (int): Identification key mapping to the live simulation target.

        Returns:
            OperationResult: Status logging the physical termination feedback loop.
        """
        return self._actor_feature.DestroyActor(actor_id)

    def StartScenario(self, scenario_name: str) -> OperationResult:
        """
        Start a named scenario lifecycle loop inside the internal state machine.

        Args:
            scenario_name (str): Unique identifying key tracking the execution model.

        Returns:
            OperationResult: State transition confirmation result packet.
        """
        return self._scenario_feature.StartScenario(scenario_name)

    def StopScenario(self) -> OperationResult:
        """
        Stop the active scenario lifecycle loop and step back down to idle.

        Returns:
            OperationResult: Termination state status feedback packet.
        """
        return self._scenario_feature.StopScenario()

    def ListActors(self) -> OperationResult:
        """
        List and summarize active actors currently living in the CARLA world.

        Returns:
            OperationResult: Compiled preview records of simulation elements.
        """
        return self._actor_feature.ListActors()
