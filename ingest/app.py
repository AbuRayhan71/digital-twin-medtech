"""
Digital Twin Ingestion Service

FastAPI service for receiving and storing patient vital signs data
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import aiomysql
import asyncio
import json
import os
from datetime import datetime
from typing import Optional
import uuid

# FastAPI app
app = FastAPI(
    title="Digital Twin Ingestion API",
    description="Receives and stores patient vital signs data",
    version="1.0.0"
)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'db': os.getenv('DB_NAME', 'digital_twin'),
    'autocommit': True
}

# Data models
class VitalSigns(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    patient_id: str = Field(..., description="Patient identifier")
    device_id: str = Field(..., description="Device identifier")
    recorded_at: str = Field(..., description="ISO timestamp when vitals were recorded")
    heart_rate: int = Field(..., ge=0, le=300, description="Heart rate in BPM")
    spo2: float = Field(..., ge=0, le=100, description="SpO2 percentage")
    systolic: int = Field(..., ge=0, le=300, description="Systolic blood pressure")
    diastolic: int = Field(..., ge=0, le=200, description="Diastolic blood pressure")
    temperature: float = Field(..., ge=20, le=50, description="Body temperature in Celsius")
    respiratory_rate: Optional[int] = Field(None, ge=0, le=100, description="Respiratory rate")

class IngestResponse(BaseModel):
    status: str
    message: str
    event_id: str
    timestamp: str

# Database connection pool
connection_pool = None

async def get_db_pool():
    """Get database connection pool"""
    global connection_pool
    if connection_pool is None:
        connection_pool = await aiomysql.create_pool(
            minsize=5,
            maxsize=20,
            **DB_CONFIG
        )
    return connection_pool

async def close_db_pool():
    """Close database connection pool"""
    global connection_pool
    if connection_pool:
        connection_pool.close()
        await connection_pool.wait_closed()
        connection_pool = None

@app.on_event("startup")
async def startup():
    """Initialize database connection pool"""
    await get_db_pool()
    print("🚀 Ingest API started - Database pool initialized")

@app.on_event("shutdown")
async def shutdown():
    """Close database connections"""
    await close_db_pool()
    print("🛑 Ingest API shutdown - Database pool closed")

@app.post("/ingest", response_model=IngestResponse)
async def ingest_vitals(vitals: VitalSigns):
    """
    Ingest vital signs data from wearable devices
    """
    try:
        pool = await get_db_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Insert into vitals_raw table
                insert_query = """
                INSERT INTO vitals_raw 
                (event_id, device_id, patient_id, recorded_at, heart_rate, spo2, 
                 systolic, diastolic, temperature, respiratory_rate, payload)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Convert recorded_at to datetime
                recorded_at = datetime.fromisoformat(vitals.recorded_at.replace('Z', '+00:00'))
                
                await cursor.execute(insert_query, (
                    vitals.event_id,
                    vitals.device_id,
                    vitals.patient_id,
                    recorded_at,
                    vitals.heart_rate,
                    vitals.spo2,
                    vitals.systolic,
                    vitals.diastolic,
                    vitals.temperature,
                    vitals.respiratory_rate,
                    json.dumps(vitals.dict())
                ))
                
                print(f"✅ Stored vitals for patient {vitals.patient_id}: HR={vitals.heart_rate}, SpO2={vitals.spo2}%")
                
                return IngestResponse(
                    status="success",
                    message="Vitals data stored successfully",
                    event_id=vitals.event_id,
                    timestamp=datetime.utcnow().isoformat()
                )
                
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to store vitals data: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1")
                result = await cursor.fetchone()
        
        return {
            "status": "healthy",
            "database": "connected" if result else "error",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": f"error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/stats")
async def get_stats():
    """Get ingestion statistics"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Count total records
                await cursor.execute("SELECT COUNT(*) FROM vitals_raw")
                total_records = (await cursor.fetchone())[0]
                
                # Count records in last hour
                await cursor.execute("""
                    SELECT COUNT(*) FROM vitals_raw 
                    WHERE ingested_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
                """)
                recent_records = (await cursor.fetchone())[0]
                
                # Count unique patients
                await cursor.execute("SELECT COUNT(DISTINCT patient_id) FROM vitals_raw")
                unique_patients = (await cursor.fetchone())[0]
                
                return {
                    "total_records": total_records,
                    "records_last_hour": recent_records,
                    "unique_patients": unique_patients,
                    "timestamp": datetime.utcnow().isoformat()
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)