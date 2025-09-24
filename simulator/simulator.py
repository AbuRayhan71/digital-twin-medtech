import asyncio
import httpx
import uuid
import random
import datetime
import json
import time

# Configuration
INGEST_ENDPOINT = "http://localhost:8000/ingest"  # Will create this API next
NUM_PATIENTS = 5  # Start with 5 patients
SEND_INTERVAL_MIN = 1.0  # Minimum seconds between sends
SEND_INTERVAL_MAX = 3.0  # Maximum seconds between sends

class PatientSimulator:
    def __init__(self, patient_id, device_id, name):
        self.patient_id = patient_id
        self.device_id = device_id
        self.name = name
        
        # Baseline vitals for this patient (each patient is different)
        self.baseline_hr = random.randint(60, 80)
        self.baseline_spo2 = random.uniform(95, 99)
        self.baseline_temp = random.uniform(36.1, 37.2)
        self.baseline_systolic = random.randint(110, 130)
        self.baseline_diastolic = random.randint(70, 85)
    
    def generate_vitals(self):
        """Generate realistic vital signs with some variation"""
        return {
            "event_id": str(uuid.uuid4()),
            "patient_id": self.patient_id,
            "device_id": self.device_id,
            "recorded_at": datetime.datetime.utcnow().isoformat(),
            "heart_rate": max(40, min(200, self.baseline_hr + random.randint(-15, 25))),
            "spo2": round(max(85, min(100, self.baseline_spo2 + random.uniform(-3, 2))), 1),
            "systolic": max(80, min(200, self.baseline_systolic + random.randint(-20, 30))),
            "diastolic": max(50, min(120, self.baseline_diastolic + random.randint(-15, 20))),
            "temperature": round(max(35.0, min(42.0, self.baseline_temp + random.uniform(-1.0, 2.0))), 1),
            "respiratory_rate": random.randint(12, 20)
        }

async def send_patient_data(session, patient_sim):
    """Send one patient's data continuously"""
    while True:
        try:
            vitals = patient_sim.generate_vitals()
            
            # Try to send to ingest API (will fail until we build it)
            try:
                response = await session.post(INGEST_ENDPOINT, json=vitals)
                if response.status_code == 200:
                    print(f"✅ {patient_sim.name}: HR={vitals['heart_rate']} SpO2={vitals['spo2']}% BP={vitals['systolic']}/{vitals['diastolic']}")
                else:
                    print(f"❌ {patient_sim.name}: API returned {response.status_code}")
            except Exception as e:
                print(f"📡 {patient_sim.name}: Waiting for ingest API... HR={vitals['heart_rate']}")
            
            # Wait before next reading
            await asyncio.sleep(random.uniform(SEND_INTERVAL_MIN, SEND_INTERVAL_MAX))
            
        except Exception as e:
            print(f"❌ Error with {patient_sim.name}: {e}")
            await asyncio.sleep(5)

async def main():
    """Start simulation for multiple patients"""
    
    # Create patient simulators
    patients = []
    patient_names = ["John Doe", "Jane Smith", "Mike Johnson", "Sarah Wilson", "Tom Brown"]
    
    for i, name in enumerate(patient_names[:NUM_PATIENTS]):
        patient_sim = PatientSimulator(
            patient_id=f"patient-{i+1:03d}",
            device_id=f"device-{i+1:03d}",
            name=name
        )
        patients.append(patient_sim)
    
    print(f"🚀 Starting Digital Twin Simulator for {NUM_PATIENTS} patients...")
    print(f"📡 Sending data to: {INGEST_ENDPOINT}")
    print("=" * 70)
    
    # Start all patient data streams concurrently
    async with httpx.AsyncClient(timeout=5.0) as session:
        tasks = [
            asyncio.create_task(send_patient_data(session, patient))
            for patient in patients
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\n🛑 Simulator stopped by user")
        except Exception as e:
            print(f"❌ Simulator error: {e}")

if __name__ == "__main__":
    asyncio.run(main())