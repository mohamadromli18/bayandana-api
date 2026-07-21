import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Memuat variabel dari file .env (hanya berlaku saat dijalankan lokal)
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Kredensial Supabase tidak ditemukan!")

# Inisialisasi klien yang akan digunakan oleh seluruh endpoint
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)