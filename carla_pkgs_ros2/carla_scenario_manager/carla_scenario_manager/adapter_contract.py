from abc import ABC, abstractmethod


class ScenarioAdapterContract(ABC):
    """
    Abstract Base Class defining the required interface contract for CARLA simulator interaction.

    Any concrete adapter implementation must override these methods to translate scenario 
    manager commands into raw commands compatible with the CARLA client simulation API.
    """

    @abstractmethod
    def ResetWorld(self) -> str:
        """
        Reset the current simulation world back to its clean, baseline starting parameters.

        Returns:
            str: The name of the world/map after the reset sequence completes.
        """

    @abstractmethod
    def ReloadWorld(self, town: str) -> str:
        """
        Completely load or reload a specific simulation world map by its formal town name.

        Args:
            town (str): The name of the map or asset level to be loaded (e.g., 'Town01').

        Returns:
            str: The verified name of the newly loaded world map.
        """

    @abstractmethod
    def SetWeather(self, profile: str, overrides: dict[str, object]) -> str:
        """
        Modify environmental, atmospheric, and weather parameters of the active world.

        Args:
            profile (str): The name of a preset weather configuration (e.g., 'ClearNoon').
            overrides (dict[str, object]): Explicit key-value parameter adjustments 
                used to fine-tune specific attributes like wetness, wind, or sun positions.

        Returns:
            str: A descriptive name or status log of the newly applied weather state.
        """

    @abstractmethod
    def SpawnVehicle(self, spawn_config: dict[str, object]) -> int:
        """
        Interface directly with CARLA's backend infrastructure to instantiate a vehicle.

        Args:
            spawn_config (dict[str, object]): Explicit positioning transforms and asset 
                blueprint definitions used to build the simulation object.

        Returns:
            int: The unique runtime ID assigned to the newly created vehicle actor by CARLA.
        """

    @abstractmethod
    def DestroyActor(self, actor_id: int) -> bool:
        """
        Command CARLA to safely remove and clean up an actor object using its ID.

        Args:
            actor_id (int): The unique identification reference tracker of the target actor.

        Returns:
            bool: True if the actor was found and successfully deleted; False otherwise.
        """

    @abstractmethod
    def ListActors(self) -> list[str]:
        """
        Poll the active simulator map and extract details about all live actors.

        Returns:
            list[str]: A collection of human-readable text strings describing the 
                currently active entities inside the world.
        """
