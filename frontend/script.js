document.getElementById('checkRiskBtn').addEventListener('click', fetchPrediction);
document.getElementById('monitorAllBtn').addEventListener('click', fetchAllPredictions);
document.getElementById('cityInput').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') fetchPrediction();
});

// Single City Prediction
async function fetchPrediction() {
    const city = document.getElementById('cityInput').value.trim();
    if (!city) return;

    resetUI();
    const loadingEl = document.getElementById('loading');
    loadingEl.textContent = "Analyzing weather patterns & generating predictions...";
    loadingEl.classList.remove('hidden');

    try {
        const response = await fetch('http://127.0.0.1:8000/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city: city })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Failed to fetch prediction.");

        displaySingleResults(data);

    } catch (err) {
        showError(err.message);
    } finally {
        loadingEl.classList.add('hidden');
    }
}

// Multi-City India Monitoring
async function fetchAllPredictions() {
    resetUI();
    const loadingEl = document.getElementById('loading');
    loadingEl.textContent = "Fetching live data across India... Please wait.";
    loadingEl.classList.remove('hidden');

    try {
        const response = await fetch('http://127.0.0.1:8000/predict-all');
        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || "Failed to fetch predictions.");

        displayMultiResults(data.results);

    } catch (err) {
        showError(err.message);
    } finally {
        loadingEl.classList.add('hidden');
    }
}

function resetUI() {
    document.getElementById('error').classList.add('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('resultsGrid').classList.add('hidden');
    document.getElementById('loading').classList.add('hidden');
}

function showError(msg) {
    const errorEl = document.getElementById('error');
    errorEl.textContent = "Error: " + msg;
    errorEl.classList.remove('hidden');
}

// Render Single City
function displaySingleResults(data) {
    document.getElementById('resCity').textContent = data.city.toUpperCase();
    document.getElementById('resTemp').textContent = `${data.weather.temperature} °C`;
    document.getElementById('resHumidity').textContent = `${data.weather.humidity} %`;
    document.getElementById('resWind').textContent = `${data.weather.wind_speed} m/s`;
    document.getElementById('resRain').textContent = `${data.weather.rainfall} mm`;

    setAlertStyle('alertFlood', 'riskFlood', data.alerts.flood);
    setAlertStyle('alertThunderstorm', 'riskThunderstorm', data.alerts.thunderstorm);
    setAlertStyle('alertCloudburst', 'riskCloudburst', data.alerts.cloudburst);

    document.getElementById('results').classList.remove('hidden');
}

function setAlertStyle(containerId, textId, alertText) {
    const container = document.getElementById(containerId);
    const textEl = document.getElementById(textId);
    container.className = 'alert-item';
    textEl.textContent = alertText;

    if (alertText.includes("HIGH RISK")) container.classList.add('risk-high');
    else if (alertText.includes("MODERATE RISK")) container.classList.add('risk-moderate');
    else container.classList.add('risk-low');
}

// Render Multi-City (Sorted by Risk)
function displayMultiResults(resultsArray) {
    const resultsGrid = document.getElementById('resultsGrid');
    resultsGrid.innerHTML = ''; // Clear previous

    // Sort: HIGH risk cities at the top
    resultsArray.sort((a, b) => {
        const aHigh = Object.values(a.alerts).some(alert => alert.includes("HIGH"));
        const bHigh = Object.values(b.alerts).some(alert => alert.includes("HIGH"));
        if (aHigh && !bHigh) return -1;
        if (!aHigh && bHigh) return 1;
        return 0;
    });

    resultsArray.forEach(data => {
        const card = document.createElement('div');
        card.className = 'card small-card';
        
        // Determine border style based on highest risk
        const hasHigh = Object.values(data.alerts).some(alert => alert.includes("HIGH"));
        const hasMod = Object.values(data.alerts).some(alert => alert.includes("MODERATE"));
        
        if (hasHigh) card.classList.add('border-high');
        else if (hasMod) card.classList.add('border-moderate');
        else card.classList.add('border-low');
        
        card.innerHTML = `
            <h3>${data.city}</h3>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">
                Temp: ${data.weather.temperature}°C | Rain: ${data.weather.rainfall}mm
            </p>
            
            <div class="mini-alert ${getAlertClass(data.alerts.flood)}">
                <span>Flood Risk</span>
                <span>${data.alerts.flood.replace(' RISK', '')}</span>
            </div>
            <div class="mini-alert ${getAlertClass(data.alerts.thunderstorm)}">
                <span>Storm Risk</span>
                <span>${data.alerts.thunderstorm.replace(' RISK', '')}</span>
            </div>
            <div class="mini-alert ${getAlertClass(data.alerts.cloudburst)}">
                <span>Cloudburst Risk</span>
                <span>${data.alerts.cloudburst.replace(' RISK', '')}</span>
            </div>
        `;
        resultsGrid.appendChild(card);
    });

    resultsGrid.classList.remove('hidden');
}

function getAlertClass(alertText) {
    if (alertText.includes("HIGH")) return 'text-high';
    if (alertText.includes("MODERATE")) return 'text-moderate';
    return 'text-low';
}
