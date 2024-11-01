inside_temp = float(hass.states.get('sensor.ebusd_sky300_insidetemperature').state)
outside_temp = float(hass.states.get('sensor.ebusd_sky300_outsidetemperature').state)
air_flow_m3h = float(hass.states.get('sensor.ebusd_sky300_exhaustflowsetting').state)
bypass_status = hass.states.get('sensor.ebusd_sky300_bypassstatus').state

# Constants
air_density = 1.2  # kg/m³
specific_heat_capacity = 1005  # J/kg·K

# Convert air flow from m³/h to m³/s
air_flow_m3s = air_flow_m3h / 3600

# Calculate temperature difference
temp_difference = inside_temp - outside_temp

# Calculate cooling power only if bypass is open
if bypass_status.lower() == 'open':
    cooling_power = air_flow_m3s * air_density * specific_heat_capacity * temp_difference  # in watts
else:
    cooling_power = 0

# Set the state for the new sensor
hass.states.set('sensor.cooling_power', cooling_power, {
    'unit_of_measurement': 'W',
    'friendly_name': 'Cooling Power'
})
