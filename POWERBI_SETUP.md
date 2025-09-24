# Power BI Dashboard Setup for Digital Twin MedTech MVP

This guide will help you create a comprehensive Power BI dashboard for the Digital Twin MedTech system.

## Prerequisites

1. **Digital Twin API Running**: Ensure the API server is running on `http://localhost:8000`
2. **Power BI Desktop**: Download and install Power BI Desktop from Microsoft
3. **Sample Data**: Run the data simulator to generate sample data

## Quick Setup Steps

### Step 1: Start the Digital Twin System

```bash
# Start the API server
python3 simple_app.py

# In another terminal, run the data simulator
python3 simple_simulator.py demo
```

### Step 2: Connect Power BI to the API

1. Open Power BI Desktop
2. Click **"Get Data"** → **"Web"**
3. Enter the API endpoint URLs (see below)
4. Click **"OK"** and **"Load"**

### API Endpoints for Power BI

#### Primary Data Sources:

**1. Dashboard Overview**
- URL: `http://localhost:8000/dashboard-data/overview`
- Contains: Patient counts, data point counts, risk distribution

**2. Patient List**
- URL: `http://localhost:8000/patients`
- Contains: Patient demographics and medical conditions

**3. Health Check**
- URL: `http://localhost:8000/health`
- Contains: System status and timestamp

### Step 3: Create Visualizations

#### Recommended Visualizations:

**1. Key Performance Indicators (Cards)**
- Total Patients
- Total Data Points  
- Total Predictions
- System Status

**2. Risk Distribution (Donut Chart)**
- Data: risk_distribution from overview endpoint
- Legend: risk_level
- Values: count
- Colors: 
  - High Risk: Red (#FF0000)
  - Medium Risk: Orange (#FF8C00)
  - Low Risk: Green (#32CD32)

**3. Patient Demographics (Bar Chart)**
- Data: patients endpoint
- Axis: gender
- Values: count of patients
- Legend: medical_conditions (if needed)

**4. System Health Indicator (Gauge)**
- Data: health endpoint
- Value: status (convert to numeric: healthy=100, unhealthy=0)
- Target: 100

### Step 4: Configure Data Refresh

1. Go to **"Home"** → **"Transform Data"**
2. For each query, go to **"Data Source Settings"**
3. Set refresh interval to **15 minutes**
4. Enable **"Background Refresh"**

### Step 5: Format and Style the Dashboard

#### Layout Suggestion:
```
┌─────────────────────────────────────────────────────────────┐
│  DIGITAL TWIN MEDTECH - PATIENT MONITORING DASHBOARD       │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│   Total     │   Total     │   Total     │   System        │
│ Patients    │ Data Points │Predictions  │   Health        │
│    [5]      │    [30]     │    [5]      │   [100%]        │
├─────────────┴─────────────┴─────────────┼─────────────────┤
│                                         │                 │
│        Risk Distribution                │   Patient       │
│      (Donut Chart)                      │ Demographics    │
│                                         │ (Bar Chart)     │
│                                         │                 │
└─────────────────────────────────────────┴─────────────────┘
```

#### Color Scheme:
- Primary: Medical Blue (#004B87)
- Secondary: Light Blue (#E3F2FD)
- Accent: Medical Green (#00A651)
- Warning: Orange (#FF8C00)
- Critical: Red (#DC3545)

### Step 6: Advanced Features (Optional)

#### Real-time Updates:
1. Go to **"Modeling"** → **"Manage Parameters"**
2. Create parameter for API base URL
3. Set up scheduled refresh every 15 minutes

#### Drill-down Capabilities:
1. Create hierarchy: Patient → Risk Level → Time
2. Enable drill-through on patient cards
3. Add filters for date range and risk level

#### Alerts and Notifications:
1. Set up data alerts for high-risk patients
2. Configure email notifications for critical events
3. Use conditional formatting for risk levels

### Step 7: Publish to Power BI Service (Optional)

1. Click **"Publish"** in Power BI Desktop
2. Choose your workspace
3. Configure scheduled refresh in the service
4. Set up sharing permissions
5. Create a public or embedded dashboard

## Sample Power BI Queries

### Query 1: Dashboard Overview
```
let
    Source = Json.Document(Web.Contents("http://localhost:8000/dashboard-data/overview")),
    #"Converted to Table" = Record.ToTable(Source)
in
    #"Converted to Table"
```

### Query 2: Risk Distribution
```
let
    Source = Json.Document(Web.Contents("http://localhost:8000/dashboard-data/overview")),
    risk_distribution = Source[risk_distribution],
    #"Converted to Table" = Table.FromList(risk_distribution, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
    #"Expanded Column1" = Table.ExpandRecordColumn(#"Converted to Table", "Column1", {"risk_level", "count"}, {"risk_level", "count"})
in
    #"Expanded Column1"
```

### Query 3: Patient List
```
let
    Source = Json.Document(Web.Contents("http://localhost:8000/patients")),
    #"Converted to Table" = Table.FromList(Source, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
    #"Expanded Column1" = Table.ExpandRecordColumn(#"Converted to Table", "Column1", {"patient_id", "name", "age", "gender", "medical_conditions"}, {"patient_id", "name", "age", "gender", "medical_conditions"})
in
    #"Expanded Column1"
```

## Troubleshooting

### Common Issues:

**1. Cannot Connect to API**
- Ensure the API server is running on localhost:8000
- Check Windows Firewall settings
- Verify the URL is correct

**2. Data Not Refreshing**
- Check data source credentials
- Verify network connectivity
- Review refresh schedule settings

**3. Visualizations Not Updating**
- Refresh the data model
- Check field mappings
- Verify data types are correct

**4. Performance Issues**
- Limit data to recent time periods
- Use aggregations where possible
- Consider using DirectQuery instead of Import mode

### Support Resources:

- **API Documentation**: Visit `http://localhost:8000` for endpoint information
- **Power BI Documentation**: https://docs.microsoft.com/en-us/power-bi/
- **Troubleshooting**: Check the console logs in the API server terminal

## Next Steps

1. **Enhanced Analytics**: Add prediction accuracy tracking, trend analysis, and statistical models
2. **Real-time Streaming**: Implement Power BI streaming datasets for live updates
3. **Mobile Optimization**: Create mobile-friendly dashboard versions
4. **Advanced Visualizations**: Add custom visuals for medical data representation
5. **Integration**: Connect to EHR systems, alert systems, and clinical workflows

---

**🎯 Goal**: Create actionable insights for healthcare providers to monitor patient health, predict deterioration risks, and improve patient outcomes through data-driven decisions.

**📱 Access**: Once published, your dashboard will be available at `https://app.powerbi.com/groups/[workspace]/dashboards/[dashboard-id]`