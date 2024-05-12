"""
Home Assistant Python Script: Temperature-Based Bypass Control

Opens and closes bypass valve based on the inside temperature and a temperature differential to the outside.
Opens when inside temperature is above open_temperature, closes when inside temperature is below close_temperature.
The temperature differential to the outside must be at least open_diff_threshold to open the valve.
If temperature differential to the outside drops below close_diff_threshold, the valve is closed disregarding the close temperature.
This allows to set certain hysteresis on both the inside temperature, as well as on the temperature differential.

Inputs:
- inside_temp_sensor (str): ID of the inside temperature sensor.
- outside_temp_sensor (str): ID of the outside temperature sensor.
- output_entity (str): ID of the output entity, e.g., a number, select, etc.
- open_temperature, close_temperature (float): Temperature thresholds for opening and closing the output entity.
- open_diff_threshold, close_diff_threshold (float): Differential temperature thresholds for opening and closing.
- open_value, close_value (str): Values to set for the output entity under specified conditions.

Example usage:
- alias: Control Bypass Valve Based on Temperature
  description: Adjusts the bypass valve based on the temperature inside compared to outside.
  trigger:
    - platform: time_pattern
      minutes: "/10"
  action:
  action:
    - service: python_script.bypass_control
      data:
        inside_temp_sensor: sensor.inside_temperature
        outside_temp_sensor: sensor.outside_temperature
        output_entity: select.bypass_valve
        open_temperature: 23.5
        close_temperature: 21.5
        open_diff_threshold: 4
        close_diff_threshold: 2
        open_value: "Open"
        close_value: "Closed"
  mode: single
"""

def get_service(entity_id):
    
    # Define a mapping of entity domains to their corresponding service and service attribute
    service_map = {
        'number': ('number', 'set_value', 'value'),
        'input_number': ('input_number', 'set_value', 'value'),
        'select': ('select', 'select_option', 'option'),
        'input_select': ('input_select', 'select_option', 'option'),
        'cover': ('cover', 'set_position', 'position'),
        'light': ('light', 'turn_on', 'brightness'),
        'media_player': ('media_player', 'volume_set', 'volume_level'),
        'climate': ('climate', 'set_temperature', 'temperature'),
        'fan': ('fan', 'set_speed', 'speed')
    }
    
    # Ensure the entity domain is supported
    domain = output_entity.split('.')[0]
    if domain not in service_map:
        logger.error(f"Unsupported domain {domain} for entity {entity_id}.")
        raise ValueError(f"Unsupported domain {domain} for entity {entity_id}.")

    service, service_action, parameter_name = service_map[domain]
    return service, service_action, parameter_name 


def set_entity(entity_id, value):
    service, service_action, parameter_name = get_service(entity_id)
    hass.services.call(service, service_action, {
        'entity_id': entity_id,
        parameter_name: value
    }, False)


# Retrieve and validate input parameters
inside_temp_sensor = data.get('inside_temp_sensor')
outside_temp_sensor = data.get('outside_temp_sensor')
output_entity = data.get('output_entity')
open_temperature = data.get('open_temperature')
close_temperature = data.get('close_temperature')
open_diff_threshold = data.get('open_diff_threshold')
close_diff_threshold = data.get('close_diff_threshold')
open_value = data.get('open_value')
close_value = data.get('close_value')

# Check all parameters
if not all([inside_temp_sensor, outside_temp_sensor, output_entity, open_value, close_value]):
    logger.error("Missing one or more required parameters.")
    raise ValueError("All parameters must be provided.")

# Entity existence check
if any(hass.states.get(entity) is None for entity in [inside_temp_sensor, outside_temp_sensor, output_entity]):
    logger.error("One or more specified entities do not exist.")
    raise ValueError("Specified entities must exist in Home Assistant.")

# Read and convert temperatures
try:
    inside_temp = float(hass.states.get(inside_temp_sensor).state)
    outside_temp = float(hass.states.get(outside_temp_sensor).state)
except ValueError:
    logger.error("Invalid temperature data.")
    raise ValueError("Temperature sensor states must be convertible to float.")

# Calculate temperature difference
diff_temp = inside_temp - outside_temp

# Determine the value to set based on temperature thresholds
value_to_set = None
if inside_temp > float(open_temperature) and diff_temp > float(open_diff_threshold):
    set_entity(output_entity, open_value)
    logger.info(f"Bypass Control: {open_value} inside: {inside_temp} outside: {outside_temp}")
elif inside_temp < float(close_temperature) or diff_temp < float(close_diff_threshold):
    set_entity(output_entity, close_value)
    logger.info(f"Bypass Control: {close_value} inside: {inside_temp} outside: {outside_temp}")
