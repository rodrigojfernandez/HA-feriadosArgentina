"""Constants for Feriados Argentina integration."""

DOMAIN = "feriados_argentina"

# API endpoint for Argentina holidays
API_URL = "https://api.argentinadatos.com/v1/feriados/{year}"

# API types that are official holidays (feriados inamovibles/trasladables)
HOLIDAY_API_TYPES = {"inamovible", "trasladable"}

# API types that are non-working days (puentes turisticos)
NON_WORKING_DAY_API_TYPES = {"puente"}
