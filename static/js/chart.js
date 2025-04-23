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
    
    const signElements = [
        'Fire', 'Earth', 'Air', 'Water',
        'Fire', 'Earth', 'Air', 'Water',
        'Fire', 'Earth', 'Air', 'Water'
    ];
    
    const elementColors = {
        'Fire': '#FF5733',
        'Earth': '#8B4513',
        'Air': '#87CEEB',
        'Water': '#0000FF'
    };
    
    // Create a circular chart
    const ctx = canvas.getContext('2d');
    
    // Clear any existing chart
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 20; // Slightly smaller to leave room for degree markers
    
    // Draw the western style zodiac wheel
    drawWesternZodiacWheel(ctx, centerX, centerY, radius, zodiacSigns, signColors, signElements);
    
    // Plot planets on the wheel
    plotPlanets(ctx, centerX, centerY, radius, planets);
    
    // Add a title to the chart
    ctx.font = 'bold 14px Arial';
    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('Vedic Chart - Sidereal Zodiac', centerX, 20);
}

function drawWesternZodiacWheel(ctx, centerX, centerY, radius, zodiacSigns, signColors, signElements) {
    // Draw outer circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Inner circle for houses
    const innerRadius = radius * 0.75;
    ctx.beginPath();
    ctx.arc(centerX, centerY, innerRadius, 0, 2 * Math.PI);
    ctx.strokeStyle = '#aaaaaa';
    ctx.lineWidth = 1;
    ctx.stroke();
    
    // Draw the zodiac wheel with 12 segments (signs)
    for (let i = 0; i < 12; i++) {
        // Each sign spans 30 degrees, convert to radians
        // Note: We subtract Math.PI/2 to start from the top (traditional astrological chart)
        const startAngle = (2 * Math.PI * i / 12) - Math.PI/2;
        const endAngle = (2 * Math.PI * (i + 1) / 12) - Math.PI/2;
        
        // Draw zodiac segment
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, startAngle, endAngle);
        ctx.closePath();
        
        // Color based on element
        const element = signElements[i];
        const baseColor = elementColors[element];
        
        // Fill with sign color (with transparency)
        ctx.fillStyle = signColors[i] + '30'; // 30 = 19% opacity
        ctx.fill();
        
        // Draw outline
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.stroke();
        
        // Draw degree markers (every 5 degrees)
        for (let deg = 0; deg < 30; deg += 5) {
            const markerAngle = startAngle + (deg / 30) * (endAngle - startAngle);
            const markerLength = (deg % 10 === 0) ? 15 : 10; // Longer markers for multiples of 10
            
            const innerX = centerX + (radius - markerLength) * Math.cos(markerAngle);
            const innerY = centerY + (radius - markerLength) * Math.sin(markerAngle);
            const outerX = centerX + radius * Math.cos(markerAngle);
            const outerY = centerY + radius * Math.sin(markerAngle);
            
            ctx.beginPath();
            ctx.moveTo(innerX, innerY);
            ctx.lineTo(outerX, outerY);
            ctx.strokeStyle = '#aaaaaa';
            ctx.lineWidth = 1;
            ctx.stroke();
            
            // Add degree numbers for multiples of 10
            if (deg % 10 === 0) {
                const textRadius = radius + 15;
                const textX = centerX + textRadius * Math.cos(markerAngle);
                const textY = centerY + textRadius * Math.sin(markerAngle);
                
                ctx.font = '10px Arial';
                ctx.fillStyle = '#aaaaaa';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(deg.toString(), textX, textY);
            }
        }
        
        // Add zodiac sign label
        const labelRadius = radius * 0.87;
        const labelAngle = startAngle + (endAngle - startAngle) / 2;
        const labelX = centerX + labelRadius * Math.cos(labelAngle);
        const labelY = centerY + labelRadius * Math.sin(labelAngle);
        
        ctx.font = 'bold 14px Arial';
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(zodiacSigns[i], labelX, labelY);
        
        // Add element symbol
        const elementRadius = radius * 0.8;
        const elementX = centerX + elementRadius * Math.cos(labelAngle);
        const elementY = centerY + elementRadius * Math.sin(labelAngle);
        
        // Symbol based on element
        let elementSymbol = '';
        switch (signElements[i]) {
            case 'Fire': elementSymbol = '△'; break;
            case 'Earth': elementSymbol = '□'; break;
            case 'Air': elementSymbol = '⬠'; break;
            case 'Water': elementSymbol = '◬'; break;
        }
        
        ctx.font = '12px Arial';
        ctx.fillStyle = elementColors[signElements[i]];
        ctx.fillText(elementSymbol, elementX, elementY - 15);
    }
    
    // Draw center circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, 5, 0, 2 * Math.PI);
    ctx.fillStyle = '#ffffff';
    ctx.fill();
    
    // Add a legend for elements
    const legendX = centerX - radius - 20;
    const legendY = centerY - radius - 40;
    
    ctx.font = '12px Arial';
    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'left';
    ctx.fillText('Elements:', legendX, legendY);
    
    let yOffset = 15;
    for (const element in elementColors) {
        ctx.fillStyle = elementColors[element];
        ctx.fillText(`■ ${element}`, legendX, legendY + yOffset);
        yOffset += 15;
    }
}

