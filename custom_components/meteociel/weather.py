from homeassistant.components.weather import (
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.const import (
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MeteocielWeather(coordinator)])


class MeteocielWeather(CoordinatorEntity, WeatherEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)

        city = coordinator.city_name
        model = coordinator.model

        self._attr_name = f"Meteociel {city} {model}"
        self._attr_unique_id = (
            f"meteociel_{city}_{model}_{coordinator.city_id}"
        )

        self._attr_supported_features = (
            WeatherEntityFeature.FORECAST_HOURLY
            | WeatherEntityFeature.FORECAST_DAILY
        )

    @property
    def condition(self):
        return self.coordinator.data.get("condition")

    @property
    def native_temperature(self):
        return self.coordinator.data.get("temperature")

    @property
    def native_temperature_unit(self):
        return UnitOfTemperature.CELSIUS

    @property
    def humidity(self):
        return self.coordinator.data.get("humidity")

    @property
    def native_pressure(self):
        return self.coordinator.data.get("pressure")

    @property
    def native_pressure_unit(self):
        return UnitOfPressure.HPA

    @property
    def native_wind_speed(self):
        return self.coordinator.data.get("wind_speed")

    @property
    def native_wind_speed_unit(self):
        return UnitOfSpeed.KILOMETERS_PER_HOUR

    @property
    def native_wind_gust_speed(self):
        return self.coordinator.data.get("wind_gust_speed")

    @property
    def wind_bearing(self):
        return self.coordinator.data.get("wind_bearing")

    @property
    def native_precipitation(self):
        return self.coordinator.data.get("precipitation")

    async def async_forecast_hourly(self):
        return self.coordinator.data.get("forecast_hourly", [])

    async def async_forecast_daily(self):
        return self.coordinator.data.get("forecast_daily", [])

    @property
    def extra_state_attributes(self):
        return {
            "condition_label": self.coordinator.data.get("condition_label"),
            "model": self.coordinator.data.get("model"),
            "url": self.coordinator.data.get("url"),
            "hourly": self.coordinator.data.get("hourly"),
        }