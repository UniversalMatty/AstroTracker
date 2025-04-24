from kerykeion import KrInstance
from kerykeion.utilities.math import degrees_to_dms

# Create a simple chart for testing
chart = KrInstance(name="Test", year=1990, month=1, day=1, hour=12, minute=0, city="Berlin", nation="DE")

# Print house structure details
print("First house details:")
first_house = chart.first_house
for key, value in first_house.items():
    print(f"  {key}: {value}")

# Print out the DMS formatted position
pos_in_sign = first_house['position']
d, m, s = degrees_to_dms(pos_in_sign)
print(f"\nDMS Format: {d}°{m}'{s}\"")

# Print sign name
print(f"Sign: {first_house['sign']}")
print(f"Sign full name: {chart.planets_list[0].sign_name}")  # Using Sun to get sign name format

