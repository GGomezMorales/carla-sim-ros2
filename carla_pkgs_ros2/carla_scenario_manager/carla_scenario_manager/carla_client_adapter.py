class CarlaClientAdapter:
    """
    Adapter around the CARLA Python API.

    This class manages the connection to the CARLA server and provides
    high-level abstractions for common simulation tasks such as loading maps,
    spawning vehicles, modifying weather conditions, and managing actors.
    """

    def __init__(self, host: str, port: int, timeout: float):
        """
        Initialize adapter connection settings.
        """
        self._host: str = host
        self._port: int = int(port)
        self._timeout: float = float(timeout)
        self._client = None
        self._carla = None

    def _import_carla(self):
        """
        Import and cache the CARLA Python API module.

        Dynamically imports the CARLA module to ensure it is only loaded when needed,
        and caches it to prevent redundant imports on subsequent calls.

        Returns:
            module: The imported CARLA Python module.

        Raises:
            RuntimeError: If the CARLA API is not available or not correctly configured in the PYTHONPATH.
        """
        if self._carla is not None:
            return self._carla

        try:
            import carla
        except ImportError as exc:
            raise RuntimeError(
                '[FAILURE!] CARLA Python API is not available. Ensure the carla wheel is installed and PYTHONPATH is configured.'
            ) from exc

        self._carla = carla
        return carla

    def  _connect(self):
        """
        Create and cache a CARLA client connection.

        Establishes a connection to the CARLA server using the host, port, and timeout
        provided during initialization. Caches the client object to avoid redundant connections.

        Returns:
            carla.Client: The active CARLA client connection.
        """
        if self._client is not None:
            return self._client

        carla = self._import_carla()
        self._client = carla.Client(self._host, self._port)
        self._client.set_timeout(self._timeout)
        return self._client

    def _current_world_name(self, world: object) -> str:
        """
        Extract the short map name from a CARLA world object.

        CARLA maps often have a path prefix (e.g., 'Carla/Maps/Town01'). This
        helper method strips the prefix and returns just the final map name.

        Args:
            world (carla.World): The active CARLA world instance.

        Returns:
            str: The short name of the currently loaded map (e.g., 'Town01').
        """
        map_name = world.get_map().name
        return map_name.split('/')[-1] if '/' in map_name else map_name

    def ResetWorld(self) -> str:
        """
        Reset the world by reloading the currently active map.

        This is useful for clearing out dynamically spawned actors and resetting
        the simulation to a clean state on the same map.

        Returns:
            str: The short name of the reloaded map.
        """
        client = self. _connect()
        world = client.get_world()
        current_town = self._current_world_name(world)
        return self.ReloadWorld(current_town)

    def ReloadWorld(self, town: str) -> str:
        """
        Load the selected town and return its map name.

        Args:
            town (str): The name of the map/town to load (e.g., 'Town03').

        Returns:
            str: The short name of the newly loaded map.
        """
        if not town:
            raise ValueError(
                '[FAILURE!] town must not be empty.'
            )

        client = self. _connect()
        world = client.load_world(town)
        return self._current_world_name(world)

    def SetWeather(self, profile: str, overrides: dict[str, object]) -> str:
        """
        Set weather using a predefined profile and optional override fields.

        Args:
            profile (str): The name of a CARLA predefined weather profile (e.g., 'ClearNoon').
            overrides (dict[str, object]): A dictionary of specific weather parameters to override 
                (e.g., {'cloudiness': 80.0, 'precipitation': 100.0}). Only valid weather
                attributes will be applied.

        Returns:
            str: The name of the weather profile applied.
        """
        carla = self._import_carla()
        client = self. _connect()
        world = client.get_world()

        weather = getattr(carla.WeatherParameters, profile, None)
        if weather is None:
            weather = carla.WeatherParameters()

        for key, value in overrides.items():
            if value is None:
                continue
            if hasattr(weather, key):
                setattr(weather, key, float(value))

        world.set_weather(weather)
        return profile

    def _resolve_spawn_transform(self, world: object, spawn_cfg: dict[str, object]):
        """
        Build or select a spawn transform based on configuration.

        If `use_random_spawn` is True, it selects a pre-defined spawn point from the map.
        Otherwise, it constructs a custom transform using the provided x, y, z, roll, pitch, and yaw.

        Args:
            world (carla.World): The active CARLA world instance.
            spawn_cfg (dict[str, object]): A dictionary containing spawn instructions.
                Expected keys include 'use_random_spawn', 'spawn_point_index', 
                'x', 'y', 'z', 'roll', 'pitch', 'yaw'.

        Returns:
            carla.Transform: The calculated transform representing the location and rotation for spawning.
        """
        carla = self._import_carla()

        if spawn_cfg.get('use_random_spawn', True):
            spawn_points = world.get_map().get_spawn_points()
            if not spawn_points:
                raise RuntimeError(
                    '[FAILURE!] No spawn points available in current map.'
                )
            index = int(
                spawn_cfg.get('spawn_point_index', 0)
            ) % len(spawn_points)
            return spawn_points[index]

        return carla.Transform(
            carla.Location(
                x=float(spawn_cfg.get('x', 0.0)),
                y=float(spawn_cfg.get('y', 0.0)),
                z=float(spawn_cfg.get('z', 0.0))
            ),
            carla.Rotation(
                roll=float(spawn_cfg.get('roll', 0.0)),
                pitch=float(spawn_cfg.get('pitch', 0.0)),
                yaw=float(spawn_cfg.get('yaw', 0.0))
            )
        )

    def SpawnVehicle(self, spawn_config: dict[str, object]) -> int:
        """
        Spawn a single vehicle into the simulation and return its actor ID.

        Args:
            spawn_config (dict[str, object]): Configuration specifying the vehicle to spawn.
                Expected keys include:
                - 'blueprint_filter' (str): Filter for the blueprint library (e.g., 'vehicle.tesla.model3').
                - 'role_name' (str): The role name attribute for the vehicle (e.g., 'ego_vehicle').
                - 'autopilot' (bool): Whether to enable the built-in CARLA autopilot upon spawning.
                Also supports keys consumed by `ResolveSpawnTransform`.

        Returns:
            int: The unique integer ID of the spawned vehicle.
        """
        client = self._connect()
        world = client.get_world()
        blueprint_library = world.get_blueprint_library()

        filter_expr = str(spawn_config.get('blueprint_filter', 'vehicle.*'))
        matching = blueprint_library.filter(filter_expr)
        if not matching:
            raise RuntimeError(
                f'[FAILURE!] No blueprint matches filter: {filter_expr}.'
            )

        blueprint = matching[0]
        role_name = str(spawn_config.get('role_name', 'scenario_vehicle'))
        if blueprint.has_attribute('role_name'):
            blueprint.set_attribute('role_name', role_name)

        transform = self._resolve_spawn_transform(world, spawn_config)
        actor = world.try_spawn_actor(blueprint, transform)
        if actor is None:
            raise RuntimeError(
                '[FAILURE!] CARLA rejected the spawn request (collision or invalid transform).'
            )

        if bool(spawn_config.get('autopilot', False)) and hasattr(actor, 'set_autopilot'):
            actor.set_autopilot(True)

        return int(actor.id)

    def DestroyActor(self, actor_id: int) -> bool:
        """
        Destroy an active actor in the simulation by its ID.

        Args:
            actor_id (int): The unique integer ID of the actor to destroy.

        Returns:
            bool: True if the actor was successfully destroyed, False if the actor 
                was not found in the simulation.
        """
        client = self._connect()
        world = client.get_world()
        actor = world.get_actor(int(actor_id))
        if actor is None:
            return False

        result = actor.destroy()
        if isinstance(result, bool):
            return result
        return True

    def ListActors(self) -> list[str]:
        """
        Return a lightweight string representation of all active actors.

        Gathers all actors currently present in the simulation world and formats
        them into a concise summary string.

        Returns:
            list[str]: A list of strings, each describing an actor's ID, type ID, 
                and role name.
        """
        client = self._connect()
        world = client.get_world()
        actor_list = world.get_actors()

        rows: list[str] = []
        for actor in actor_list:
            role_name: str | None = None
            if actor.attributes and 'role_name' in actor.attributes:
                role_name = actor.attributes['role_name']

            rows.append(
                f'id={actor.id}, type={actor.type_id}, role={role_name or "-"}'
            )

        return rows
