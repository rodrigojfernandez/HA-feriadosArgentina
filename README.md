# Holiday Days Argentina

Home Assistant integration that retrieves national holidays and non-working days in Argentina from the ArgentinaDatos API.

## Features

- Detects if today is a **national holiday** (fixed or movable holidays)
- Detects if today is a **non-working day** (bridge days / tourist days)
- Automatic updates from [ArgentinaDatos API](https://api.argentinadatos.com)

## Entities

### Binary Sensors

| Entity | Description |
|--------|-------------|
| `binary_sensor.is_holiday_today` | `on` if today is a national holiday (fixed/movable) |
| `binary_sensor.is_non_working_day_today` | `on` if today is a non-working bridge day |

### Sensors

| Entity | Description |
|--------|-------------|
| `sensor.today_s_holiday` | Name of today's holiday/non-working day |

## Attributes

Sensors include additional attributes such as:

- `year`, `date`
- `is_holiday`, `is_non_working_day`
- `name`, `type`
- Detailed list of `holidays` and `non_working_days`

## Installation

### HACS (recommended)

1. Add this repository as a custom repository in HACS
2. Search for "Holiday Days Argentina" and install
3. Restart Home Assistant

### Manual

1. Copy the `feriados_argentina` folder to `config/custom_components/`
2. Restart Home Assistant

## Configuration

1. Go to **Settings > Devices & Services > Add Integration**
2. Search for "Holiday Days Argentina"
3. Click "Submit" (no configuration options required)

## Usage Examples

### Automation: Don't trigger alarm on holidays

```yaml
automation:
  - alias: "Morning alarm"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.is_holiday_today
        state: "off"
      - condition: state
        entity_id: binary_sensor.is_non_working_day_today
        state: "off"
    action:
      - service: media_player.play_media
        # ...
```

### Template: Show holiday in dashboard

```yaml
type: markdown
content: >
  {% if is_state('binary_sensor.is_holiday_today', 'on') %}
    Today is a holiday: {{ states('sensor.today_s_holiday') }}
  {% elif is_state('binary_sensor.is_non_working_day_today', 'on') %}
    Today is a bridge day: {{ states('sensor.today_s_holiday') }}
  {% else %}
    Today is a regular day
  {% endif %}
```

## Data Source

Data is retrieved from the ArgentinaDatos API:
https://api.argentinadatos.com/v1/feriados/{year}

The integration fetches data once per year and updates every 12 hours to check for changes.

## Holiday Types

| API Type | Sensor | Description |
|----------|--------|-------------|
| `inamovible` | Is Holiday Today | Fixed holiday (cannot be moved) |
| `trasladable` | Is Holiday Today | Movable holiday (can be shifted to Monday) |
| `puente` | Is Non-Working Day Today | Bridge day (tourist non-working day) |

## Changelog

### 2.0.0
- Changed data source from web scraping to ArgentinaDatos API
- Removed religious non-working days options (not available in API)
- Simplified configuration (no options required)
- Improved reliability and performance

### 1.0.1
- Initial release with web scraping from argentina.gob.ar

## License

MIT
