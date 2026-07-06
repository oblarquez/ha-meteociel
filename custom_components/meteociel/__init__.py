from .const import DOMAIN
from .coordinator import MeteocielCoordinator


async def async_setup_entry(hass, entry):
    city_id = entry.data["city_id"]
    city_name = entry.data["city_name"]
    model = entry.data.get("model", "gfs")

    coordinator = MeteocielCoordinator(hass, city_id, city_name, model)
    
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["weather"])

    return True

async def async_unload_entry(hass, entry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["weather"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok