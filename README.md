# Holiday Days Argentina

Home Assistant integration that retrieves national holidays and non-working days in Argentina from the official government website.

## Features

- Detects if today is a **national holiday** (fixed, movable, or bridge day)
- Detects if today is a **non-working day** (optional religious days)
- Optional support for **Jewish** and **Islamic** non-working days
- Automatic updates from [argentina.gob.ar](https://www.argentina.gob.ar/jefatura/feriados-nacionales-2026) (year is dynamic)

## Entities

### Binary Sensors

| Entity | Description |
|--------|-------------|
| `binary_sensor.is_holiday_today` | `on` if today is a national holiday |
| `binary_sensor.is_non_working_day_today` | `on` if today is a non-working day |

### Sensors

| Entity | Description |
|--------|-------------|
| `sensor.today_s_holiday` | Name of today's holiday/non-working day |

## Attributes

Sensors include additional attributes such as:

- `year`, `date`
- `is_holiday`, `is_non_working_day`
- `name`, `type`, `category`
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
3. Configure options:
   - **Include Jewish days**: Include non-working days for the Jewish community
   - **Include Islamic days**: Include non-working days for the Islamic community

Options can be modified later from the integration settings.

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
  {% else %}
    Today is not a holiday
  {% endif %}
```

## Data Source

Data is retrieved from the official Argentine government website:
https://www.argentina.gob.ar/jefatura/feriados-nacionales-{year}

The integration queries this page automatically and updates the data at the beginning of each month.

## License

MIT
