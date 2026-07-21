from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Bayandana API",
    description="SaaS Manajemen Keuangan Masjid (PSAK 109)",
    version="1.0.0"
)

# Mengizinkan akses lintas platform (CORS) agar UI nantinya bisa mengakses API ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API Bayandana menyala dan siap!"}