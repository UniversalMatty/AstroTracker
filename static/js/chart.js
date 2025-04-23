// Chart.js script for visualizing astrological data

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts when DOM is loaded
    renderCharts();
});

function renderCharts() {
    // Check if we're on the results page by looking for the chart canvas
    const planetChartCanvas = document.getElementById('planet-chart');
    if (!planetChartCanvas) return;
    
    // Get planet data from the data attribute
    const planetsDataElement = document.getElementById('planets-data');
    if (!planetsDataElement) return;
    
    try {
        // Get data from the attribute and handle possible errors
        const planetsDataStr = planetsDataElement.getAttribute('data-planets');
        console.log("Raw planets data:", planetsDataStr);
        
        // Parse the JSON data
        const planetsData = JSON.parse(planetsDataStr);
        console.log("Parsed planets data:", planetsData);
        
        // Make sure it's an array before proceeding
        if (Array.isArray(planetsData)) {
            createZodiacChart(planetChartCanvas, planetsData);
        } else {
            console.error("Expected planets data to be an array but got:", typeof planetsData);
        }
    } catch (error) {
        console.error('Error parsing planet data:', error);
    }
}

function createZodiacChart(canvas, planets) {
    // Chart configuration
    const zodiacSigns = [
        "Aries", "Taurus", "Gemini", "Cancer", 
        "Leo", "Virgo", "Libra", "Scorpio", 
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ];
    
    const signColors = [
        '#FF5733', '#8B4513', '#FFFF00', '#87CEEB',
        '#FFA500', '#90EE90', '#FF69B4', '#800000',
        '#0000FF', '#A52A2A', '#00FFFF', '#9370DB'
    ];
    
    // Create a circular chart
    const ctx = canvas.getContext('2d');
    
    // Clear any existing chart
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 10;
    
    // Draw the zodiac wheel
    drawZodiacWheel(ctx, centerX, centerY, radius, zodiacSigns, signColors);
    
    // Plot planets on the wheel
    plotPlanets(ctx, centerX, centerY, radius, planets);
}

function drawZodiacWheel(ctx, centerX, centerY, radius, zodiacSigns, signColors) {
    // Draw the zodiac wheel with 12 segments (signs)
    for (let i = 0; i < 12; i++) {
        const startAngle = 2 * Math.PI * i / 12;
        const endAngle = 2 * Math.PI * (i + 1) / 12;
        
        // Draw segment
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, startAngle, endAngle);
        ctx.closePath();
        
        // Fill with sign color (with transparency)
        ctx.fillStyle = signColors[i] + '40'; // 40 = 25% opacity
        ctx.fill();
        
        // Draw outline
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.stroke();
        
        // Add zodiac sign label
        const labelRadius = radius * 0.85;
        const labelX = centerX + labelRadius * Math.cos(startAngle + (endAngle - startAngle) / 2);
        const labelY = centerY + labelRadius * Math.sin(startAngle + (endAngle - startAngle) / 2);
        
        ctx.font = 'bold 12px Arial';
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(zodiacSigns[i], labelX, labelY);
    }
    
    // Draw center circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, 5, 0, 2 * Math.PI);
    ctx.fillStyle = '#ffffff';
    ctx.fill();
}

function plotPlanets(ctx, centerX, centerY, radius, planets) {
    // Planet symbols (using abbreviations as symbols would need special font)
    const planetSymbols = {
        'Sun': '☉',
        'Moon': '☽',
        'Mercury': '☿',
        'Venus': '♀',
        'Mars': '♂',
        'Jupiter': '♃',
        'Saturn': '♄',
        'Uranus': '♅',
        'Neptune': '♆',
        'Pluto': '♇'
    };
    
    // Organize planets by sign to avoid overlap
    const planetsByLongitude = [...planets].sort((a, b) => a.longitude - b.longitude);
    
    for (let i = 0; i < planetsByLongitude.length; i++) {
        const planet = planetsByLongitude[i];
        
        // Calculate position on the circle
        const angle = (planet.longitude / 360) * 2 * Math.PI - Math.PI / 2; // Start from top (- Math.PI/2)
        
        // Adjust radius slightly to avoid overlapping planets in the same sign
        const planetRadius = radius * (0.6 + (i % 3) * 0.1);
        
        const x = centerX + planetRadius * Math.cos(angle);
        const y = centerY + planetRadius * Math.sin(angle);
        
        // Draw planet symbol
        ctx.font = 'bold 16px Arial';
        ctx.fillStyle = planet.retrograde ? '#FF6B6B' : '#ffffff';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // Use symbol if available, otherwise use first letter
        const symbol = planetSymbols[planet.name] || planet.name[0];
        ctx.fillText(symbol, x, y);
        
        // Add small label with planet name
        ctx.font = '10px Arial';
        ctx.fillText(planet.name, x, y + 15);
    }
}
