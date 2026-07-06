import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN, DEFAULT_MODEL, MODEL_URLS



class MeteocielConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):

        if user_input is not None:
            return self.async_create_entry(
                title=f"Meteociel {user_input['city_name']} ({user_input['model']})",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required("city_id", default=31051): vol.Coerce(int),
            vol.Required("city_name", default="carpentras"): str,
            vol.Required("model", default=DEFAULT_MODEL): vol.In(list(MODEL_URLS.keys())),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )