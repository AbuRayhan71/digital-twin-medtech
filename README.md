Project Goal
Create a basic version (MVP) of a digital twin system that collects and analyzes data from wearable devices in real-time, predicts patient deterioration risk, stores all the records, and displays a comparison of predictions versus actual patient data using a Power BI dashboard.


Key Features Explained
•	Simulate live data from multiple wearable devices for many patients.
•	Send data immediately from devices to a central entry point, storing records in a MySQL database.
•	Use Spark Structured Streaming for real-time processing and extracting relevant features from the incoming data.
•	Build and run a Python machine learning model that provides a score for patient health risk (deterioration).
•	Serve the prediction model online and set up automated alerts triggered by specific risk thresholds.
•	Visualize the system’s predictions and compare them to actual readings in Power BI—so users can see “digital twin” outcomes vs. reality.

