DOMAIN = "meteociel"

DEFAULT_MODEL = "gfs"

MODEL_URLS = {
    "gfs": "https://www.meteociel.fr/previsions/{city_id}/{city_name}.htm",
    "arome": "https://www.meteociel.fr/previsions-arome/{city_id}/{city_name}.htm",
    "arome_1h": "https://www.meteociel.fr/previsions-arome-1h/{city_id}/{city_name}.htm",
    "wrf": "https://www.meteociel.fr/previsions-wrf/{city_id}/{city_name}.htm",
    "wrf_1h": "https://www.meteociel.fr/previsions-wrf-1h/{city_id}/{city_name}.htm",
    "icon_eu": "https://www.meteociel.fr/previsions-iconeu/{city_id}/{city_name}.htm",
    "icon_d2": "https://www.meteociel.fr/previsions-icond2/{city_id}/{city_name}.htm",
    "arpege_1h": "https://www.meteociel.fr/previsions-arpege-1h/{city_id}/{city_name}.htm",
    "tendances": "https://www.meteociel.fr/tendances/{city_id}/{city_name}.htm",
}

