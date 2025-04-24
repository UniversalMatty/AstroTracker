from kerykeion import KrInstance

# Create a simple chart for testing
chart = KrInstance(name="Test", year=1990, month=1, day=1, hour=12, minute=0, city="Berlin", nation="DE")

# Print out the chart data
print("Chart created for:", chart.name)
print("First house cusp:", chart.first_house)
print("Sun position:", chart.sun)
print("Moon position:", chart.moon)

