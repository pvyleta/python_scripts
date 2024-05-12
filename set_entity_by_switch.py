"""
Home Assistant Python Script: Switch-Based Entity Control

Sets the state or value of an entity based on the state of a switch. 
This script is designed to handle different entity types such as numbers, selectors, covers, lights, media players, climate controls, and fans where only a single value adjustment is needed.

Inputs:
- switch_entity_id (str): The entity ID of the switch whose state ('on' or 'off') determines the values set on the output entity.
- output_entity_id (str): The entity ID of the output to be controlled. Must belong to one of the supported domains.
- on_value (varies): The value to set for the output entity when the switch is 'on'. The type and range depend on the output entity's domain.
- off_value (varies): The value to set for the output entity when the switch is 'off'. The type and range depend on the output entity's domain.

Service Map Details:
- 'number': Uses 'set_value' service to adjust a number entity.
- 'input_number': Uses 'set_value' service for input number adjustments.
- 'select': Uses 'select_option' for selecting an option.
- 'input_select': Uses 'select_option' for input selections.
- 'cover': Uses 'set_position' for positioning covers.
- 'light': Adjusts 'brightness' using the 'turn_on' service.
- 'media_player': Sets 'volume_set' for adjusting volume level.
- 'climate': Adjusts 'temperature' using the 'set_temperature' service.
- 'fan': Uses 'set_speed' to control fan speed.

Exceptions:
- Raises ValueError if essential parameters are missing or invalid.
- Logs errors if the specified output entity's domain is unsupported or if the entities do not exist in Home Assistant.
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
input_switch = data['switch_entity_id']
output_entity = data['output_entity_id']
on_value = data['on_value']
off_value = data['off_value']

# Check entity existence
output_state = hass.states.get(output_entity)
if output_state is None:
    logger.error(f"Output entity {output_entity} not found.")
    raise ValueError(f"Output entity {output_entity} does not exist.")

switch_state = hass.states.get(input_switch)
if switch_state is None:
    logger.error(f"Switch entity {input_switch} not found.")
    raise ValueError(f"Switch entity {input_switch} does not exist.")

# Determine the value to set based on the switch state
value_to_set = on_value if switch_state.state == 'on' else off_value
set_entity(output_entity, value_to_set)