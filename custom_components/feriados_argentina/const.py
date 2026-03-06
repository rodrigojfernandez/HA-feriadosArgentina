"""Constants for Feriados Argentina integration."""

DOMAIN = "feriados_argentina"
BASE_URL = "https://www.argentina.gob.ar/jefatura/feriados-nacionales-{year}"

# Config entry keys
CONF_INCLUDE_JEWISH = "include_jewish"
CONF_INCLUDE_ISLAMIC = "include_islamic"

# Holiday type classification
# (a) = Armenio/tolerancia, (b) = Judío, (c) = Islámico
ISLAMIC_MARKER = "(c)"
JEWISH_MARKER = "(b)"

# Types that count as official holidays (feriados)
FERIADO_TYPES = {
    "Feriado inamovible",
    "Feriado trasladable",
    "Feriado turístico",
}

# Types that are non-working days (días no laborables) for specific communities
DIA_NO_LABORABLE_TYPE = "Día no laborable"
