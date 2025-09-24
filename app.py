"""
Digital Twin MedTech MVP - Main Application
Real-time wearable device data collection, analysis, and patient deterioration prediction
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import json
import datetime
from datetime import datetime as dt, timedelta
import schedule
import time
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Digital Twin MedTech MVP",
    description="Real-time wearable device data collection and patient deterioration prediction",
    version="1.0.0"
)

# Enable CORS for Power BI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class WearableData(BaseModel):
    patient_id: str
    timestamp: datetime.datetime
    heart_rate: float
    blood_pressure_systolic: float
    blood_pressure_diastolic: float
    temperature: float
    oxygen_saturation: float
    activity_level: float

class PatientRecord(BaseModel):
    patient_id: str
    name: str
    age: int
    gender: str
    medical_conditions: List[str]

class PredictionResult(BaseModel):
    patient_id: str
    timestamp: datetime.datetime
    deterioration_risk: float
    risk_level: str
    contributing_factors: List[str]

# Global variables for ML model
ml_model = None
scaler = None
is_model_trained = False

# Database initialization
def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect('digital_twin.db')
    cursor = conn.cursor()
    
    # Wearable data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wearable_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            heart_rate REAL,
            blood_pressure_systolic REAL,
            blood_pressure_diastolic REAL,
            temperature REAL,
            oxygen_saturation REAL,
            activity_level REAL
        )
    ''')
    
    # Patient records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            medical_conditions TEXT
        )
    ''')
    
    # Predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            deterioration_risk REAL,
            risk_level TEXT,
            contributing_factors TEXT,
            actual_outcome INTEGER DEFAULT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def train_ml_model():
    """Train ML model with sample data for patient deterioration prediction"""
    global ml_model, scaler, is_model_trained
    
    try:
        # Generate sample training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: heart_rate, bp_systolic, bp_diastolic, temperature, oxygen_sat, activity
        X = np.random.normal(0, 1, (n_samples, 6))
        
        # Normalize features to realistic ranges
        X[:, 0] = np.clip(X[:, 0] * 20 + 80, 40, 180)  # heart rate
        X[:, 1] = np.clip(X[:, 1] * 20 + 120, 80, 200)  # systolic BP
        X[:, 2] = np.clip(X[:, 2] * 10 + 80, 50, 120)   # diastolic BP
        X[:, 3] = np.clip(X[:, 3] * 2 + 98.6, 95, 105)  # temperature
        X[:, 4] = np.clip(X[:, 4] * 5 + 97, 85, 100)    # oxygen saturation
        X[:, 5] = np.clip(X[:, 5] * 3 + 5, 0, 10)       # activity level
        
        # Generate labels (deterioration risk)
        # High risk conditions: high HR, high/low BP, high temp, low O2 sat, low activity
        risk_score = (
            (X[:, 0] > 100) * 0.3 +  # high heart rate
            ((X[:, 1] > 140) | (X[:, 1] < 90)) * 0.25 +  # abnormal systolic BP
            (X[:, 3] > 100.4) * 0.2 +  # fever
            (X[:, 4] < 95) * 0.3 +  # low oxygen saturation
            (X[:, 5] < 2) * 0.15  # low activity
        )
        
        y = (risk_score > 0.4).astype(int)  # Binary classification
        
        # Train model
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        ml_model = RandomForestClassifier(n_estimators=100, random_state=42)
        ml_model.fit(X_scaled, y)
        
        is_model_trained = True
        logger.info("ML model trained successfully")
        
    except Exception as e:
        logger.error(f"Error training ML model: {e}")

def predict_deterioration(wearable_data: WearableData) -> PredictionResult:
    """Predict patient deterioration risk based on wearable data"""
    global ml_model, scaler, is_model_trained
    
    if not is_model_trained:
        train_ml_model()
    
    try:
        # Prepare features
        features = np.array([[
            wearable_data.heart_rate,
            wearable_data.blood_pressure_systolic,
            wearable_data.blood_pressure_diastolic,
            wearable_data.temperature,
            wearable_data.oxygen_saturation,
            wearable_data.activity_level
        ]])
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Predict
        risk_prob = ml_model.predict_proba(features_scaled)[0][1]
        
        # Determine risk level
        if risk_prob < 0.3:
            risk_level = "Low"
        elif risk_prob < 0.7:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        # Identify contributing factors
        contributing_factors = []
        if wearable_data.heart_rate > 100:
            contributing_factors.append("Elevated heart rate")
        if wearable_data.blood_pressure_systolic > 140:
            contributing_factors.append("High systolic blood pressure")
        if wearable_data.temperature > 100.4:
            contributing_factors.append("Fever")
        if wearable_data.oxygen_saturation < 95:
            contributing_factors.append("Low oxygen saturation")
        if wearable_data.activity_level < 2:
            contributing_factors.append("Low activity level")
        
        return PredictionResult(
            patient_id=wearable_data.patient_id,
            timestamp=wearable_data.timestamp,
            deterioration_risk=float(risk_prob),
            risk_level=risk_level,
            contributing_factors=contributing_factors
        )
        
    except Exception as e:
        logger.error(f"Error predicting deterioration: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    init_database()
    train_ml_model()
    logger.info("Application started successfully")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Digital Twin MedTech MVP API",
        "version": "1.0.0",
        "description": "Real-time wearable device data collection and patient deterioration prediction",
        "endpoints": {
            "/patients": "Patient management",
            "/wearable-data": "Wearable device data collection",
            "/predictions": "Patient deterioration predictions",
            "/dashboard-data": "Power BI dashboard data",
            "/health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": dt.now(),
        "model_trained": is_model_trained,
        "database": "connected"
    }

# Patient endpoints
@app.post("/patients")
async def create_patient(patient: PatientRecord):
    """Create a new patient record"""
    try:
        conn = sqlite3.connect('digital_twin.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO patients (patient_id, name, age, gender, medical_conditions)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            patient.patient_id,
            patient.name,
            patient.age,
            patient.gender,
            json.dumps(patient.medical_conditions)
        ))
        
        conn.commit()
        conn.close()
        
        return {"message": "Patient created successfully", "patient_id": patient.patient_id}
        
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Patient already exists")
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(status_code=500, detail="Failed to create patient")

@app.get("/patients")
async def get_patients():
    """Get all patients"""
    try:
        conn = sqlite3.connect('digital_twin.db')
        df = pd.read_sql_query("SELECT * FROM patients", conn)
        conn.close()
        
        patients = []
        for _, row in df.iterrows():
            patients.append({
                "patient_id": row['patient_id'],
                "name": row['name'],
                "age": row['age'],
                "gender": row['gender'],
                "medical_conditions": json.loads(row['medical_conditions'])
            })
        
        return patients
        
    except Exception as e:
        logger.error(f"Error fetching patients: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch patients")

# Wearable data endpoints
@app.post("/wearable-data")
async def collect_wearable_data(data: WearableData, background_tasks: BackgroundTasks):
    """Collect wearable device data and trigger prediction"""
    try:
        # Store wearable data
        conn = sqlite3.connect('digital_twin.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO wearable_data 
            (patient_id, timestamp, heart_rate, blood_pressure_systolic, 
             blood_pressure_diastolic, temperature, oxygen_saturation, activity_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.patient_id,
            data.timestamp,
            data.heart_rate,
            data.blood_pressure_systolic,
            data.blood_pressure_diastolic,
            data.temperature,
            data.oxygen_saturation,
            data.activity_level
        ))
        
        conn.commit()
        conn.close()
        
        # Generate prediction in background
        background_tasks.add_task(generate_and_store_prediction, data)
        
        return {"message": "Data collected successfully", "patient_id": data.patient_id}
        
    except Exception as e:
        logger.error(f"Error collecting wearable data: {e}")
        raise HTTPException(status_code=500, detail="Failed to collect data")

async def generate_and_store_prediction(data: WearableData):
    """Generate and store prediction"""
    try:
        prediction = predict_deterioration(data)
        
        # Store prediction
        conn = sqlite3.connect('digital_twin.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions 
            (patient_id, timestamp, deterioration_risk, risk_level, contributing_factors)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            prediction.patient_id,
            prediction.timestamp,
            prediction.deterioration_risk,
            prediction.risk_level,
            json.dumps(prediction.contributing_factors)
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Prediction stored for patient {prediction.patient_id}: {prediction.risk_level}")
        
    except Exception as e:
        logger.error(f"Error storing prediction: {e}")

@app.get("/wearable-data/{patient_id}")
async def get_wearable_data(patient_id: str, limit: int = 100):
    """Get wearable data for a specific patient"""
    try:
        conn = sqlite3.connect('digital_twin.db')
        query = '''
            SELECT * FROM wearable_data 
            WHERE patient_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        '''
        df = pd.read_sql_query(query, conn, params=(patient_id, limit))
        conn.close()
        
        return df.to_dict('records')
        
    except Exception as e:
        logger.error(f"Error fetching wearable data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch wearable data")

# Prediction endpoints
@app.get("/predictions/{patient_id}")
async def get_predictions(patient_id: str, limit: int = 50):
    """Get predictions for a specific patient"""
    try:
        conn = sqlite3.connect('digital_twin.db')
        query = '''
            SELECT * FROM predictions 
            WHERE patient_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        '''
        df = pd.read_sql_query(query, conn, params=(patient_id, limit))
        conn.close()
        
        predictions = []
        for _, row in df.iterrows():
            predictions.append({
                "patient_id": row['patient_id'],
                "timestamp": row['timestamp'],
                "deterioration_risk": row['deterioration_risk'],
                "risk_level": row['risk_level'],
                "contributing_factors": json.loads(row['contributing_factors']),
                "actual_outcome": row['actual_outcome']
            })
        
        return predictions
        
    except Exception as e:
        logger.error(f"Error fetching predictions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch predictions")

@app.put("/predictions/{prediction_id}/outcome")
async def update_actual_outcome(prediction_id: int, outcome: int):
    """Update actual outcome for prediction (0 = no deterioration, 1 = deterioration)"""
    try:
        conn = sqlite3.connect('digital_twin.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE predictions 
            SET actual_outcome = ? 
            WHERE id = ?
        ''', (outcome, prediction_id))
        
        conn.commit()
        conn.close()
        
        return {"message": "Actual outcome updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating actual outcome: {e}")
        raise HTTPException(status_code=500, detail="Failed to update outcome")

# Dashboard data endpoints for Power BI
@app.get("/dashboard-data/overview")
async def get_dashboard_overview():
    """Get overview data for Power BI dashboard"""
    try:
        conn = sqlite3.connect('digital_twin.db')
        
        # Get basic statistics
        total_patients = pd.read_sql_query("SELECT COUNT(DISTINCT patient_id) as count FROM patients", conn).iloc[0]['count']
        total_data_points = pd.read_sql_query("SELECT COUNT(*) as count FROM wearable_data", conn).iloc[0]['count']
        total_predictions = pd.read_sql_query("SELECT COUNT(*) as count FROM predictions", conn).iloc[0]['count']
        
        # Risk distribution
        risk_distribution = pd.read_sql_query('''
            SELECT risk_level, COUNT(*) as count 
            FROM predictions 
            GROUP BY risk_level
        ''', conn).to_dict('records')
        
        conn.close()
        
        return {
            "total_patients": total_patients,
            "total_data_points": total_data_points,
            "total_predictions": total_predictions,
            "risk_distribution": risk_distribution,
            "last_updated": dt.now()
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")

@app.get("/dashboard-data/predictions-vs-actual")
async def get_predictions_vs_actual():
    """Get predictions vs actual outcomes for comparison analysis"""
    try:
        conn = sqlite3.connect('digital_twin.db')
        
        query = '''
            SELECT 
                patient_id,
                timestamp,
                deterioration_risk,
                risk_level,
                actual_outcome,
                CASE 
                    WHEN actual_outcome IS NOT NULL THEN 
                        CASE 
                            WHEN (deterioration_risk > 0.5 AND actual_outcome = 1) OR 
                                 (deterioration_risk <= 0.5 AND actual_outcome = 0) 
                            THEN 'Correct'
                            ELSE 'Incorrect'
                        END
                    ELSE 'Pending'
                END as prediction_accuracy
            FROM predictions
            WHERE actual_outcome IS NOT NULL
            ORDER BY timestamp DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Calculate accuracy metrics
        if len(df) > 0:
            accuracy = len(df[df['prediction_accuracy'] == 'Correct']) / len(df) * 100
            
            # Confusion matrix data
            true_positives = len(df[(df['deterioration_risk'] > 0.5) & (df['actual_outcome'] == 1)])
            false_positives = len(df[(df['deterioration_risk'] > 0.5) & (df['actual_outcome'] == 0)])
            true_negatives = len(df[(df['deterioration_risk'] <= 0.5) & (df['actual_outcome'] == 0)])
            false_negatives = len(df[(df['deterioration_risk'] <= 0.5) & (df['actual_outcome'] == 1)])
        else:
            accuracy = 0
            true_positives = false_positives = true_negatives = false_negatives = 0
        
        return {
            "predictions": df.to_dict('records'),
            "accuracy": accuracy,
            "confusion_matrix": {
                "true_positives": true_positives,
                "false_positives": false_positives,
                "true_negatives": true_negatives,
                "false_negatives": false_negatives
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching predictions vs actual: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch comparison data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)