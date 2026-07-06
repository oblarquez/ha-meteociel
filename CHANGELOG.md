# Changelog

All notable changes to this project will be documented in this file.

---

**Note:** Version 0.3.3 is the first public release of the project. Previous versions represent the internal development history and were never publicly released.



### Added
- Added daily reference evapotranspiration (ETP) estimation (Hargreaves).
- Added hourly Vapor Pressure Deficit (VPD) calculation.
- Added support for Meteociel "Tendances" forecasts.
- Added custom integration logo.
- Added support for multiple Meteociel forecast models.
- Added support for multiple integration instances.

### Improved
- Forecast parser now ignores past hourly forecasts.
- Improved current forecast selection.
- Daily forecasts ignore incomplete days (useful for long-range trends).
- Improved weather condition mapping.
- Improved parser reliability.

---

## [0.3.2]

### Added
- Daily forecast support.
- Hourly forecast support compatible with Home Assistant WeatherEntity.
- Support for weather forecast cards.

### Improved
- Better HTML parser.
- Improved duplicate forecast detection.

---

## [0.3.1]

### Added
- Multi-model support:
  - GFS
  - AROME
  - AROME 1h
  - ARPEGE 1h
  - ICON-EU
  - ICON-D2
  - WRF
  - WRF 1h

### Improved
- Better configuration flow.
- Cleaner entity naming.

---

## [0.3.0]

### Added
- Initial HTML parser.
- Weather entity.
- Current conditions.
- Hourly weather data.
- Pressure, humidity, wind, precipitation support.

---

## [0.2.0]

### Added
- Initial Home Assistant integration.
- Config Flow.
- Coordinator.
- Automatic data updates.

---

## [0.1.0]

### Added
- Project initialization.
- Meteociel HTML retrieval.
- First working prototype.