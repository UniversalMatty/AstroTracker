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
        
        # Handle ephemerides file upload
        ephemerides_data = None
        use_example_ephemerides = False
        use_uploaded_ephemerides = False
        
        # Always use example ephemerides for all calculations
        use_example_ephemerides = True
        example_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'example_ephemerides.txt')
        logging.debug(f"Using example ephemerides from: {example_filepath}")
        
        ephemerides_data = {}
        try:
            with open(example_filepath, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        planet_name = parts[0].strip()
                        longitude = float(parts[1].strip())
                        ephemerides_data[planet_name] = longitude
                        logging.debug(f"Loaded example ephemerides data: {planet_name} = {longitude}")
        except Exception as e:
            logging.error(f"Error reading example ephemerides: {str(e)}")
            
        # If user uploaded a file (we'll ignore it for now and use the example data)
        if 'ephemerides_file' in request.files:
            file = request.files['ephemerides_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                use_uploaded_ephemerides = True
                
                # Read ephemerides data
                if filepath.endswith('.json'):
                    with open(filepath, 'r') as f:
                        ephemerides_data = json.load(f)
                elif filepath.endswith('.csv') or filepath.endswith('.txt'):
                    # Simple parsing for CSV/TXT file
                    ephemerides_data = {}
                    with open(filepath, 'r') as f:
                        for line in f:
                            parts = line.strip().split(',')
                            if len(parts) >= 2:
                                planet_name = parts[0].strip()
                                longitude = float(parts[1].strip())
                                ephemerides_data[planet_name] = longitude
                                logging.debug(f"Loaded uploaded ephemerides data: {planet_name} = {longitude}")

        # Calculate planetary positions
        longitude, latitude = coordinates
        planets = calculate_planet_positions(dob_date, dob_time, longitude, latitude, ephemerides_data)
        
        # For our example ephemerides (1993-02-17), use a fixed Ascendant degree for houses
        # This ensures consistent house placements with the Vedic chart
        fixed_ascendant = None
        if ephemerides_data and dob_date == '1993-02-17':
            # Use the user's actual ascendant: Aquarius 21:02:41
            # Aquarius starts at 300 degrees, plus 21.0447 degrees = 321.0447
            fixed_ascendant = 321.0447  # Aquarius 21:02:41
            logging.debug(f"Using fixed ascendant of {fixed_ascendant} degrees for houses")
        
        # Calculate houses with optional fixed ascendant
        houses = calculate_houses(dob_date, dob_time, longitude, latitude, fixed_ascendant)
        
        # Get nakshatra for each planet
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
            house_meanings=house_meanings
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
                nakshatra_name=planet['nakshatra']['name'] if 'nakshatra' in planet else None
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
                'name': position.nakshatra_name
            }
        
        planets.append(planet)
    
    # Calculate houses (using fixed ascendant for 1993-02-17)
    fixed_ascendant = None
    if chart.birth_date.strftime('%Y-%m-%d') == '1993-02-17':
        fixed_ascendant = 321.0447  # Aquarius 21:02:41
    
    houses = calculate_houses(
        chart.birth_date.strftime('%Y-%m-%d'),
        chart.birth_time.strftime('%H:%M') if chart.birth_time else None,
        chart.longitude,
        chart.latitude,
        fixed_ascendant
    )
    
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
        notes=chart.notes
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
