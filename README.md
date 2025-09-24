# Digital Twin MedTech MVP

A comprehensive digital twin system that collects and analyzes data from wearable devices in real-time, predicts patient deterioration risk, and provides visualization through Power BI dashboards.

## 🎯 Features

- **Real-time Data Collection**: Simulates wearable device data collection from multiple patients
- **Predictive Analytics**: Machine learning model for patient deterioration risk assessment  
- **Risk Stratification**: Categorizes patients into Low, Medium, and High risk levels
- **Data Storage**: Persistent storage of patient records, wearable data, and predictions
- **Power BI Integration**: Ready-to-use dashboard configuration for visualization
- **Comparison Analytics**: Tracks prediction accuracy vs actual patient outcomes
- **REST API**: Comprehensive API for data access and integration

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Wearable       │    │   Digital Twin   │    │   Power BI      │
│  Devices        │───▶│   API Server     │───▶│   Dashboard     │
│  (Simulated)    │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   SQLite         │
                       │   Database       │
                       └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd digital-twin-medtech
   ```

2. **Run the automated setup**:
   ```bash
   ./start_system.sh
   ```

This script will:
- Create a virtual environment
- Install all dependencies
- Start the API server
- Run system tests
- Optionally start data simulation

### Manual Setup

If you prefer manual setup:

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the API server**:
   ```bash
   python app.py
   ```

4. **Run tests** (in another terminal):
   ```bash
   python test_system.py
   ```

5. **Start data simulation**:
   ```bash
   python data_simulator.py
   ```

## 📊 API Endpoints

### Core Endpoints
- `GET /` - API information and available endpoints
- `GET /health` - System health check
- `GET /docs` - Interactive API documentation (Swagger UI)

### Patient Management
- `POST /patients` - Create new patient
- `GET /patients` - List all patients

### Wearable Data
- `POST /wearable-data` - Submit wearable device data
- `GET /wearable-data/{patient_id}` - Get patient's wearable data

### Predictions
- `GET /predictions/{patient_id}` - Get patient's risk predictions
- `PUT /predictions/{prediction_id}/outcome` - Update actual outcome

### Dashboard Data (Power BI Integration)
- `GET /dashboard-data/overview` - System overview statistics
- `GET /dashboard-data/predictions-vs-actual` - Prediction accuracy data

## 🔮 Machine Learning Model

The system uses a Random Forest classifier trained on:

### Features:
- Heart Rate (BPM)
- Blood Pressure (Systolic/Diastolic)
- Body Temperature (°F)
- Oxygen Saturation (%)
- Activity Level (0-10 scale)

### Risk Categories:
- **Low Risk**: < 30% deterioration probability
- **Medium Risk**: 30-70% deterioration probability  
- **High Risk**: > 70% deterioration probability

### Model Performance:
- Tracks prediction accuracy vs actual outcomes
- Provides confusion matrix for model evaluation
- Identifies contributing risk factors for each prediction

## 📈 Power BI Dashboard Setup

### Automatic Setup:
1. Review the `powerbi_config.json` file for dashboard configuration
2. The API provides two main endpoints for Power BI:
   - `/dashboard-data/overview` - Summary statistics
   - `/dashboard-data/predictions-vs-actual` - Prediction performance

### Manual Setup:
1. Open Power BI Desktop
2. Get Data → Web
3. Enter API endpoint URLs:
   - Overview: `http://localhost:8000/dashboard-data/overview`
   - Predictions: `http://localhost:8000/dashboard-data/predictions-vs-actual`
4. Configure visualizations:
   - **Cards**: Total patients, data points, predictions
   - **Donut Chart**: Risk level distribution
   - **Gauge**: Prediction accuracy
   - **Line Chart**: Risk trends over time
   - **Matrix**: Confusion matrix
   - **Table**: Patient risk details

### Recommended Visualizations:
- Patient overview metrics
- Risk distribution by category
- Prediction accuracy gauge
- Timeline of predictions vs actual outcomes
- Confusion matrix for model performance
- Patient risk level table

## 🧪 Testing & Validation

### Automated Testing:
```bash
python test_system.py
```

Tests include:
- ✅ Health check validation
- ✅ Patient creation and retrieval
- ✅ Wearable data collection
- ✅ Prediction generation
- ✅ High-risk scenario detection
- ✅ Dashboard endpoints
- ✅ Outcome tracking

### Data Simulation:
```bash
python data_simulator.py
```

Simulates 5 patients with different risk profiles:
- **High Risk**: Elderly patients with multiple conditions
- **Medium Risk**: Middle-aged patients with some conditions  
- **Low Risk**: Younger, healthy patients

### Demo Mode:
```bash
python data_simulator.py demo
```

Runs a scripted demo with normal and high-risk scenarios.

## 📁 File Structure

```
digital-twin-medtech/
├── app.py                    # Main FastAPI application
├── data_simulator.py         # Wearable data simulation
├── test_system.py           # System tests
├── start_system.sh          # Startup script
├── requirements.txt         # Python dependencies
├── powerbi_config.json      # Power BI configuration
├── README.md               # This file
├── digital_twin.db         # SQLite database (created at runtime)
└── venv/                   # Virtual environment (created at setup)
```

## 🔧 Configuration

### Environment Variables:
Create a `.env` file for configuration:
```
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=sqlite:///digital_twin.db
MODEL_RETRAIN_INTERVAL=24  # hours
```

### Database Schema:
- **patients**: Patient demographic and medical history
- **wearable_data**: Real-time vitals and activity data
- **predictions**: Risk assessments and actual outcomes

## 🛡️ Security Considerations

**Note**: This is an MVP for demonstration purposes. For production use:

- Implement proper authentication and authorization
- Use HTTPS for all communications
- Encrypt sensitive patient data
- Implement data anonymization
- Add input validation and sanitization
- Use environment variables for secrets
- Implement rate limiting
- Add comprehensive logging and monitoring

## 🚧 Future Enhancements

- [ ] Real device integration (Fitbit, Apple Watch, etc.)
- [ ] Advanced ML models (LSTM, Transformer networks)
- [ ] Real-time alerting system
- [ ] Mobile application
- [ ] Integration with EHR systems
- [ ] Advanced analytics dashboard
- [ ] Multi-tenant architecture
- [ ] Cloud deployment (AWS, Azure, GCP)
- [ ] FHIR compliance
- [ ] WebSocket real-time updates

## 📞 API Usage Examples

### Create Patient:
```bash
curl -X POST "http://localhost:8000/patients" \
-H "Content-Type: application/json" \
-d '{
  "patient_id": "PAT001",
  "name": "John Doe", 
  "age": 65,
  "gender": "male",
  "medical_conditions": ["hypertension", "diabetes"]
}'
```

### Submit Wearable Data:
```bash
curl -X POST "http://localhost:8000/wearable-data" \
-H "Content-Type: application/json" \
-d '{
  "patient_id": "PAT001",
  "timestamp": "2024-01-15T10:30:00",
  "heart_rate": 85.0,
  "blood_pressure_systolic": 140.0,
  "blood_pressure_diastolic": 90.0,
  "temperature": 98.6,
  "oxygen_saturation": 97.0,
  "activity_level": 3.5
}'
```

### Get Predictions:
```bash
curl "http://localhost:8000/predictions/PAT001"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything works
5. Submit a pull request

## 📄 License

This project is for educational and demonstration purposes. Please ensure compliance with healthcare regulations (HIPAA, GDPR, etc.) before using with real patient data.

---

**⚡ Ready to explore digital healthcare innovation!** 

Start with `./start_system.sh` and visit `http://localhost:8000/docs` for interactive API documentation.
