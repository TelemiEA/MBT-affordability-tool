#!/usr/bin/env python3
"""
Setup script for Supabase integration
Helps users set up their environment and test the connection
"""

import os
import sys
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists and has required variables."""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("   Please create a .env file based on .env.template")
        print("   1. Copy .env.template to .env")
        print("   2. Fill in your Supabase URL and API key")
        return False
    
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials in .env file!")
        print("   Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file")
        return False
    
    print("✅ Environment variables found")
    return True

def test_supabase_connection():
    """Test connection to Supabase."""
    try:
        from supabase_client import supabase_manager
        
        if not supabase_manager.is_connected():
            print("❌ Supabase client not connected")
            print("   Check your SUPABASE_URL and SUPABASE_ANON_KEY in .env file")
            return False
        
        print("✅ Supabase connection successful!")
        
        # Test basic functionality
        summary = supabase_manager.get_historical_summary()
        if 'error' in summary:
            print(f"⚠️ Warning: {summary['error']}")
            print("   This might indicate the database tables are not set up yet")
            print("   Please run the SQL from supabase_schema.sql in your Supabase SQL editor")
        else:
            print(f"✅ Database access working - found {summary.get('total_runs', 0)} historical runs")
        
        return True
        
    except ImportError as e:
        print("❌ Missing dependencies!")
        print("   Please install required packages: pip3 install supabase python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 MBT Affordability Tool - Supabase Setup")
    print("=" * 50)
    
    # Step 1: Check environment
    print("\n1. Checking environment configuration...")
    if not check_env_file():
        return False
    
    # Step 2: Test connection
    print("\n2. Testing Supabase connection...")
    if not test_supabase_connection():
        return False
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. If you haven't already, run the SQL from supabase_schema.sql in your Supabase SQL editor")
    print("2. Start the server: python3 enhanced_server.py")
    print("3. Open http://127.0.0.1:8001 in your browser")
    print("4. Run some automation scenarios to start collecting historical data")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)