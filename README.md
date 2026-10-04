# Smart Traffic Congestion Prediction System

A machine learning-based web application that predicts **hourly traffic volume and congestion levels** using environmental, temporal, and weather-related parameters.

The system uses a **Random Forest Regressor** trained on the **Metro Interstate Traffic Volume Dataset** and provides an interactive Flask-based web interface for making traffic predictions.

---

## 📌 Project Overview

Traffic congestion is a major urban problem that leads to increased travel time, fuel consumption, emissions, and commuter stress.

This project develops a **Smart Traffic Congestion Prediction System** that estimates traffic volume based on factors such as:

* Hour of the day
* Day of the week
* Temperature
* Rain
* Snow
* Cloud cover
* Weather conditions
* Holiday / non-working day

The trained machine learning model is deployed through a **Flask web application**, allowing users to enter traffic and environmental conditions and receive a predicted traffic volume along with a congestion assessment.

---

## 🎯 Objectives

1. To analyze the relationship between traffic volume and environmental/temporal factors.
2. To perform exploratory data analysis on the traffic dataset.
3. To engineer useful time-based features from timestamps.
4. To train a machine learning model for traffic volume prediction.
5. To evaluate the model using statistical performance measures.
6. To deploy the trained model using Flask.
7. To provide an interactive dashboard for traffic congestion analysis.

---

## 📊 Dataset

The project uses the **Metro Interstate Traffic Volume Dataset**.

### Dataset Information

| Property        | Description                              |
| --------------- | ---------------------------------------- |
| Dataset         | Metro Interstate Traffic Volume          |
| Observations    | 48,204 hourly observations               |
| Location        | Westbound I-94 near Minneapolis–St. Paul |
| Period          | 2012–2018                                |
| Target Variable | `traffic_volume`                         |
| Data Type       | Time-series traffic data                 |

### Main Features

* `holiday`
* `temp`
* `rain_1h`
* `snow_1h`
* `clouds_all`
* `weather_main`
* `weather_description`
* `date_time`
* `traffic_volume`

The original dataset contains no reported missing values.

---

## 🧠 Machine Learning Model

The project uses a:

### Random Forest Regressor

Random Forest was selected because traffic patterns can have nonlinear relationships between time, weather, holidays, and traffic volume.

The model combines multiple decision trees to produce a more robust prediction.

### Model Workflow

```text
Raw Dataset
     ↓
Data Cleaning
     ↓
Exploratory Data Analysis
     ↓
Feature Engineering
     ↓
Encoding / Preprocessing
     ↓
Train-Test Split
     ↓
Random Forest Regressor
     ↓
Model Evaluation
     ↓
Model Serialization
     ↓
Flask Web Application
     ↓
Traffic Prediction
```

---

## 📈 Model Evaluation

The current project reports an approximate:

**R² Score: 95.3%**

The dashboard also reports:

**MAE: 325.58 vehicles/hour**

### Evaluation Metrics

| Metric   |                           Result |
| -------- | -------------------------------: |
| R² Score |                        **95.3%** |
| MAE      |         **325.58 vehicles/hour** |
| RMSE     | Calculated from test predictions |

### Meaning of Metrics

**R² Score:**
Measures how much of the variation in traffic volume is explained by the model.

**MAE:**
Represents the average absolute difference between the predicted and actual traffic volume.

**RMSE:**
Measures prediction error while giving greater importance to larger errors.

---

## 🌐 Web Application

The machine learning model is deployed using **Flask**.

The application provides an interactive dashboard where users can modify different parameters and predict traffic volume.

### User Inputs

* Hour of Day
* Day of Week
* Weather Condition
* Temperature
* Cloud Cover
* Rain
* Snow
* Holiday / Non-working Day

### Output

The system displays:

* Predicted traffic volume
* Congestion level
* Highway capacity load
* Traffic advisory
* Parameter summary

For example:

```text
Predicted Traffic Volume
        ↓
5,396 vehicles/hour

Congestion Level
        ↓
HIGH CONGESTION

Traffic Advisory
        ↓
Consider alternate routes
or delaying departure.
```

---

## 📁 Project Structure

```text
stats/
│
├── data/
│   └── metro_traffic.csv
│
├── models/
│   ├── metrics.json
│   └── traffic_model.joblib
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── main.js
│
├── templates/
│   └── [HTML templates]
│
├── app.py
├── train_model.py
├── requirements.txt
└── README.md
```

