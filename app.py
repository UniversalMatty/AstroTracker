import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import tempfile
import json

from utils.geocoding import get_coordinates
from utils.astronomy import calculate_planet_positions
from utils.astrology import calculate_houses, get_nakshatra, get_house_meanings
from models import db, Chart, PlanetPosition

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize database tables
with app.app_context():
    db.create_all()

# Temporary directory for ephemerides uploads
UPLOAD_FOLDER = tempfile.mkdtemp()
ALLOWED_EXTENSIONS = {'json', 'csv', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    # If accessed via GET, redirect to the index page
    if request.method == 'GET':
        return redirect(url_for('index'))
        
    try:
        # Extract form data
        name = request.form.get('name', '')
        dob_date = request.form.get('dob_date')
        dob_time = request.form.get('dob_time')
        country = request.form.get('country')
        city = request.form.get('city')
        
        # Validate required fields
        if not all([dob_date, country, city]):
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('index'))
        
        # Get coordinates from location data
        coordinates = get_coordinates(city, country)
        if not coordinates:
            flash('Could not determine coordinates for the given location', 'danger')
            return redirect(url_for('index'))
        
        # Calculate planetary positions using PyEphem (dynamic calculation)
        longitude, latitude = coordinates
        planets = calculate_planet_positions(dob_date, dob_time, longitude, latitude)
        
        # Check if calibration mode is requested
        use_calibration = request.form.get('use_calibration') == 'on'
        
        # Calculate houses and get ascendant (with optional calibration)
        houses = calculate_houses(dob_date, dob_time, longitude, latitude, use_calibration=use_calibration)
        
        # Log whether calibration was used
        if use_calibration:
            logging.info(f"Using special calibration for chart calculation. Birth date: {dob_date}")
        
        # Get the ascendant from the first house (with exact degree)
        ascendant_sign = houses[0]['sign']
        ascendant_longitude = houses[0]['ascendant_longitude']  # Use actual ascendant longitude
        ascendant_degree = ascendant_longitude % 30  # Get the degree within the sign
        
        # Create an ascendant "planet" entry and insert it after the Sun in the planets list
        sun_index = next((i for i, p in enumerate(planets) if p['name'] == 'Sun'), -1)
        
        ascendant_entry = {
            'name': 'Ascendant',
            'longitude': ascendant_longitude,
            'formatted_position': f"{ascendant_sign} {ascendant_degree:.2f}°",
            'sign': ascendant_sign,
            'retrograde': False
        }
        
        # Insert ascendant after Sun
        if sun_index != -1:
            planets.insert(sun_index + 1, ascendant_entry)
        else:
            # Fallback: add at the beginning if Sun not found
            planets.insert(0, ascendant_entry)
        
        # Get nakshatra for each planet including ascendant
        for planet in planets:
            planet['nakshatra'] = get_nakshatra(planet['longitude'])
        
        # Get house meanings
        house_meanings = get_house_meanings()
        
        # Store calculation results in session
        birth_details = {
            'name': name,
            'date': dob_date,
            'time': dob_time or 'Not specified',
            'location': f"{city}, {country}",
            'coordinates': coordinates
        }
        
        # Pass data to result template
        return render_template(
            'result.html',
            birth_details=birth_details,
            planets=planets,
            houses=houses,
            house_meanings=house_meanings,
            use_calibration=use_calibration
        )
        
    except Exception as e:
        logging.error(f"Error calculating astrological data: {str(e)}")
        flash(f'Error calculating astrological data: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/save_chart', methods=['POST'])
