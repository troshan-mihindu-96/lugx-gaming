from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import os
import json

app = FastAPI()

order_router = APIRouter()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB Connection utility
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "order-db"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "admin123"),
            database=os.getenv("DB_NAME", "ordersdb"),
            port=int(os.getenv("DB_PORT", 3306))
        )
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

# Pydantic models
class OrderIn(BaseModel):
    customer_name: str
    items: List[dict]
    total_price: float

class OrderOut(BaseModel):
    id: int
    customer_name: str
    items: List[dict]
    total_price: float
    order_date: datetime

# POST /orders/ → Place order
@order_router.post("/")
def place_order(order: OrderIn):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "INSERT INTO orders (customer_name, items, total_price) VALUES (%s, %s, %s)"
        cursor.execute(query, (
            order.customer_name,
            json.dumps(order.items),
            order.total_price
        ))
        connection.commit()
        cursor.close()
        connection.close()
        return {"status": "order placed"}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to place order: {e}")

# GET /orders/ → Get all orders
@order_router.get("/", response_model=List[OrderOut])
def get_orders():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT id, customer_name, items, total_price, order_date FROM orders ORDER BY order_date DESC"
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        orders = []
        for row in rows:
            orders.append({
                "id": row[0],
                "customer_name": row[1],
                "items": json.loads(row[2]),
                "total_price": row[3],
                "order_date": row[4]
            })

        return orders
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve orders: {e}")

# GET /orders/health → Health Check
@order_router.get("/health")
def health_check():
    return {"message": "Order Service is running"}

# Include router under /orders prefix
app.include_router(order_router)