### File Description

| File / Folder                 | Purpose                     |
| ----------------------------- | --------------------------- |
| `data/metro_traffic.csv`      | Traffic dataset             |
| `models/traffic_model.joblib` | Trained Random Forest model |
| `models/metrics.json`         | Model evaluation metrics    |
| `static/css/style.css`        | Application styling         |
| `static/js/main.js`           | Frontend JavaScript         |
| `templates/`                  | Flask HTML templates        |
| `train_model.py`              | Model training script       |
| `app.py`                      | Flask application           |
| `requirements.txt`            | Python dependencies         |
| `README.md`                   | Project documentation       |

---

## ⚙️ Technologies Used

* **Python**
* **Flask**
* **Pandas**
* **NumPy**
* **Scikit-learn**
* **Joblib**
* **HTML**
* **CSS**
* **JavaScript**

---

## 🚀 Installation

### 1. Clone or download the project

```bash
git clone <repository-url>
cd stats
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

### Windows

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🏋️ Train the Model

If the model needs to be retrained, run:

```bash
python train_model.py
```

This generates the trained model and evaluation information inside the `models/` directory.

---

## ▶️ Run the Application

Start the Flask application using:

```bash
python app.py
```

The application will normally be available at:

```text
http://127.0.0.1:5000
```

Open the address in a web browser to access the dashboard.

---

## 🖥️ Application Features

### 1. Quick Test Scenarios

The dashboard provides preset scenarios such as:

* Morning Rush
* Evening Rush
* Storm Delay
* Late Night Clear

These allow users to quickly test different traffic conditions.

### 2. Environmental & Temporal Parameters

Users can modify:

* Time
* Day
* Temperature
* Cloud cover
* Rain
* Snow
* Holiday status
* Weather condition

### 3. Congestion Analytics

The system presents:

* Predicted traffic volume
* Congestion severity
* Highway capacity load
* Driver advisory
* Route intelligence

---

## 🔬 Exploratory Data Analysis

The project performs EDA to understand the relationship between traffic volume and its influencing variables.

Important steps include:

1. Checking the dataset structure.
2. Checking missing values.
3. Checking duplicates and data ranges.
4. Extracting time-related features.
5. Examining traffic distributions.
6. Analyzing peak-hour traffic patterns.
7. Studying correlations between variables.

### Correlation Analysis

The project uses Pearson correlation to screen linear relationships between traffic volume and selected variables.

Example results used in the analysis:

| Feature               | Pearson Correlation |
| --------------------- | ------------------: |
| Hour                  |              +0.173 |
| Weekday / Day-of-week |              −0.416 |
| Temperature           |              +0.128 |
| Rain                  |              +0.004 |
| Snow                  |              +0.001 |

Correlation indicates association and does not by itself establish causation.

---

## ⚠️ Limitations

The current system has several limitations:

* The dataset represents only one traffic corridor and direction.
* Historical data may not contain sudden accidents or road closures.
* Changes in travel behavior can reduce model performance.
* Weather and traffic conditions may change over time.
* Predictions are based on historical patterns and should not be treated as perfect real-time forecasts.

---

## 🔮 Future Scope

The system can be improved by:

1. Integrating **live traffic APIs**.
2. Integrating real-time **weather APIs**.
3. Adding accident and roadwork information.
4. Using time-aware validation techniques.
5. Adding prediction uncertainty intervals.
6. Implementing model drift monitoring.
7. Adding explainable AI techniques.
8. Training on multiple traffic corridors.
9. Performing environmental-equity analysis.
10. Continuously retraining the model using new traffic data.

---

## 👥 Team Members

**Statistics for Machine Learning and Data Science Lab**

* Satyamkumar Singh — Roll No. 52
* Vaibhav Singh — Roll No. 53
* Yash Thakur — Roll No. 58

**Department:** Artificial Intelligence & Data Science
**Course Code:** 2015111

---

## 📌 Conclusion

The Smart Traffic Congestion Prediction System demonstrates how machine learning can be used to estimate traffic volume from temporal and environmental conditions. A Random Forest Regressor provides the prediction engine, while Flask provides an interactive web-based interface.

The current project reports an **R² score of approximately 95.3%** and an **MAE of 325.58 vehicles/hour**, demonstrating a strong baseline for traffic-volume prediction. Future integration with live traffic, weather, incident, and roadwork data can make the system more suitable for real-world traffic management.
