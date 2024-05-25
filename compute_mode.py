"""
Home Assistant Python Script: Control Fan Based on CO2 Levels

This script adjusts the fan mode based on CO2 levels read from specified sensors.
It compares CO2 readings against predefined mode thresholds and selects the appropriate fan mode.
It selects the mode that corresponds to the smallest CO2 threshold.
The modes is a dictionary in the form of "[mode_name]: [upper_co2_threshold]"

Inputs:
- input_entities (list[str]): Entity IDs for CO2 sensors.
- output_entity (str): Entity ID to publish the selected mode.
- modes (dict): Dictionary mapping fan modes to their CO2 ppm upper thresholds.

Example usage:
- alias: "Adjust Fan Mode Based on CO2 Levels"
  trigger:
    - platform: time_pattern
      minutes: "/10"
  action:
    - service: python_script.compute_mode
      data:
        input_entities:
          - sensor.co2_living_room
          - sensor.co2_office
        output_entity: 'select.fan_mode'
        modes:
          Holiday: 500
          Reduced: 620
          Normal: 750
          High: 5000
  mode: single
"""

def get_co2_ppm(value):
    try:
        return int(float(value))
    except ValueError:
        # use 400 (atmosphere level) if unknown
        return 400

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
modes = data.get('modes', {})
input_entities = data.get('input_entities')
output_entity = data.get('output_entity')

# Check all parameters
if not all([modes, input_entities, output_entity, output_entity]):
    raise ValueError("All parameters must be provided.")

# Retrieve and process CO2 sensor values
input_states = [hass.states.get(entity) for entity in input_entities]
ppm_values = [get_co2_ppm(state.state) for state in input_states if state]

# Determine the highest CO2 concentration
max_ppm_value = max(ppm_values) if ppm_values else 0

# Find the appropriate mode based on CO2 levels
target_mode = ""
target_ppm = 1000000  # Maximum for a ppm value representing 100%

# Iterate over all modes and their ppm boundaries, and find the smallest one
for mode, ppm in modes.items():
    if max_ppm_value < ppm and ppm < target_ppm:
        target_mode = mode
        target_ppm = ppm

# Retrieve the previous modes from the input_text entity
previous_modes_str = hass.states.get('input_text.previous_modes').state
previous_modes = previous_modes_str.split(',') if previous_modes_str else []

# Append the current target mode to the previous modes list
previous_modes.append(target_mode)

# Ensure the list does not exceed three entries
if len(previous_modes) > 3:
    previous_modes.pop(0)

# Update the input_text entity with the new previous modes
hass.services.call('input_text', 'set_value', {
    'entity_id': 'input_text.previous_modes',
    'value': ','.join(previous_modes)
}, False)

# Check if the last three modes are the same
if len(previous_modes) == 3 and all(mode == previous_modes[0] for mode in previous_modes):
    # Log the results and set the mode
    logger.info(f"CO2 levels: {ppm_values} Max PPM: {max_ppm_value} Selected Mode: {target_mode}")
    set_entity(output_entity, target_mode)
else:
    logger.info(f"CO2 levels: {ppm_values} Max PPM: {max_ppm_value} Mode not changed due to insufficient consecutive agreement.")
