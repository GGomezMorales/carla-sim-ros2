from .adapter_contract import ScenarioAdapterContract
from .core_context import ManagerContext, OperationResult


class WeatherFeature:
    """
    Handles weather-profile configuration actions.

    Interacts with the simulator client via an adapter interface to alter air, 
    precipitation, and ambient lighting components inside the running scene.
    """

    def __init__(self, adapter: ScenarioAdapterContract, context: ManagerContext):
        """
        Initialize weather feature dependencies.

        Args:
            adapter (ScenarioAdapterContract): Contract-compliant abstraction layer.
            context (ManagerContext): State tracking framework for diagnostic logging.
        """
        self._adapter: ScenarioAdapterContract = adapter
        self._context: ManagerContext = context

    def SetWeatherProfile(self, profile: str, overrides: dict[str, object]) -> OperationResult:
        """
        Apply a named weather layout alongside custom parameter override definitions.

        Args:
            profile (str): Baseline asset setup profile name (e.g., 'CloudyNoon').
            overrides (dict[str, object]): Tailored configuration adjustments map.

        Returns:
            OperationResult: Success indicating the confirmed active settings string, 
                or failure tracing the client configuration fault.
        """
        if not profile:
            return self._context._failure('weather.profile must not be empty.')

        try:
            applied_profile: str = self._adapter.SetWeather(profile, overrides)
        except Exception as exc:
            return self._context._failure(f'Failed to set weather profile: {exc}')

        return self._context._success(
            f'Weather profile set to {applied_profile}.',
            {'profile': applied_profile}
        )
