from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Chart(db.Model):
    """Model for storing astrological chart data"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.Date, nullable=False)
    birth_time = db.Column(db.Time, nullable=True)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationship with planet positions
    planet_positions = db.relationship('PlanetPosition', backref='chart', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Chart {self.id} - {self.name or "Unnamed"}>'
    
class PlanetPosition(db.Model):
    """Model for storing planet positions in a chart"""
    id = db.Column(db.Integer, primary_key=True)
    chart_id = db.Column(db.Integer, db.ForeignKey('chart.id'), nullable=False)
    planet_name = db.Column(db.String(50), nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    sign = db.Column(db.String(20), nullable=False)
    retrograde = db.Column(db.Boolean, default=False)
    nakshatra_name = db.Column(db.String(50), nullable=True)
    nakshatra_ruling_planet = db.Column(db.String(50), nullable=True)
    
    def __repr__(self):
        return f'<PlanetPosition {self.planet_name} at {self.longitude}>'