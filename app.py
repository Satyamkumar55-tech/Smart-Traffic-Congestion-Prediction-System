import os
import json
import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify

# Base Directory Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'traffic_model.joblib')

app = Flask(__name__)

# Global model and metadata variables
model = None
weather_categories = [
    'Clear', 'Clouds', 'Rain', 'Drizzle', 'Mist', 'Fog', 'Snow', 'Haze', 'Thunderstorm'
]
feature_columns = ['hour', 'day_of_week', 'temp_c', 'rain_1h', 'snow_1h', 'clouds_all', 'is_holiday', 'weather_encoded']
model_metrics = {
    'mae': 285.5,
    'rmse': 390.2,
    'r2_score': 0.942,
    'model_name': 'Random Forest Regressor'
}

def load_or_train_model():
    """
    Loads pre-trained model artifact bundle from disk.
    If not found, executes train_model script to train and save a fresh model.
    """
    global model, weather_categories, feature_columns, model_metrics
    
    if not os.path.exists(MODEL_PATH):
        print("Model file not found. Running dataset generation & model training script...")
        from train_model import train_and_save_model
        train_and_save_model()
        
    print(f"Loading trained model from '{MODEL_PATH}'...")
    bundle = joblib.load(MODEL_PATH)
    model = bundle['model']
    feature_columns = bundle.get('feature_columns', feature_columns)
    weather_categories = bundle.get('weather_categories', weather_categories)
    model_metrics = bundle.get('metrics', model_metrics)
    print("Model loaded successfully!")

# Ensure model is ready when Flask app loads
with app.app_context():
    load_or_train_model()

def determine_congestion_level(volume):
    """
    Categorizes predicted traffic volume into low, moderate, or high congestion levels
    along with visual styling badges, color codes, and actionable traffic advice.
    """
    # Max realistic capacity on I-94 segment is ~7500 vehicles/hour
    max_capacity = 7500.0
    congestion_pct = min(100, max(0, round((volume / max_capacity) * 100, 1)))
    
    if volume < 2200:
        level = "Low"
        badge_class = "success"
        color = "#10b981" # Emerald Green
        icon = "fa-circle-check"
        summary = "Free Flowing Traffic"
        advice = "Road conditions are clear with minimal traffic. Ideal time for travel with normal speeds."
    elif volume <= 4800:
        level = "Moderate"
        badge_class = "warning"
        color = "#f59e0b" # Amber Yellow
        icon = "fa-triangle-exclamation"
        summary = "Moderate Congestion"
        advice = "Expect standard commuter slowdowns during peak intervals. Allow 10-15 extra travel minutes."
    else:
        level = "High"
        badge_class = "danger"
        color = "#ef4444" # Vivid Red
        icon = "fa-circle-exclamation"
        summary = "Severe Traffic Jam"
        advice = "Heavy congestion detected on main interstate corridors! Consider alternate bypass routes or delaying departure by 45 mins."

    return {
        'level': level,
        'badge_class': badge_class,
        'color': color,
        'icon': icon,
        'summary': summary,
        'advice': advice,
        'congestion_pct': congestion_pct
    }

@app.route('/')
def home():
    """
    Home page route rendering the interactive traffic prediction UI.
    """
    days = [
        {'id': 0, 'name': 'Monday'},
        {'id': 1, 'name': 'Tuesday'},
        {'id': 2, 'name': 'Wednesday'},
        {'id': 3, 'name': 'Thursday'},
        {'id': 4, 'name': 'Friday'},
        {'id': 5, 'name': 'Saturday'},
        {'id': 6, 'name': 'Sunday'}
    ]
    return render_template(
        'index.html',
        weather_options=weather_categories,
        days_of_week=days,
        metrics=model_metrics
    )

@app.route('/predict', methods=['POST'])
def predict():
    """
    Prediction route: receives user input parameters via Form or JSON request,
    runs inference using the Scikit-Learn model, and returns traffic predictions.
    """
    try:
        # Check if request is JSON or form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        # Extract features with sensible defaults
        hour = int(data.get('hour', 8))
        day_of_week = int(data.get('day_of_week', 0))
        temp_c = float(data.get('temp_c', 20.0))
        rain_1h = float(data.get('rain_1h', 0.0))
        snow_1h = float(data.get('snow_1h', 0.0))
        clouds_all = int(data.get('clouds_all', 20))
        weather_main = str(data.get('weather_main', 'Clear')).strip()
        is_holiday = int(data.get('is_holiday', 0))

        # Encode weather_main to match training label encoding index
        if weather_main in weather_categories:
            weather_encoded = weather_categories.index(weather_main)
        else:
            weather_encoded = 0 # default to 'Clear'

        # Construct input DataFrame matching exact feature column names
        input_data = pd.DataFrame([{
            'hour': hour,
            'day_of_week': day_of_week,
            'temp_c': temp_c,
            'rain_1h': rain_1h,
            'snow_1h': snow_1h,
            'clouds_all': clouds_all,
            'is_holiday': is_holiday,
            'weather_encoded': weather_encoded
        }])[feature_columns]

        # Model inference
        raw_prediction = model.predict(input_data)[0]
        predicted_volume = max(0, int(round(raw_prediction)))

        # Determine traffic congestion details
        congestion_info = determine_congestion_level(predicted_volume)

        response_payload = {
            'success': True,
            'predicted_volume': predicted_volume,
            'formatted_volume': f"{predicted_volume:,}",
            'congestion': congestion_info,
            'inputs_summary': {
                'hour': f"{hour:02d}:00",
                'day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day_of_week],
                'temp': f"{temp_c:.1f}°C ({temp_c * 9/5 + 32:.1f}°F)",
                'weather': weather_main,
                'is_holiday': "Yes" if is_holiday else "No"
            }
        }

        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(response_payload)
        
        # If standard form submit without JS, render template with result
        days = [{'id': 0, 'name': 'Monday'}, {'id': 1, 'name': 'Tuesday'}, {'id': 2, 'name': 'Wednesday'},
                {'id': 3, 'name': 'Thursday'}, {'id': 4, 'name': 'Friday'}, {'id': 5, 'name': 'Saturday'}, {'id': 6, 'name': 'Sunday'}]
        return render_template(
            'index.html',
            weather_options=weather_categories,
            days_of_week=days,
            metrics=model_metrics,
            result=response_payload
        )

    except Exception as e:
        error_msg = f"Prediction Error: {str(e)}"
        print(error_msg)
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': error_msg}), 400
        return render_template('index.html', error=error_msg), 400

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})

if __name__ == '__main__':
    # Run Flask local dev server
    print("Starting Smart Traffic Congestion Prediction Flask App...")
    app.run(host='127.0.0.1', port=5000, debug=True)
