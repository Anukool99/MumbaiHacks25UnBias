import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def get_supabase_client() -> Optional[Client]:
    """
    Get Supabase client instance.
    Returns None if environment variables are missing (with a warning).
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    print("DEBUG — SUPABASE_URL:", supabase_url)
    print("DEBUG — SUPABASE_KEY exists:", bool(supabase_key))

    if not supabase_url or not supabase_key:
        print("WARNING: SUPABASE_URL or SUPABASE_KEY environment variables are missing.")
        print("Supabase client will not be initialized.")
        return None
    
    try:
        print("DEBUG — Creating Supabase client...")
        client = create_client(supabase_url, supabase_key)
        print("DEBUG — Supabase client initialized successfully")
        return client
    except Exception as e:
        print(f"WARNING: Failed to create Supabase client: {e}")
        return None


# Initialize client on module import (optional, can be lazy-loaded)
supabase: Optional[Client] = get_supabase_client()
