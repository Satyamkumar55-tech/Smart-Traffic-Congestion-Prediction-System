import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'models')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

DATASET_PATH = os.path.join(DATA_DIR, 'metro_traffic.csv')
MODEL_PATH = os.path.join(MODEL_DIR, 'traffic_model.joblib')
METRICS_PATH = os.path.join(MODEL_DIR, 'metrics.json')

# Standard weather main categories matching Kaggle Metro Interstate Traffic dataset
WEATHER_CATEGORIES = [
    'Clear', 'Clouds', 'Rain', 'Drizzle', 'Mist', 'Fog', 'Snow', 'Haze', 'Thunderstorm'
]

HOLIDAYS = [
    'None', 'Columbus Day', 'Veterans Day', 'Thanksgiving Day', 
    'Christmas Day', 'New Years Day', 'Labor Day', 'Independence Day', 'Memorial Day'
]

def generate_synthetic_metro_traffic_dataset(num_rows=6000):
    """
    Generates a realistic synthetic Metro Interstate Traffic Volume dataset
    mirroring the structure and distributions of the Kaggle Metro Interstate Traffic Volume dataset.
    """
    print(f"Generating realistic Metro Interstate Traffic Volume dataset ({num_rows} records)...")
    np.random.seed(42)
    start_date = datetime(2023, 1, 1, 0, 0, 0)
    
    dates = [start_date + timedelta(hours=i) for i in range(num_rows)]
    
    data = []
    for d in dates:
        hour = d.hour
        day_of_week = d.weekday() # 0 = Mon, 6 = Sun
        month = d.month
        
        # Holiday selection (rare ~2%)
        is_holiday_sample = np.random.rand() < 0.02
        holiday = np.random.choice(HOLIDAYS[1:]) if is_holiday_sample else 'None'
        
        # Temperature in Kelvin (min ~245K (-28C), max ~310K (+37C))
        base_temp_c = 15 + 15 * np.sin((month - 4) / 12 * 2 * np.pi) # seasonal variation
        daily_variation = 5 * np.sin((hour - 9) / 24 * 2 * np.pi)
        noise_temp = np.random.normal(0, 3)
        temp_c = base_temp_c + daily_variation + noise_temp
        temp_k = temp_c + 273.15
        
        # Weather main category
        weather_p = [0.40, 0.28, 0.12, 0.05, 0.05, 0.03, 0.04, 0.02, 0.01]
        weather_main = np.random.choice(WEATHER_CATEGORIES, p=weather_p)
        
        # Rain & Snow mm
        rain_1h = 0.0
        if weather_main in ['Rain', 'Thunderstorm']:
            rain_1h = round(float(np.random.exponential(scale=2.5)), 2)
        elif weather_main == 'Drizzle':
            rain_1h = round(float(np.random.uniform(0.1, 1.2)), 2)
            
        snow_1h = 0.0
        if weather_main == 'Snow':
            snow_1h = round(float(np.random.exponential(scale=1.5)), 2)
            
        # Cloud cover percentage
        if weather_main == 'Clear':
            clouds_all = int(np.random.uniform(0, 15))
        elif weather_main == 'Clouds':
            clouds_all = int(np.random.uniform(40, 100))
        else:
            clouds_all = int(np.random.uniform(60, 100))
            
        # Traffic Volume calculation based on hour, day of week, holiday, weather
        # Hourly profile:
        # Rush hours: 7-9 AM (morning peak) and 16-18 PM (evening peak)
        if 0 <= hour <= 5:
            base_vol = 300 + hour * 120
        elif 6 <= hour <= 9:
            base_vol = 3500 + (hour - 6) * 1100 + np.random.randint(-200, 300)
        elif 10 <= hour <= 14:
            base_vol = 4200 + np.random.randint(-400, 400)
        elif 15 <= hour <= 18:
            base_vol = 4800 + (18 - hour) * 400 + np.random.randint(-300, 500)
        else:
            base_vol = 3800 - (hour - 18) * 600
            
        # Weekend adjustment (-35% peak volume, shifted schedule)
        if day_of_week >= 5:
            base_vol = base_vol * 0.65 + np.random.randint(-200, 300)
            
        # Holiday adjustment (-50% volume)
        if holiday != 'None':
            base_vol *= 0.45
            
        # Weather impact (adverse weather reduces speed/volume slightly or creates bottleneck spikes)
        if weather_main in ['Snow', 'Thunderstorm', 'Fog']:
            base_vol *= 0.88
        elif weather_main == 'Rain':
            base_vol *= 0.94
            
        # Add random realistic variance
        traffic_volume = int(np.clip(base_vol + np.random.normal(0, 350), 150, 7200))
        
        data.append({
            'date_time': d.strftime('%Y-%m-%d %H:%M:%S'),
            'holiday': holiday,
            'temp': round(temp_k, 2),
            'rain_1h': rain_1h,
            'snow_1h': snow_1h,
            'clouds_all': clouds_all,
            'weather_main': weather_main,
            'traffic_volume': traffic_volume
        })
        
    df = pd.DataFrame(data)
    df.to_csv(DATASET_PATH, index=False)
    print(f"Dataset successfully created and saved to '{DATASET_PATH}' ({len(df)} rows).")
    return df

