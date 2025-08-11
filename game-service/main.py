from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import mysql.connector
from mysql.connector import Error
import os

app = FastAPI()

game_router = APIRouter()

# Enable CORS for frontend access via Ingress
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in prod with allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Pydantic models
class Game(BaseModel):
    name: str
    category: str
    price: float
    release_date: str

class GameOut(Game):
    id: int

# DB Connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "game-db"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "admin123"),
            database=os.getenv("DB_NAME", "gamesdb"),
            port=int(os.getenv("DB_PORT", 3306))
        )
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

# GET /games/ → List Games
@game_router.get("/api/games", response_model=List[GameOut])
@game_router.get("/api/games/", response_model=List[GameOut])
@game_router.get("/", response_model=List[GameOut])
def list_games():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, category, price, release_date FROM games")
        rows = cursor.fetchall()
        return [
            {
                "id": r[0],
                "name": r[1],
                "category": r[2],
                "price": r[3],
                "release_date": str(r[4]) if r[4] else "N/A" # Handle NULL values
            } for r in rows
        ]
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve games: {e}")
    finally:
        cursor.close()
        conn.close()

# POST /games/ → Add Game
@game_router.post("/api/games")
@game_router.post("/api/games/")
@game_router.post("/")
def create_game(game: Game):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO games (name, category, price, release_date) VALUES (%s, %s, %s, %s)",
            (game.name, game.category, game.price, game.release_date)
        )
        conn.commit()
        return {"status": "Game added"}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to add game: {e}")
    finally:
        cursor.close()
        conn.close()

# GET /games/health → Health check endpoint
@game_router.get("/health")
def health_check():
    return {"message": "Game Service is running"}

# Mount router under /games prefix
app.include_router(game_router, prefix="/api/games")