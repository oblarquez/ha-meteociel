import logging
from datetime import timedelta

import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEFAULT_MODEL, MODEL_URLS
from .parser import parse_forecast

_LOGGER = logging.getLogger(__name__)


class MeteocielCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, city_id, city_name, model=DEFAULT_MODEL):
        self.hass = hass
        self.city_id = city_id
        self.city_name = city_name
        self.model = model



        super().__init__(
            hass,
            _LOGGER,
            name="meteociel",
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self):
        url_template = MODEL_URLS.get(
            self.model,
            MODEL_URLS[DEFAULT_MODEL],
        )

        url = url_template.format(
            city_id=self.city_id,
            city_name=self.city_name,
        )

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 "
                "Chrome/138 Safari/537.36"
            )
        }

        try:
            _LOGGER.debug("Meteociel URL: %s", url)

            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=20) as response:
                    _LOGGER.debug("HTTP status: %s", response.status)

                    response.raise_for_status()

                    html = await response.text()

            _LOGGER.debug("HTML reçu : %d caractères", len(html))

            #
            # Décommenter uniquement en cas de debug.
            #
            # debug_file = self.hass.config.path(
            #     "www",
            #     "meteociel_debug.html",
            # )
            #
            # with open(debug_file, "w", encoding="utf-8") as f:
            #     f.write(html)

            data = parse_forecast(html)

            data["model"] = self.model
            data["url"] = url

            return data

        except Exception as err:
            _LOGGER.exception("Erreur Meteociel : %s", err)
            raise