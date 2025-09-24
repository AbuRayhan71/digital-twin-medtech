-- Digital Twin Database Schema
CREATE DATABASE IF NOT EXISTS digital_twin;
USE digital_twin;

-- Patients table
CREATE TABLE patients (
  patient_id VARCHAR(36) PRIMARY KEY,
  given_name VARCHAR(100),
  family_name VARCHAR(100),
  dob DATE,
  gender VARCHAR(10),
  blood_type VARCHAR(3),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Devices table
CREATE TABLE devices (
  device_id VARCHAR(36) PRIMARY KEY,
  patient_id VARCHAR(36),
  device_type VARCHAR(50),
  installed_at TIMESTAMP,
  FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

-- Raw vitals data table
CREATE TABLE vitals_raw (
  event_id VARCHAR(36) PRIMARY KEY,
  device_id VARCHAR(36),
  patient_id VARCHAR(36),
  recorded_at DATETIME,
  heart_rate INT,
  spo2 FLOAT,
  systolic INT,
  diastolic INT,
  temperature FLOAT,
  respiratory_rate INT,
  payload JSON,
  ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast queries
CREATE INDEX idx_vitals_patient_time ON vitals_raw(patient_id, recorded_at);

-- Triage logs table
CREATE TABLE triage_logs (
  triage_id VARCHAR(36) PRIMARY KEY,
  patient_id VARCHAR(36),
  triage_level VARCHAR(20),
  triage_time DATETIME,
  notes TEXT
);

-- Insert sample data
INSERT INTO patients (patient_id, given_name, family_name, dob, gender, blood_type) VALUES
('patient-001', 'John', 'Doe', '1980-05-15', 'M', 'O+'),
('patient-002', 'Jane', 'Smith', '1992-11-22', 'F', 'A-'),
('patient-003', 'Mike', 'Johnson', '1975-08-03', 'M', 'B+');