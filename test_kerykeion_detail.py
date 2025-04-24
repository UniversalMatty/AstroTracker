from kerykeion import KrInstance

# Create a simple chart for testing
chart = KrInstance(name="Test", year=1990, month=1, day=1, hour=12, minute=0, city="Berlin", nation="DE")

# Print house structure details
print("First house details:")
first_house = chart.first_house
print(f"Type: {type(first_house)}")
print(f"Dir: {dir(first_house)}")
print(f"Repr: {repr(first_house)}")

# Define our own DMS conversion function
def degrees_to_dms(degrees):
    """Convert decimal degrees to degrees, minutes, seconds"""
    d = int(degrees)
    m_float = (degrees - d) * 60
    m = int(m_float)
    s = int((m_float - m) * 60)
    return d, m, s

# Access the fields as attributes
print("\nAccessing attributes:")
print(f"Name: {first_house.name}")
print(f"Sign: {first_house.sign}")
print(f"Position in sign: {first_house.position}")
print(f"Absolute position: {first_house.abs_pos}")

# Format the position in DMS
d, m, s = degrees_to_dms(first_house.position)
print(f"\nDMS Format: {d}°{m}'{s}\"")

# Access the sign name
print("\nSign name:")
try:
    print(f"Sign name attribute: {first_house.sign_name}")
except AttributeError:
    print("sign_name attribute does not exist")

# Print all planets and their positions
print("\nAll planets:")
for planet in chart.planets_list:
    pos_in_sign = planet.position
    d, m, s = degrees_to_dms(pos_in_sign)
    print(f"{planet.name}: {planet.sign} {d}°{m}'{s}\" (House: {planet.house})")

