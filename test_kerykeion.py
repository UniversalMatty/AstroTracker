from kerykeion import KrInstance

# Create a simple chart for testing
chart = KrInstance(
    name="Test",
    year=1990,
    month=1,
    day=1,
    hour=12,
    minute=0,
    lat=52.52,
    lng=13.405,
    tz_str="Europe/Berlin",
    city="Berlin",
    nation="DE",
    online=False,
)

# Print out the chart data
print("Chart created for:", chart.name)
print("First house cusp:", chart.first_house)
print("Sun position:", chart.sun)
print("Moon position:", chart.moon)