def preprocess_data(df):
    """
    Preprocesses raw dataset:
    - Parses date_time into hour, day_of_week, month
    - Converts temperature from Kelvin to Celsius
    - Creates binary is_holiday flag
    - Encodes weather_main category
    - Returns feature matrix X, target y, and weather LabelEncoder
    """
    df = df.copy()
    
    # Handle missing values if any
    df.ffill(inplace=True)
    
    # Feature engineering from date_time
    if 'date_time' in df.columns:
        df['date_time'] = pd.to_datetime(df['date_time'])
        df['hour'] = df['date_time'].dt.hour
        df['day_of_week'] = df['date_time'].dt.dayofweek # 0=Mon, 6=Sun
        df['month'] = df['date_time'].dt.month
    else:
        # Fallbacks if columns already extracted
        if 'hour' not in df.columns: df['hour'] = 12
        if 'day_of_week' not in df.columns: df['day_of_week'] = 0
        if 'month' not in df.columns: df['month'] = 6
        
    # Temperature conversion: Kelvin to Celsius
    # If temp is > 200, assume Kelvin
    if 'temp' in df.columns:
        df['temp_c'] = df['temp'].apply(lambda k: k - 273.15 if k > 200 else k)
    elif 'temp_c' in df.columns:
        df['temp_c'] = df['temp_c']
    else:
        df['temp_c'] = 20.0 # default 20C
        
    # Binary holiday feature
    if 'holiday' in df.columns:
        df['is_holiday'] = df['holiday'].apply(lambda h: 0 if str(h).strip().lower() in ['none', '0', 'false', 'nan', ''] else 1)
    else:
        df['is_holiday'] = 0
        
    # Weather Main encoding
    le_weather = LabelEncoder()
    # Fit encoder on expected complete category list to ensure all labels are known
    le_weather.fit(WEATHER_CATEGORIES)
    
    # Transform existing values, fallback to 'Clear' if unknown category
    df['weather_main'] = df['weather_main'].apply(lambda w: w if w in WEATHER_CATEGORIES else 'Clear')
    df['weather_encoded'] = le_weather.transform(df['weather_main'])
    
    # Selected feature columns for model input
    feature_columns = ['hour', 'day_of_week', 'temp_c', 'rain_1h', 'snow_1h', 'clouds_all', 'is_holiday', 'weather_encoded']
    
    X = df[feature_columns]
    y = df['traffic_volume'] if 'traffic_volume' in df.columns else None
    
    return X, y, le_weather, feature_columns

def train_and_save_model():
    """
    Loads dataset, trains Random Forest model, calculates performance metrics,
    and exports trained model + metadata to joblib file.
    """
    if not os.path.exists(DATASET_PATH):
        df = generate_synthetic_metro_traffic_dataset()
    else:
        print(f"Loading existing traffic dataset from '{DATASET_PATH}'...")
        df = pd.read_csv(DATASET_PATH)
        
    print("Preprocessing data and engineering features...")
    X, y, le_weather, feature_columns = preprocess_data(df)
    
    # Train-test split (80/20)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    print(f"Training Random Forest Regressor on {len(X_train)} samples...")
    model = RandomForestRegressor(
        n_estimators=120,
        max_depth=16,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # Model evaluation
    y_pred = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2 = float(r2_score(y_test, y_pred))
    
    metrics = {
        'mae': round(mae, 2),
        'rmse': round(rmse, 2),
        'r2_score': round(r2, 4),
        'total_samples': len(df),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'model_name': 'Random Forest Regressor'
    }
    
    print("=" * 50)
    print("MODEL PERFORMANCE METRICS:")
    print(f"  - R² Score: {metrics['r2_score']:.4f}")
    print(f"  - MAE (Vehicles/hr): {metrics['mae']:.2f}")
    print(f"  - RMSE (Vehicles/hr): {metrics['rmse']:.2f}")
    print("=" * 50)
    
    # Save model artifact bundle
    model_bundle = {
        'model': model,
        'feature_columns': feature_columns,
        'weather_categories': list(le_weather.classes_),
        'metrics': metrics
    }
    
    joblib.dump(model_bundle, MODEL_PATH)
    print(f"Model bundle saved to '{MODEL_PATH}'.")
    
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=4)
        
    return model_bundle

if __name__ == '__main__':
    train_and_save_model()
