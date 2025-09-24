"""
Digital Twin MedTech MVP - Simplified Version
Lightweight implementation using standard library only
"""

import sqlite3
import json
import random
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DigitalTwinHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            query = urllib.parse.parse_qs(parsed_path.query)
            
            if path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "message": "Digital Twin MedTech MVP API",
                    "version": "1.0.0",
                    "status": "running",
                    "endpoints": ["/health", "/patients", "/dashboard-data/overview"]
                }
                self.wfile.write(json.dumps(response, indent=2).encode())
                
            elif path == '/health':
                self.send_health_check()
                
            elif path == '/patients':
                self.get_patients()
                
            elif path == '/dashboard-data/overview':
                self.get_dashboard_overview()
                
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'{"error": "Endpoint not found"}')
                
        except Exception as e:
            logger.error(f"GET error: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f'{{"error": "{str(e)}"}}'.encode())
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            path = self.path
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            if path == '/patients':
                self.create_patient(data)
            elif path == '/wearable-data':
                self.collect_wearable_data(data)
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'{"error": "Endpoint not found"}')
                
        except Exception as e:
            logger.error(f"POST error: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f'{{"error": "{str(e)}"}}'.encode())
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_health_check(self):
        """Send health check response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
        self.wfile.write(json.dumps(response).encode())
    
    def get_patients(self):
        """Get all patients"""
        try:
            conn = sqlite3.connect('digital_twin.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients")
            rows = cursor.fetchall()
            
            patients = []
            for row in rows:
                patients.append({
                    "patient_id": row[1],
                    "name": row[2],
                    "age": row[3],
                    "gender": row[4],
                    "medical_conditions": json.loads(row[5] or '[]')
                })
            
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(patients, indent=2).encode())
            
        except Exception as e:
            logger.error(f"Error getting patients: {e}")
            self.send_response(500)
            self.end_headers()
    
    def create_patient(self, data):
        """Create a new patient"""
        try:
            conn = sqlite3.connect('digital_twin.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO patients (patient_id, name, age, gender, medical_conditions)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data['patient_id'],
                data['name'],
                data['age'],
                data['gender'],
                json.dumps(data.get('medical_conditions', []))
            ))
            
            conn.commit()
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"message": "Patient created successfully", "patient_id": data['patient_id']}
            self.wfile.write(json.dumps(response).encode())
            
        except sqlite3.IntegrityError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error": "Patient already exists"}')
        except Exception as e:
            logger.error(f"Error creating patient: {e}")
            self.send_response(500)
            self.end_headers()
    
    def collect_wearable_data(self, data):
        """Collect wearable device data"""
        try:
            conn = sqlite3.connect('digital_twin.db')
            cursor = conn.cursor()
            
            # Store wearable data
            cursor.execute('''
                INSERT INTO wearable_data 
                (patient_id, timestamp, heart_rate, blood_pressure_systolic, 
                 blood_pressure_diastolic, temperature, oxygen_saturation, activity_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['patient_id'],
                data['timestamp'],
                data['heart_rate'],
                data['blood_pressure_systolic'],
                data['blood_pressure_diastolic'],
                data['temperature'],
                data['oxygen_saturation'],
                data['activity_level']
            ))
            
            # Generate simple risk prediction
            risk_score = self.calculate_simple_risk(data)
            risk_level = "Low" if risk_score < 0.3 else "Medium" if risk_score < 0.7 else "High"
            
            # Store prediction
            cursor.execute('''
                INSERT INTO predictions 
                (patient_id, timestamp, deterioration_risk, risk_level, contributing_factors)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data['patient_id'],
                data['timestamp'],
                risk_score,
                risk_level,
                json.dumps(self.get_risk_factors(data))
            ))
            
            conn.commit()
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "message": "Data collected successfully", 
                "patient_id": data['patient_id'],
                "risk_prediction": {
                    "risk_score": risk_score,
                    "risk_level": risk_level
                }
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            logger.error(f"Error collecting wearable data: {e}")
            self.send_response(500)
            self.end_headers()
    
    def calculate_simple_risk(self, data):
        """Calculate simple risk score based on vital signs"""
        risk = 0.0
        
        # Heart rate risk
        if data['heart_rate'] > 100 or data['heart_rate'] < 60:
            risk += 0.2
        
        # Blood pressure risk
        if data['blood_pressure_systolic'] > 140 or data['blood_pressure_systolic'] < 90:
            risk += 0.25
        
        # Temperature risk
        if data['temperature'] > 100.4 or data['temperature'] < 96.8:
            risk += 0.2
        
        # Oxygen saturation risk
        if data['oxygen_saturation'] < 95:
            risk += 0.3
        
        # Activity level risk
        if data['activity_level'] < 2:
            risk += 0.15
        
        return min(risk, 1.0)
    
    def get_risk_factors(self, data):
        """Get contributing risk factors"""
        factors = []
        
        if data['heart_rate'] > 100:
            factors.append("Elevated heart rate")
        elif data['heart_rate'] < 60:
            factors.append("Low heart rate")
            
        if data['blood_pressure_systolic'] > 140:
            factors.append("High blood pressure")
        elif data['blood_pressure_systolic'] < 90:
            factors.append("Low blood pressure")
            
        if data['temperature'] > 100.4:
            factors.append("Fever")
        elif data['temperature'] < 96.8:
            factors.append("Low body temperature")
            
        if data['oxygen_saturation'] < 95:
            factors.append("Low oxygen saturation")
            
        if data['activity_level'] < 2:
            factors.append("Low activity level")
        
        return factors
    
    def get_dashboard_overview(self):
        """Get dashboard overview data"""
        try:
            conn = sqlite3.connect('digital_twin.db')
            cursor = conn.cursor()
            
            # Get counts
            cursor.execute("SELECT COUNT(DISTINCT patient_id) FROM patients")
            total_patients = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM wearable_data")
            total_data_points = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM predictions")
            total_predictions = cursor.fetchone()[0]
            
            # Risk distribution
            cursor.execute("SELECT risk_level, COUNT(*) FROM predictions GROUP BY risk_level")
            risk_dist = [{"risk_level": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            conn.close()
            
            response = {
                "total_patients": total_patients,
                "total_data_points": total_data_points,
                "total_predictions": total_predictions,
                "risk_distribution": risk_dist,
                "last_updated": datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            logger.error(f"Error getting dashboard overview: {e}")
            self.send_response(500)
            self.end_headers()

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect('digital_twin.db')
    cursor = conn.cursor()
    
    # Patients table
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

def create_sample_data():
    """Create sample patients and data"""
    conn = sqlite3.connect('digital_twin.db')
    cursor = conn.cursor()
    
    # Check if patients already exist
    cursor.execute("SELECT COUNT(*) FROM patients")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    sample_patients = [
        ("PAT001", "John Smith", 65, "male", ["hypertension", "diabetes"]),
        ("PAT002", "Sarah Johnson", 34, "female", ["asthma"]),
        ("PAT003", "Michael Brown", 78, "male", ["heart_disease", "hypertension"]),
        ("PAT004", "Emily Davis", 42, "female", []),
        ("PAT005", "Robert Wilson", 58, "male", ["hypertension"])
    ]
    
    for patient in sample_patients:
        cursor.execute('''
            INSERT INTO patients (patient_id, name, age, gender, medical_conditions)
            VALUES (?, ?, ?, ?, ?)
        ''', (*patient[:4], json.dumps(patient[4])))
        
        # Generate sample wearable data
        for i in range(5):
            timestamp = (datetime.now() - timedelta(hours=i)).isoformat()
            
            # Generate realistic vitals based on age and conditions
            base_hr = 70 + random.randint(-10, 20)
            base_systolic = 120 + random.randint(-20, 30)
            base_diastolic = 80 + random.randint(-10, 15)
            
            if "hypertension" in patient[4]:
                base_systolic += random.randint(10, 30)
                base_diastolic += random.randint(5, 15)
            
            if patient[2] > 65:  # elderly
                base_hr += random.randint(0, 15)
                base_systolic += random.randint(5, 20)
            
            wearable_data = (
                patient[0],  # patient_id
                timestamp,
                base_hr,
                base_systolic,
                base_diastolic,
                98.6 + random.uniform(-1, 2),  # temperature
                97 + random.uniform(-3, 2),    # oxygen_saturation
                random.uniform(2, 8)           # activity_level
            )
            
            cursor.execute('''
                INSERT INTO wearable_data 
                (patient_id, timestamp, heart_rate, blood_pressure_systolic, 
                 blood_pressure_diastolic, temperature, oxygen_saturation, activity_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', wearable_data)
    
    conn.commit()
    conn.close()
    logger.info("Sample data created")

def run_server():
    """Run the HTTP server"""
    try:
        init_database()
        create_sample_data()
        
        server = HTTPServer(('localhost', 8000), DigitalTwinHandler)
        logger.info("🚀 Digital Twin MedTech MVP server starting on http://localhost:8000")
        logger.info("📖 Available endpoints:")
        logger.info("  GET  /           - API information")
        logger.info("  GET  /health     - Health check")
        logger.info("  GET  /patients   - List patients")
        logger.info("  POST /patients   - Create patient")
        logger.info("  POST /wearable-data - Submit wearable data")
        logger.info("  GET  /dashboard-data/overview - Dashboard overview")
        logger.info("\n🛑 Press Ctrl+C to stop the server")
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    run_server()