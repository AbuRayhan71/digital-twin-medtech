"""
Wearable Device Data Simulator
Simulates real-time data collection from multiple patients with various health conditions
"""

import requests
import json
import time
import random
import numpy as np
from datetime import datetime, timedelta
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WearableDataSimulator:
    def __init__(self, base_url="http://localhost:8000", num_patients=5):
        self.base_url = base_url
        self.num_patients = num_patients
        self.patients = []
        self.running = False
        
    def create_sample_patients(self):
        """Create sample patients with different risk profiles"""
        sample_patients = [
            {
                "patient_id": "PAT001",
                "name": "John Smith",
                "age": 65,
                "gender": "male",
                "medical_conditions": ["hypertension", "diabetes"],
                "risk_profile": "high"
            },
            {
                "patient_id": "PAT002", 
                "name": "Sarah Johnson",
                "age": 34,
                "gender": "female",
                "medical_conditions": ["asthma"],
                "risk_profile": "low"
            },
            {
                "patient_id": "PAT003",
                "name": "Michael Brown",
                "age": 78,
                "gender": "male", 
                "medical_conditions": ["heart_disease", "hypertension", "diabetes"],
                "risk_profile": "high"
            },
            {
                "patient_id": "PAT004",
                "name": "Emily Davis",
                "age": 42,
                "gender": "female",
                "medical_conditions": [],
                "risk_profile": "low"
            },
            {
                "patient_id": "PAT005",
                "name": "Robert Wilson",
                "age": 58,
                "gender": "male",
                "medical_conditions": ["hypertension"],
                "risk_profile": "medium"
            }
        ]
        
        # Register patients
        for patient in sample_patients:
            try:
                response = requests.post(f"{self.base_url}/patients", json={
                    "patient_id": patient["patient_id"],
                    "name": patient["name"],
                    "age": patient["age"],
                    "gender": patient["gender"],
                    "medical_conditions": patient["medical_conditions"]
                })
                
                if response.status_code == 200:
                    logger.info(f"Created patient: {patient['name']}")
                    self.patients.append(patient)
                else:
                    logger.warning(f"Patient {patient['name']} might already exist")
                    self.patients.append(patient)
                    
            except Exception as e:
                logger.error(f"Error creating patient {patient['name']}: {e}")
    
    def generate_wearable_data(self, patient):
        """Generate realistic wearable data based on patient risk profile"""
        risk_profile = patient["risk_profile"]
        age = patient["age"]
        conditions = patient["medical_conditions"]
        
        # Base vital signs
        if risk_profile == "high":
            heart_rate = np.random.normal(95, 25)  # Higher average, more variation
            bp_systolic = np.random.normal(140, 20)
            bp_diastolic = np.random.normal(90, 15)
            temperature = np.random.normal(98.8, 1.2)
            oxygen_sat = np.random.normal(96, 3)
            activity = np.random.normal(3, 2)
        elif risk_profile == "medium":
            heart_rate = np.random.normal(80, 15)
            bp_systolic = np.random.normal(125, 15)
            bp_diastolic = np.random.normal(80, 10)
            temperature = np.random.normal(98.6, 0.8)
            oxygen_sat = np.random.normal(97, 2)
            activity = np.random.normal(5, 2)
        else:  # low risk
            heart_rate = np.random.normal(72, 12)
            bp_systolic = np.random.normal(115, 10)
            bp_diastolic = np.random.normal(75, 8)
            temperature = np.random.normal(98.6, 0.5)
            oxygen_sat = np.random.normal(98, 1)
            activity = np.random.normal(6, 2)
        
        # Apply age adjustments
        if age > 70:
            heart_rate += np.random.normal(5, 5)
            bp_systolic += np.random.normal(10, 5)
            activity = max(0, activity - np.random.normal(2, 1))
        
        # Apply condition-specific adjustments
        if "hypertension" in conditions:
            bp_systolic += np.random.normal(15, 10)
            bp_diastolic += np.random.normal(8, 5)
            
        if "diabetes" in conditions:
            # Simulate occasional stress responses
            if random.random() < 0.1:
                heart_rate += np.random.normal(20, 10)
                
        if "heart_disease" in conditions:
            heart_rate += np.random.normal(10, 15)
            if random.random() < 0.05:  # Occasional events
                heart_rate += np.random.normal(30, 15)
                oxygen_sat -= np.random.normal(5, 3)
        
        # Ensure realistic ranges
        heart_rate = np.clip(heart_rate, 40, 180)
        bp_systolic = np.clip(bp_systolic, 80, 200)
        bp_diastolic = np.clip(bp_diastolic, 40, 120)
        temperature = np.clip(temperature, 95, 105)
        oxygen_sat = np.clip(oxygen_sat, 85, 100)
        activity = np.clip(activity, 0, 10)
        
        return {
            "patient_id": patient["patient_id"],
            "timestamp": datetime.now().isoformat(),
            "heart_rate": round(heart_rate, 1),
            "blood_pressure_systolic": round(bp_systolic, 1),
            "blood_pressure_diastolic": round(bp_diastolic, 1),
            "temperature": round(temperature, 1),
            "oxygen_saturation": round(oxygen_sat, 1),
            "activity_level": round(activity, 1)
        }
    
    def send_wearable_data(self, patient):
        """Send wearable data to the API"""
        data = self.generate_wearable_data(patient)
        
        try:
            response = requests.post(f"{self.base_url}/wearable-data", json=data)
            if response.status_code == 200:
                logger.info(f"Data sent for {patient['name']}: HR={data['heart_rate']}, Risk={patient['risk_profile']}")
            else:
                logger.error(f"Failed to send data for {patient['name']}: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error sending data for {patient['name']}: {e}")
    
    def simulate_patient_data(self, patient):
        """Simulate continuous data collection for a patient"""
        while self.running:
            self.send_wearable_data(patient)
            # Send data every 30-60 seconds with some randomness
            time.sleep(random.uniform(30, 60))
    
    def start_simulation(self):
        """Start the simulation for all patients"""
        logger.info("Starting wearable data simulation...")
        self.create_sample_patients()
        
        self.running = True
        threads = []
        
        for patient in self.patients:
            thread = threading.Thread(target=self.simulate_patient_data, args=(patient,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            
        logger.info(f"Started simulation for {len(self.patients)} patients")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping simulation...")
            self.running = False
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False

def run_demo_scenario():
    """Run a demo scenario with specific events"""
    simulator = WearableDataSimulator()
    simulator.create_sample_patients()
    
    logger.info("Running demo scenario...")
    
    # Simulate normal readings
    for _ in range(5):
        for patient in simulator.patients:
            simulator.send_wearable_data(patient)
        time.sleep(10)
    
    # Simulate a high-risk event for PAT003
    high_risk_patient = next(p for p in simulator.patients if p["patient_id"] == "PAT003")
    
    logger.info("Simulating high-risk event for PAT003...")
    
    # Override risk profile temporarily
    original_risk = high_risk_patient["risk_profile"]
    high_risk_patient["risk_profile"] = "high"
    
    # Send elevated readings
    for _ in range(3):
        data = simulator.generate_wearable_data(high_risk_patient)
        # Force high-risk readings
        data["heart_rate"] = 135
        data["blood_pressure_systolic"] = 165
        data["temperature"] = 101.2
        data["oxygen_saturation"] = 92
        data["activity_level"] = 1
        
        try:
            response = requests.post(f"{simulator.base_url}/wearable-data", json=data)
            logger.info(f"High-risk data sent: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending high-risk data: {e}")
            
        time.sleep(5)
    
    # Restore original risk profile
    high_risk_patient["risk_profile"] = original_risk
    
    logger.info("Demo scenario completed")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_demo_scenario()
    else:
        simulator = WearableDataSimulator()
        try:
            simulator.start_simulation()
        except KeyboardInterrupt:
            logger.info("Simulation stopped by user")