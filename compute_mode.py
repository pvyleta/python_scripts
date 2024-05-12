def round_to_nearest_divisible_by_5(value):
    return int(((value + 2) // 5) * 5)

def get_co2_ppm(value):
    try:
        return int(float(value))
    except ValueError:
        # use 400 (atmosphere level) if unknown
        return 400

modes = data.get('modes', {})
input_entities = data.get('input_entities')
fan_mode_topic = data.get('fan_mode_topic')

# Retrieve values from input entities
input_states = [hass.states.get(entity) for entity in input_entities]

# Convert input states to integers
ppm_values = [get_co2_ppm(state.state) for state in input_states]

# Calculate max value
max_ppm_value = max(ppm_values)

target_mode = ""
target_ppm = 1000000 # Maximum for a ppm value representing 100%

# Iterate over all modes and their ppm boundaries, and find the smallest one
for mode, ppm in modes.items():
    if max_ppm_value < ppm and ppm < target_ppm:
        target_mode = mode
        target_ppm = ppm

logger.info(f"co2: {ppm_values} max_ppm: {max_ppm_value} mode: {target_mode}")
hass.services.call('mqtt', 'publish', {'topic': fan_mode_topic, 'payload': target_mode})
