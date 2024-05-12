# control_bypass.py

inside_temp_sensor = data.get('inside_temp_sensor')
outside_temp_sensor = data.get('outside_temp_sensor')
bypass_entity = data.get('bypass_entity')

inside_temp = float(hass.states.get(inside_temp_sensor).state)
outside_temp = float(hass.states.get(outside_temp_sensor).state)
diff_temp = inside_temp - outside_temp

if inside_temp > 23.5 and diff_temp > 4:
    # Assuming the 'open' value for the input_select is "Open"
    hass.services.call('select', 'select_option', {'entity_id': bypass_entity, 'option': 'Open'}, False)
    logger.info(f"Bypass: OPEN  inside: {inside_temp} outside: {outside_temp}")
elif inside_temp < 21.5 or diff_temp < 2:
    # Assuming the 'closed' value for the input_select is "Closed"
    hass.services.call('select', 'select_option', {'entity_id': bypass_entity, 'option': 'Closed'}, False)
    logger.info(f"Bypass: CLOSE inside: {inside_temp} outside: {outside_temp}")
else:
    logger.info(f"Bypass: NONE  inside: {inside_temp} outside: {outside_temp}")