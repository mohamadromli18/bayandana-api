from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import supabase
from app.api.v1.router import api_router

# Mengubah CDN default ke unpkg untuk menghindari blokiran pada jaringan/komputer tertentu
app = FastAPI(
    title="Bayandana API", 
    version="1.0.0",
    swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
    swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

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