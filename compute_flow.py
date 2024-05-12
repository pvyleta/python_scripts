def round_to_nearest_divisible_by_5(value):
    return int(((value + 2) // 5) * 5)

def get_co2_ppm(value):
    try:
        return int(float(value))
    except ValueError:
        # use 400 (atmosphere level) if unknown
        return 400

input_entities = data.get('input_entities')
output_entity = data.get('output_entity')
mqtt_topic = data.get('mqtt_topic')
lowest_boundary = data.get('lowest_boundary', None)
highest_boundary = data.get('highest_boundary', None)

# Retrieve values from input entities
input_states = [hass.states.get(entity) for entity in input_entities]

# Convert input states to integers
ppm_values = [get_co2_ppm(state.state) for state in input_states]

# Calculate max value
max_value = max(ppm_values)

# Round up to nearest integer divisible by 5
target_value = int(max_value*1.15/10)
rounded_value = round_to_nearest_divisible_by_5(target_value)

# Check if boundaries are specified and within range
if lowest_boundary is not None:
    rounded_value = max(rounded_value, lowest_boundary)
if highest_boundary is not None:
    rounded_value = min(rounded_value, highest_boundary)

# Read the current value from the MQTT topic
current_state = hass.states.get(output_entity).state
current_value = int(float(current_state)) if current_state != 'unknown' else None

# Publish new value to MQTT topic if the target differs more than 6 from the current value (hysteresis)
if current_value is None or abs(target_value - current_value) > 6:
    logger.info(f"co2: {ppm_values} current: {current_value} aim: {target_value} rounded: {rounded_value} action: SET")
    hass.services.call('mqtt', 'publish', {'topic': mqtt_topic, 'payload': rounded_value})
else:
    logger.info(f"co2: {ppm_values} current: {current_value} aim: {target_value} rounded: {rounded_value} action: PASS")

