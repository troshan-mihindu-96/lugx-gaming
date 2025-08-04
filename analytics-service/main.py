# analytics-service/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import clickhouse_connect
import json
import os

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ClickHouse Connection
CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))
USERNAME = os.getenv("CLICKHOUSE_USER", "default")
PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "admin123")
client = clickhouse_connect.get_client(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT, username=USERNAME, password=PASSWORD)

# Event Model
class PageEvent(BaseModel):
    event_type: str
    page: str
    timestamp: datetime
    details: Optional[dict] = {}

# Table Creation
@app.on_event("startup")
def create_clickhouse_table():
    try:
        client.command('''
            CREATE TABLE IF NOT EXISTS page_events (
                event_type String,
                page String,
                timestamp DateTime,
                details String
            )
            ENGINE = MergeTree()
            ORDER BY timestamp
        ''')
        print("✅ ClickHouse table 'page_events' ready.")
    except Exception as e:
        print("❌ Table creation failed:", e)

# Track Event Endpoint
@app.post("/track/")
def track_event(event: PageEvent):
    try:
        client.insert(
            table='page_events',
            data=[(event.event_type, event.page, event.timestamp, json.dumps(event.details))],
            column_names=['event_type', 'page', 'timestamp', 'details']
        )
        return {"status": "tracked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track event: {e}")

# Simple Health Check
@app.get("/")
def health():
    return {"message": "Analytics Service is running"}
