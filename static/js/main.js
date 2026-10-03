/**
 * Smart Traffic Congestion Prediction System - Frontend Interactions & AJAX Handling
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initial display setup
    const hourInput = document.getElementById('hour');
    if (hourInput) updateHourDisplay(hourInput.value);

    const tempInput = document.getElementById('temp_c');
    if (tempInput) updateTempDisplay(tempInput.value);

    // Attach AJAX form submission
    const form = document.getElementById('prediction-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
});

/**
 * Format 24-hour integer to 12-hour AM/PM string
 */
function updateHourDisplay(val) {
    const h = parseInt(val, 10);
    const ampm = h >= 12 ? 'PM' : 'AM';
    const displayHour = h % 12 === 0 ? 12 : h % 12;
    const formatted = `${displayHour.toString().padStart(2, '0')}:00 ${ampm}`;
    
    const label = document.getElementById('hour-val');
    if (label) label.innerText = formatted;
}

/**
 * Update temperature display in Celsius & Fahrenheit
 */
function updateTempDisplay(val) {
    const tempC = parseFloat(val);
    const tempF = (tempC * 9/5 + 32).toFixed(1);
    const label = document.getElementById('temp-val');
    if (label) label.innerText = `${tempC.toFixed(1)} °C (${tempF} °F)`;
}

/**
 * Apply predefined scenario presets for fast interactive testing
 */
function applyPreset(scenario) {
    const hourEl = document.getElementById('hour');
    const dayEl = document.getElementById('day_of_week');
    const weatherEl = document.getElementById('weather_main');
    const tempEl = document.getElementById('temp_c');
    const rainEl = document.getElementById('rain_1h');
    const snowEl = document.getElementById('snow_1h');
    const cloudsEl = document.getElementById('clouds_all');
    const holidayCheck = document.getElementById('is_holiday_check');
    const holidayHidden = document.getElementById('is_holiday');

    switch (scenario) {
        case 'morning_rush':
            hourEl.value = 8;
            dayEl.value = 1; // Tuesday
            weatherEl.value = 'Clear';
            tempEl.value = 18.0;
            rainEl.value = 0.0;
            snowEl.value = 0.0;
            cloudsEl.value = 10;
            holidayCheck.checked = false;
            holidayHidden.value = '0';
            break;

        case 'evening_rush':
            hourEl.value = 17; // 5 PM
            dayEl.value = 4; // Friday
            weatherEl.value = 'Clouds';
            tempEl.value = 24.5;
            rainEl.value = 0.0;
            snowEl.value = 0.0;
            cloudsEl.value = 60;
            holidayCheck.checked = false;
            holidayHidden.value = '0';
            break;

        case 'heavy_rain':
            hourEl.value = 16; // 4 PM
            dayEl.value = 3; // Thursday
            weatherEl.value = 'Thunderstorm';
            tempEl.value = 16.0;
            rainEl.value = 14.5;
            snowEl.value = 0.0;
            cloudsEl.value = 95;
            holidayCheck.checked = false;
            holidayHidden.value = '0';
            break;

        case 'late_night':
            hourEl.value = 2; // 2 AM
            dayEl.value = 6; // Sunday
            weatherEl.value = 'Clear';
            tempEl.value = 12.0;
            rainEl.value = 0.0;
            snowEl.value = 0.0;
            cloudsEl.value = 0;
            holidayCheck.checked = false;
            holidayHidden.value = '0';
            break;
    }

    // Trigger input update event listeners
    updateHourDisplay(hourEl.value);
    updateTempDisplay(tempEl.value);
    document.getElementById('clouds-val').innerText = `${cloudsEl.value} %`;

    // Automatically trigger prediction for immediate user feedback
    document.getElementById('predict-btn').click();
}

/**
 * Handle form submission asynchronously with AJAX fetch
 */
async function handleFormSubmit(e) {
    e.preventDefault();

    const emptyState = document.getElementById('empty-state');
    const loadingState = document.getElementById('loading-state');
    const resultContainer = document.getElementById('result-container');
    const form = e.target;

    // Show loading state
    if (emptyState) emptyState.classList.add('hidden');
    if (resultContainer) resultContainer.classList.add('hidden');
    if (loadingState) loadingState.classList.remove('hidden');

    const formData = new FormData(form);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();

        if (!data.success) {
            alert(data.error || 'Prediction failed.');
            if (loadingState) loadingState.classList.add('hidden');
            if (emptyState) emptyState.classList.remove('hidden');
            return;
        }

        // Render response data dynamically into dashboard
        renderResult(data);

        // Hide loader, show result
        if (loadingState) loadingState.classList.add('hidden');
        if (resultContainer) resultContainer.classList.remove('hidden');

    } catch (err) {
        console.error('AJAX Error:', err);
        alert('An unexpected error occurred while processing prediction.');
        if (loadingState) loadingState.classList.add('hidden');
        if (emptyState) emptyState.classList.remove('hidden');
    }
}

/**
 * Render dynamic prediction data into the dashboard UI
 */
function renderResult(data) {
    const res = data;
    const cong = res.congestion;

    const html = `
        <!-- Dynamic Top Status Badge -->
        <div class="congestion-status-box badge-${cong.badge_class}">
            <div class="status-icon">
                <i class="fa-solid ${cong.icon}"></i>
            </div>
            <div class="status-details">
                <span class="status-tag">${cong.level} CONGESTION</span>
                <h3 class="status-title">${cong.summary}</h3>
            </div>
        </div>

        <!-- Volume Big Counter Card -->
        <div class="volume-display-card">
            <span class="volume-label">PREDICTED TRAFFIC VOLUME</span>
            <div class="volume-number-wrap">
                <span class="volume-number">${res.formatted_volume}</span>
                <span class="volume-unit">vehicles / hr</span>
            </div>
            <p class="volume-subtitle">Estimated Westbound I-94 Freeway Traffic</p>
        </div>

        <!-- Traffic Capacity Meter Gauge -->
        <div class="gauge-container">
            <div class="gauge-header">
                <span>Highway Capacity Load</span>
                <span class="gauge-pct">${cong.congestion_pct}%</span>
            </div>
            <div class="progress-track">
                <div class="progress-fill progress-${cong.badge_class}" style="width: ${cong.congestion_pct}%;"></div>
            </div>
            <div class="gauge-labels">
                <span>0 (Low)</span>
                <span>3,500 (Moderate)</span>
                <span>7,500+ (High)</span>
            </div>
        </div>

        <!-- AI Traffic Advisory Box -->
        <div class="advisory-box">
            <h4><i class="fa-solid fa-compass"></i> Driver Advisory & Route Intelligence</h4>
            <p>${cong.advice}</p>
        </div>

        <!-- Input Parameters Recap -->
        <div class="input-recap">
            <h4><i class="fa-solid fa-list-check"></i> Parameter Summary</h4>
            <div class="recap-grid">
                <div class="recap-item"><span>Time:</span> <strong>${res.inputs_summary.hour}</strong></div>
                <div class="recap-item"><span>Day:</span> <strong>${res.inputs_summary.day}</strong></div>
                <div class="recap-item"><span>Weather:</span> <strong>${res.inputs_summary.weather}</strong></div>
                <div class="recap-item"><span>Temp:</span> <strong>${res.inputs_summary.temp}</strong></div>
            </div>
        </div>
    `;

    const resultContainer = document.getElementById('result-container');
    if (resultContainer) {
        resultContainer.innerHTML = html;
    }
}