function plotPlanets(ctx, centerX, centerY, radius, planets) {
    // Planet symbols and colors
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
        'Pluto': '♇',
        'Rahu': '☊',  // North Node
        'Ketu': '☋'   // South Node
    };
    
    const planetColors = {
        'Sun': '#FFD700',      // Gold
        'Moon': '#F0F0F0',     // Silver/white
        'Mercury': '#7786B3',  // Blue-grey
        'Venus': '#77DD77',    // Green
        'Mars': '#FF6B6B',     // Red
        'Jupiter': '#7B68EE',  // Purple
        'Saturn': '#708090',   // Grey
        'Uranus': '#40E0D0',   // Turquoise
        'Neptune': '#6495ED',  // Blue
        'Pluto': '#8B4513',    // Brown
        'Rahu': '#483D8B',     // Dark blue
        'Ketu': '#8B008B'      // Dark magenta
    };
    
    // Group planets by zodiac sign (each 30 degrees)
    const planetsBySign = {};
    
    planets.forEach(planet => {
        // Get which 30-degree segment the planet is in
        const signIndex = Math.floor(planet.longitude / 30);
        if (!planetsBySign[signIndex]) {
            planetsBySign[signIndex] = [];
        }
        planetsBySign[signIndex].push(planet);
    });
    
    // Now plot planets, with planets in the same sign staggered
    for (const signIndex in planetsBySign) {
        const planetsInSign = planetsBySign[signIndex];
        
        // Sort planets by exact position within sign
        planetsInSign.sort((a, b) => (a.longitude % 30) - (b.longitude % 30));
        
        // Calculate how to stagger planets in the same sign
        const middleAngle = ((parseInt(signIndex) * 30) + 15) * Math.PI / 180 - Math.PI/2;
        
        // Plot each planet
        for (let i = 0; i < planetsInSign.length; i++) {
            const planet = planetsInSign[i];
            
            // Calculate exact position on the circle
            const angle = (planet.longitude / 360) * 2 * Math.PI - Math.PI/2; // Start from top (- Math.PI/2)
            
            // Stagger planets in the same sign
            const offset = (i - (planetsInSign.length - 1) / 2) * 0.1;
            const planetRadius = radius * (0.6 + offset);
            
            const x = centerX + planetRadius * Math.cos(angle);
            const y = centerY + planetRadius * Math.sin(angle);
            
            // Draw planet symbol
            ctx.font = 'bold 18px Arial';
            
            // White outline for better visibility
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 3;
            ctx.strokeText(planetSymbols[planet.name] || planet.name[0], x, y);
            
            // Actual planet color
            ctx.fillStyle = planetColors[planet.name] || '#ffffff';
            if (planet.retrograde) {
                // Add R symbol for retrograde planets
                ctx.fillText(`${planetSymbols[planet.name]}`, x, y);
                ctx.font = 'bold 10px Arial';
                ctx.fillText('R', x + 10, y - 10);
            } else {
                ctx.fillText(`${planetSymbols[planet.name]}`, x, y);
            }
            
            // Add position label
            const posInSign = Math.round(planet.longitude % 30 * 100) / 100;
            const posLabel = `${planet.name}: ${posInSign.toFixed(1)}°`;
            
            // Calculate position for the label
            const labelRadius = radius * 0.4;
            const labelX = centerX + labelRadius * Math.cos(angle);
            const labelY = centerY + labelRadius * Math.sin(angle);
            
            // Draw a line connecting planet and label
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(labelX, labelY);
            ctx.strokeStyle = '#aaaaaa';
            ctx.lineWidth = 0.5;
            ctx.stroke();
            
            // Draw label with background
            const labelWidth = ctx.measureText(posLabel).width + 10;
            const labelHeight = 16;
            
            ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            ctx.fillRect(labelX - labelWidth/2, labelY - labelHeight/2, labelWidth, labelHeight);
            
            ctx.font = '10px Arial';
            ctx.fillStyle = '#ffffff';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(posLabel, labelX, labelY);
        }
    }
    
    // Add a legend for retrograde planets
    ctx.font = '12px Arial';
    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'left';
    ctx.fillText('R = Retrograde', centerX + radius - 80, centerY - radius - 10);
}