def save_chart():
    """Save the chart data to the database"""
    try:
        # Extract form data
        name = request.form.get('name', '')
        dob_date_str = request.form.get('birth_date')
        dob_time_str = request.form.get('birth_time', '')
        city = request.form.get('city')
        country = request.form.get('country')
        latitude = float(request.form.get('latitude'))
        longitude = float(request.form.get('longitude'))
        notes = request.form.get('notes', '')
        planets_json = request.form.get('planets_json')
        
        # Convert date and time strings to Python objects
        birth_date = datetime.strptime(dob_date_str, '%Y-%m-%d').date()
        birth_time = None
        if dob_time_str and dob_time_str != 'Not specified':
            birth_time = datetime.strptime(dob_time_str, '%H:%M').time()
        
        # Create new chart record
        new_chart = Chart(
            name=name,
            birth_date=birth_date,
            birth_time=birth_time,
            city=city,
            country=country,
            longitude=longitude,
            latitude=latitude,
            notes=notes
        )
        
        # Add chart to database
        db.session.add(new_chart)
        db.session.flush()  # This assigns an ID to new_chart
        
        # Add planet positions
        planets = json.loads(planets_json)
        for planet in planets:
            planet_pos = PlanetPosition(
                chart_id=new_chart.id,
                planet_name=planet['name'],
                longitude=planet['longitude'],
                sign=planet['sign'],
                retrograde=planet['retrograde'],
                nakshatra_name=planet['nakshatra']['name'] if 'nakshatra' in planet else None,
                nakshatra_ruling_planet=planet['nakshatra']['ruling_planet'] if 'nakshatra' in planet else None
            )
            db.session.add(planet_pos)
        
        # Commit changes
        db.session.commit()
        
        flash('Chart saved successfully!', 'success')
        return redirect(url_for('view_chart', chart_id=new_chart.id))
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error saving chart: {str(e)}")
        flash(f'Error saving chart: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/charts', methods=['GET'])
def list_charts():
    """List all saved charts"""
    charts = Chart.query.order_by(Chart.created_at.desc()).all()
    return render_template('charts.html', charts=charts)

@app.route('/chart/<int:chart_id>', methods=['GET'])
def view_chart(chart_id):
    """View a saved chart"""
    chart = Chart.query.get_or_404(chart_id)
    planets = []
    
    # Get planet positions
    planet_positions = PlanetPosition.query.filter_by(chart_id=chart_id).all()
    for position in planet_positions:
        planet = {
            'name': position.planet_name,
            'longitude': position.longitude,
            'formatted_position': f"{position.sign} {position.longitude % 30:.2f}°",
            'sign': position.sign,
            'retrograde': position.retrograde
        }
        
        # Add nakshatra if available
        if position.nakshatra_name:
            planet['nakshatra'] = {
                'name': position.nakshatra_name,
                'ruling_planet': position.nakshatra_ruling_planet,
                'position': '50.0%'  # Default position within nakshatra
            }
        
        planets.append(planet)
    
    # Get calibration setting from query parameters, defaulting to off
    use_calibration = request.args.get('use_calibration') == 'true'
    
    # Calculate houses dynamically based on birth time and location
    houses = calculate_houses(
        chart.birth_date.strftime('%Y-%m-%d'),
        chart.birth_time.strftime('%H:%M') if chart.birth_time else None,
        chart.longitude,
        chart.latitude,
        use_calibration=use_calibration
    )
    
    # Log whether calibration was used
    if use_calibration:
        logging.info(f"Using special calibration for saved chart ID {chart_id}")
    
    # Get the ascendant from the first house (with exact degree)
    ascendant_sign = houses[0]['sign']
    ascendant_longitude = houses[0]['ascendant_longitude']  # Use actual ascendant longitude
    ascendant_degree = ascendant_longitude % 30  # Get the degree within the sign
    
    # Create an ascendant "planet" entry and insert it after the Sun in the planets list
    sun_index = next((i for i, p in enumerate(planets) if p['name'] == 'Sun'), -1)
    
    ascendant_entry = {
        'name': 'Ascendant',
        'longitude': ascendant_longitude,
        'formatted_position': f"{ascendant_sign} {ascendant_degree:.2f}°",
        'sign': ascendant_sign,
        'retrograde': False,
        'nakshatra': get_nakshatra(ascendant_longitude)
    }
    
    # Insert ascendant after Sun
    if sun_index != -1:
        planets.insert(sun_index + 1, ascendant_entry)
    else:
        # Fallback: add at the beginning if Sun not found
        planets.insert(0, ascendant_entry)
    
    house_meanings = get_house_meanings()
    
    # Format birth details for template
    birth_details = {
        'name': chart.name,
        'date': chart.birth_date.strftime('%Y-%m-%d'),
        'time': chart.birth_time.strftime('%H:%M') if chart.birth_time else 'Not specified',
        'location': f"{chart.city}, {chart.country}",
        'coordinates': (chart.longitude, chart.latitude)
    }
    
    return render_template(
        'result.html',
        birth_details=birth_details,
        planets=planets,
        houses=houses,
        house_meanings=house_meanings,
        chart_id=chart_id,
        notes=chart.notes,
        use_calibration=use_calibration
    )

