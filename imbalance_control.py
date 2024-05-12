input_switch = data.get('switch_entity_id')
numeric_entity = data.get('numeric_entity_id')
on_value = float(data.get('on_value', 0))  # Default value if switch is on
off_value = float(data.get('off_value', 0))  # Default value if switch is off

# Fetch the current state of the switch
switch_state = hass.states.get(input_switch).state

# Determine the value to set based on the switch state
value_to_set = on_value if switch_state == 'on' else off_value

# Set the numeric entity's value
hass.services.call('number', 'set_value', {
    'entity_id': numeric_entity,
    'value': value_to_set
}, False)