from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import supabase
from app.api.v1.endpoints import organizations # Impor router baru

app = FastAPI(title="Bayandana API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mendaftarkan rute organisasi
app.include_router(
    organizations.router, 
    prefix="/api/v1/organizations", 
    tags=["Organizations"]
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API Bayandana menyala!"}

@app.get("/test-db")
def test_db_connection():
    try:
        response = supabase.table("organizations").select("*").execute()
        return {"status": "terhubung", "data": response.data}
    except Exception as e:
        return {"status": "gagal", "error": str(e)}