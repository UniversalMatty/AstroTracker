import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import tempfile
import json

from utils.geocoding import get_coordinates
from utils.astronomy import calculate_planet_positions
from utils.astrology import calculate_houses, get_nakshatra, get_house_meanings

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

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

@app.route('/calculate', methods=['POST'])
def calculate():
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
        if 'ephemerides_file' in request.files:
            file = request.files['ephemerides_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
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
                                ephemerides_data[parts[0]] = float(parts[1])

        # Calculate planetary positions
        longitude, latitude = coordinates
        planets = calculate_planet_positions(dob_date, dob_time, longitude, latitude, ephemerides_data)
        
        # Calculate houses
        houses = calculate_houses(dob_date, dob_time, longitude, latitude)
        
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
