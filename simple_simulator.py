"""
Simple Data Simulator for Digital Twin MVP
Uses only standard library - no external dependencies
"""

import json
import time
import random
from datetime import datetime
from http.client import HTTPConnection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleDataSimulator:
    def __init__(self, host="localhost", port=8000):
        self.host = host
        self.port = port
        self.patients = [
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
                "medical_conditions": ["heart_disease", "hypertension"],
                "risk_profile": "high"
            }
        ]
        
    def send_request(self, method, path, data=None):
        """Send HTTP request to API"""
        try:
            conn = HTTPConnection(self.host, self.port, timeout=10)
            
            headers = {'Content-Type': 'application/json'}
            body = json.dumps(data) if data else None
            
            conn.request(method, path, body, headers)
            response = conn.getresponse()
            
            result = {
                'status': response.status,
                'data': response.read().decode()
            }
            
            conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None
    
    def generate_vitals(self, patient):
        """Generate realistic vital signs based on patient profile"""
        risk_profile = patient["risk_profile"]
        age = patient["age"]
        conditions = patient["medical_conditions"]
        
        # Base vital signs
        if risk_profile == "high":
            heart_rate = random.uniform(85, 120)
            bp_systolic = random.uniform(130, 160)
            bp_diastolic = random.uniform(85, 100)
            temperature = random.uniform(98.2, 100.5)
            oxygen_sat = random.uniform(94, 98)
            activity = random.uniform(1, 4)
        elif risk_profile == "medium":
            heart_rate = random.uniform(70, 95)
            bp_systolic = random.uniform(110, 140)
            bp_diastolic = random.uniform(70, 90)
            temperature = random.uniform(97.8, 99.2)
            oxygen_sat = random.uniform(96, 99)
            activity = random.uniform(3, 6)
        else:  # low risk
            heart_rate = random.uniform(60, 85)
            bp_systolic = random.uniform(100, 130)
            bp_diastolic = random.uniform(60, 85)
            temperature = random.uniform(97.5, 98.8)
            oxygen_sat = random.uniform(97, 100)
            activity = random.uniform(4, 8)
        
        # Age adjustments
        if age > 70:
            heart_rate += random.uniform(0, 10)
            bp_systolic += random.uniform(5, 20)
            activity = max(1, activity - random.uniform(1, 3))
        
        # Condition adjustments
        if "hypertension" in conditions:
            bp_systolic += random.uniform(10, 25)
            bp_diastolic += random.uniform(5, 15)
            
        if "diabetes" in conditions:
            if random.random() < 0.1:  # Occasional spikes
                heart_rate += random.uniform(15, 25)
                
        if "heart_disease" in conditions:
            heart_rate += random.uniform(5, 20)
            if random.random() < 0.05:  # Occasional events
                oxygen_sat -= random.uniform(3, 8)
        
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
    
    def test_connection(self):
        """Test connection to API"""
        logger.info("Testing connection to API...")
        response = self.send_request("GET", "/health")
        
        if response and response['status'] == 200:
            logger.info("✓ Connected to API successfully")
            return True
        else:
            logger.error("✗ Failed to connect to API")
            return False
    
    def create_patients(self):
        """Create sample patients"""
        logger.info("Creating sample patients...")
        
        for patient in self.patients:
            patient_data = {
                "patient_id": patient["patient_id"],
                "name": patient["name"],
                "age": patient["age"],
                "gender": patient["gender"],
                "medical_conditions": patient["medical_conditions"]
            }
            
            response = self.send_request("POST", "/patients", patient_data)
            
            if response and response['status'] in [200, 400]:  # 400 might mean already exists
                logger.info(f"✓ Patient {patient['name']} processed")
            else:
                logger.error(f"✗ Failed to create patient {patient['name']}")
    
    def simulate_data_collection(self, cycles=10):
        """Simulate data collection for multiple cycles"""
        logger.info(f"Starting data simulation for {cycles} cycles...")
        
        for cycle in range(cycles):
            logger.info(f"\nCycle {cycle + 1}/{cycles}")
            
            for patient in self.patients:
                vitals = self.generate_vitals(patient)
                
                response = self.send_request("POST", "/wearable-data", vitals)
                
                if response and response['status'] == 200:
                    try:
                        result = json.loads(response['data'])
                        risk_info = result.get('risk_prediction', {})
                        logger.info(f"✓ {patient['name']}: HR={vitals['heart_rate']}, "
                                  f"Risk={risk_info.get('risk_level', 'Unknown')}")
                    except:
                        logger.info(f"✓ Data sent for {patient['name']}")
                else:
                    logger.error(f"✗ Failed to send data for {patient['name']}")
                
                time.sleep(1)  # Brief pause between patients
            
            if cycle < cycles - 1:
                logger.info("Waiting 30 seconds before next cycle...")
                time.sleep(30)
    
    def simulate_high_risk_event(self):
        """Simulate a high-risk medical event"""
        logger.info("\n🚨 Simulating high-risk medical event for PAT003...")
        
        high_risk_patient = next(p for p in self.patients if p["patient_id"] == "PAT003")
        
        # Generate critical vitals
        critical_vitals = {
            "patient_id": "PAT003",
            "timestamp": datetime.now().isoformat(),
            "heart_rate": 140.0,
            "blood_pressure_systolic": 175.0,
            "blood_pressure_diastolic": 95.0,
            "temperature": 101.8,
            "oxygen_saturation": 88.0,
            "activity_level": 0.5
        }
        
        response = self.send_request("POST", "/wearable-data", critical_vitals)
        
        if response and response['status'] == 200:
            try:
                result = json.loads(response['data'])
                risk_info = result.get('risk_prediction', {})
                logger.info(f"🚨 Critical event detected! Risk Level: {risk_info.get('risk_level', 'Unknown')}")
                logger.info(f"   Risk Score: {risk_info.get('risk_score', 'Unknown')}")
            except:
                logger.info("🚨 Critical event data sent")
        else:
            logger.error("✗ Failed to send critical event data")
    
    def get_dashboard_summary(self):
        """Get and display dashboard summary"""
        logger.info("\n📊 Dashboard Summary:")
        
        response = self.send_request("GET", "/dashboard-data/overview")
        
        if response and response['status'] == 200:
            try:
                data = json.loads(response['data'])
                logger.info(f"  Total Patients: {data.get('total_patients', 0)}")
                logger.info(f"  Total Data Points: {data.get('total_data_points', 0)}")
                logger.info(f"  Total Predictions: {data.get('total_predictions', 0)}")
                
                risk_dist = data.get('risk_distribution', [])
                if risk_dist:
                    logger.info("  Risk Distribution:")
                    for risk in risk_dist:
                        logger.info(f"    {risk.get('risk_level', 'Unknown')}: {risk.get('count', 0)}")
                        
            except Exception as e:
                logger.error(f"Error parsing dashboard data: {e}")
        else:
            logger.error("✗ Failed to get dashboard data")
    
    def run_demo(self):
        """Run complete demo scenario"""
        logger.info("🏥 Starting Digital Twin MedTech MVP Demo")
        
        if not self.test_connection():
            logger.error("Cannot connect to API. Make sure the server is running.")
            return False
        
        self.create_patients()
        time.sleep(2)
        
        self.simulate_data_collection(cycles=3)
        
        self.simulate_high_risk_event()
        time.sleep(2)
        
        self.get_dashboard_summary()
        
        logger.info("\n🎉 Demo completed successfully!")
        logger.info("💡 You can now:")
        logger.info("  - View API at http://localhost:8000")
        logger.info("  - Check health at http://localhost:8000/health")
        logger.info("  - View patients at http://localhost:8000/patients") 
        logger.info("  - View dashboard data at http://localhost:8000/dashboard-data/overview")
        
        return True

def main():
    """Main function"""
    import sys
    
    simulator = SimpleDataSimulator()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            simulator.run_demo()
        elif sys.argv[1] == "continuous":
            if simulator.test_connection():
                simulator.create_patients()
                logger.info("Starting continuous simulation...")
                logger.info("Press Ctrl+C to stop")
                try:
                    while True:
                        simulator.simulate_data_collection(cycles=1)
                        time.sleep(60)  # Wait 1 minute between cycles
                except KeyboardInterrupt:
                    logger.info("\nSimulation stopped by user")
        else:
            print("Usage: python simple_simulator.py [demo|continuous]")
    else:
        # Default: run demo
        simulator.run_demo()

if __name__ == "__main__":
    main()