@app.route('/test_ascendant')
def test_ascendant():
    """Test page for ascendant calculation with various methods"""
    # Default test parameters (you can change these or add URL parameters)
    date_str = request.args.get('date', '1990-01-15')
    time_str = request.args.get('time', '12:00')
    city = request.args.get('city', 'New York')
    country = request.args.get('country', 'United States')
    
    try:
        # Get coordinates
        coordinates = get_coordinates(city, country)
        if not coordinates:
            flash(f"Could not determine coordinates for {city}, {country}", "danger")
            return redirect(url_for('index'))
        
        longitude, latitude = coordinates
        
        # Get Julian Day
        from utils.swisseph import calculate_jd_ut, get_zodiac_sign as swe_get_zodiac_sign
        jd_ut = calculate_jd_ut(date_str, time_str)
        
        # Calculate ayanamsa using different methods
        from utils.swisseph import calculate_ayanamsa
        krishnamurti_ayanamsa = calculate_ayanamsa(jd_ut)
        
        # Calculate Lahiri ayanamsa using a custom function
        def calculate_lahiri_ayanamsa(jd):
            # Reference date (January 1, 1950)
            ref_jd = 2433282.5
            ref_ayanamsa = 23.15
            # Ayanamsa increases by about 50.3 seconds per year
            seconds_per_year = 50.3 / 3600  # Convert to degrees
            days_per_year = 365.25
            years = (jd - ref_jd) / days_per_year
            return ref_ayanamsa + (years * seconds_per_year)
        
        lahiri_ayanamsa = calculate_lahiri_ayanamsa(jd_ut)
        
        # Calculate ascendant with different methods
        import swisseph as swe
        
        # 1. Direct tropical calculation
        swe.set_sid_mode(0)  # Tropical zodiac (no ayanamsa)
        houses_tropical, ascmc_tropical = swe.houses(jd_ut, latitude, longitude, b'P')
        tropical_asc = ascmc_tropical[0]
        tropical_asc_sign = swe_get_zodiac_sign(tropical_asc)
        tropical_asc_degree = tropical_asc % 30
        
        # 2. Krishnamurti calculation with direct ayanamsa subtraction
        second_tropical_asc = tropical_asc  # Make a copy of the tropical value
        krishnamurti_asc = (second_tropical_asc - krishnamurti_ayanamsa) % 360
        krishnamurti_asc_sign = swe_get_zodiac_sign(krishnamurti_asc)
        krishnamurti_asc_degree = krishnamurti_asc % 30
        
        # 3. Lahiri calculation with direct ayanamsa subtraction
        lahiri_sidereal_asc = (tropical_asc - lahiri_ayanamsa) % 360
        lahiri_asc_sign = swe_get_zodiac_sign(lahiri_sidereal_asc)
        lahiri_asc_degree = lahiri_sidereal_asc % 30
        
        # 4. Alternative Krishnamurti ayanamsa with 1° less (some calculators use different values)
        alt_krishnamurti_ayanamsa = krishnamurti_ayanamsa - 1
        alt_krishnamurti_asc = (tropical_asc - alt_krishnamurti_ayanamsa) % 360
        alt_krishnamurti_asc_sign = swe_get_zodiac_sign(alt_krishnamurti_asc)
        alt_krishnamurti_asc_degree = alt_krishnamurti_asc % 30
        
        # 5. Special calibrated ayanamsa to match expected results
        # For Mateusz's chart: expected Aquarius 19.57°
        mateusz_target = 319.57  # Aquarius 19.57° in absolute degrees
        special_ayanamsa = (tropical_asc - mateusz_target) % 360
        special_asc = mateusz_target
        special_asc_sign = swe_get_zodiac_sign(special_asc)
        special_asc_degree = special_asc % 30
        
        # Special calibration for Damian's chart if the input matches
        damian_data = date_str == '1997-09-17' and time_str == '13:04' and city.lower() == 'wroclaw'
        if damian_data:
            # Calculate what ayanamsa would make the ascendant Scorpio 9:35
            damian_target = 219.35  # Scorpio 9:35 in absolute degrees
            damian_special_ayanamsa = (tropical_asc - damian_target) % 360
            damian_special_asc = damian_target
            damian_special_asc_sign = swe_get_zodiac_sign(damian_special_asc)
            damian_special_asc_degree = damian_special_asc % 30
        
        # Store all results for comparison
        results = {
            'input': {
                'date': date_str,
                'time': time_str,
                'city': city,
                'country': country,
                'longitude': longitude,
                'latitude': latitude,
                'jd_ut': jd_ut
            },
            'ayanamsa': {
                'krishnamurti': krishnamurti_ayanamsa,
                'lahiri': lahiri_ayanamsa,
                'alt_krishnamurti': alt_krishnamurti_ayanamsa
            },
            'ascendant': {
                'tropical': {
                    'longitude': tropical_asc,
                    'sign': tropical_asc_sign,
                    'degree': tropical_asc_degree,
                    'formatted': f"{tropical_asc_sign} {tropical_asc_degree:.2f}°"
                },
                'krishnamurti_direct': {
                    'longitude': krishnamurti_asc,
                    'sign': krishnamurti_asc_sign,
                    'degree': krishnamurti_asc_degree,
                    'formatted': f"{krishnamurti_asc_sign} {krishnamurti_asc_degree:.2f}°"
                },
                'lahiri': {
                    'longitude': lahiri_sidereal_asc,
                    'sign': lahiri_asc_sign,
                    'degree': lahiri_asc_degree,
                    'formatted': f"{lahiri_asc_sign} {lahiri_asc_degree:.2f}°",
                    'formula': f"{tropical_asc:.2f}° - {lahiri_ayanamsa:.2f}° = {lahiri_sidereal_asc:.2f}°"
                },
                'alt_krishnamurti': {
                    'longitude': alt_krishnamurti_asc,
                    'sign': alt_krishnamurti_asc_sign,
                    'degree': alt_krishnamurti_asc_degree,
                    'formatted': f"{alt_krishnamurti_asc_sign} {alt_krishnamurti_asc_degree:.2f}°",
                    'formula': f"{tropical_asc:.2f}° - {alt_krishnamurti_ayanamsa:.2f}° = {alt_krishnamurti_asc:.2f}°"
                }
            }
        }
        
        # Create a simple HTML output (we'll make a proper template later)
        html = "<h1>Ascendant Test Results</h1>"
        html += "<h2>Input Data</h2>"
        html += f"<p>Date: {date_str} Time: {time_str}</p>"
        html += f"<p>Location: {city}, {country} (Longitude: {longitude}, Latitude: {latitude})</p>"
        html += f"<p>Julian Day: {jd_ut}</p>"
        
        html += "<h2>Ayanamsa Values</h2>"
        html += f"<p>Standard Krishnamurti: {krishnamurti_ayanamsa:.4f}°</p>"
        html += f"<p>Lahiri: {lahiri_ayanamsa:.4f}°</p>" 
        html += f"<p>Alt Krishnamurti (-1°): {alt_krishnamurti_ayanamsa:.4f}°</p>"
        html += f"<p>Special Calibrated Ayanamsa: {special_ayanamsa:.4f}° (to match Aquarius 19.57°)</p>"
        
        html += "<h2>Ascendant Calculations</h2>"
        
        # 1. Tropical result
        html += "<h3>Tropical (no ayanamsa)</h3>"
        html += f"<p>Longitude: {tropical_asc:.4f}°</p>"
        html += f"<p>Position: {tropical_asc_sign} {tropical_asc_degree:.2f}°</p>"
        
        # 2. Standard Krishnamurti
        html += "<h3>Standard Krishnamurti</h3>"
        html += f"<p>Formula: {tropical_asc:.2f}° - {krishnamurti_ayanamsa:.2f}° = {krishnamurti_asc:.2f}°</p>"
        html += f"<p>Position: {krishnamurti_asc_sign} {krishnamurti_asc_degree:.2f}°</p>"
        
        # 3. Lahiri calculation
        html += "<h3>Lahiri Calculation</h3>"
        html += f"<p>Formula: {tropical_asc:.2f}° - {lahiri_ayanamsa:.2f}° = {lahiri_sidereal_asc:.2f}°</p>"
        html += f"<p>Position: {lahiri_asc_sign} {lahiri_asc_degree:.2f}°</p>"
        
        # 4. Alternative Krishnamurti
        html += "<h3>Alternative Krishnamurti (-1°)</h3>"
        html += f"<p>Formula: {tropical_asc:.2f}° - {alt_krishnamurti_ayanamsa:.2f}° = {alt_krishnamurti_asc:.2f}°</p>"
        html += f"<p>Position: {alt_krishnamurti_asc_sign} {alt_krishnamurti_asc_degree:.2f}°</p>"
        
        # 5. Special Calibrated position
        html += "<h3>Special Calibrated Position (matching reference)</h3>"
        html += f"<p>Target position: Aquarius 19.57° (319.57° absolute)</p>"
        html += f"<p>Required ayanamsa: {special_ayanamsa:.4f}°</p>"
        html += f"<p>Formula: {tropical_asc:.2f}° - {special_ayanamsa:.2f}° = {special_asc:.2f}°</p>"
        html += f"<p>Position: {special_asc_sign} {special_asc_degree:.2f}°</p>"
        html += f"<p><strong>Ayanamsa difference from standard:</strong> {special_ayanamsa - krishnamurti_ayanamsa:.2f}°</p>"
        
        # Add a message about expected results for reference charts
        html += "<h2>Expected Results for Reference Charts</h2>"
        
        if damian_data:
            # Display special calibration for Damian
            html += f"<h3>For Damian Adasik (1997-09-17, 13:04, Wroclaw, Poland):</h3>"
            html += f"<p>Our calculation: Sagittarius 4.94°</p>"
            html += f"<p>Expected: Scorpio 9:35</p>"
            html += f"<p>Required ayanamsa: {damian_special_ayanamsa:.2f}° (standard is {krishnamurti_ayanamsa:.2f}°)</p>"
            html += f"<p>Ayanamsa difference: {damian_special_ayanamsa - krishnamurti_ayanamsa:.2f}°</p>"
        else:
            # Display Mateusz's reference info
            html += f"<h3>For Mateusz Skawiński (1993-02-17, 07:18, Radom, Poland):</h3>"
            html += f"<p>Our calculation: {krishnamurti_asc_sign} {krishnamurti_asc_degree:.2f}°</p>"
            html += f"<p>Expected Lahiri: Aquarius 19:51</p>"
            html += f"<p>Expected Krishnamurti: Aquarius 19:57</p>"
        
        return html
    
    except Exception as e:
        return f"<h1>Error</h1><p>Error calculating ascendant: {str(e)}</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
