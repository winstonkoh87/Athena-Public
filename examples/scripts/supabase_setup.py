#!/usr/bin/env python3
"""
Execute the Supabase schema setup via the service role key.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def run_schema():
    print("=" * 60)
    print("SUPABASE SCHEMA SETUP")
    print("=" * 60)
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"✅ Connected to: {SUPABASE_URL}")
    
    # Step 1: Enable pgvector
    print("\n1️⃣  Enabling pgvector extension...")
    try:
        supabase.postgrest.rpc("", {}).execute()  # Dummy to check connection
    except:
        pass
    
    # We need to use raw SQL - Supabase doesn't allow CREATE EXTENSION via client
    # User will need to run the SQL in dashboard
    print("   ⚠️  pgvector must be enabled in Supabase Dashboard:")
    print("      → Database → Extensions → Search 'vector' → Enable")
    
    # Step 2: Create tables via RPC or direct SQL
    # Since we can't run DDL via client, let's check if tables exist
    print("\n2️⃣  Checking if tables exist...")
    
    try:
        result = supabase.table("sessions").select("id").limit(1).execute()
        print("   ✅ 'sessions' table exists")
    except Exception as e:
        if "does not exist" in str(e):
            print("   ❌ 'sessions' table does NOT exist")
            print("   → Please run the SQL in: .agent/scripts/supabase_schema.sql")
        else:
            print(f"   ⚠️  Unknown error: {e}")
    
    try:
        result = supabase.table("case_studies").select("id").limit(1).execute()
        print("   ✅ 'case_studies' table exists")
    except Exception as e:
        if "does not exist" in str(e):
            print("   ❌ 'case_studies' table does NOT exist")
            print("   → Please run the SQL in: .agent/scripts/supabase_schema.sql")
        else:
            print(f"   ⚠️  Unknown error: {e}")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Go to Supabase Dashboard → SQL Editor")
    print("2. Copy contents of: .agent/scripts/supabase_schema.sql")
    print("3. Run the SQL")
    print("4. Then run: python .agent/scripts/supabase_sync.py")
    print("=" * 60)


if __name__ == "__main__":
    run_schema()
