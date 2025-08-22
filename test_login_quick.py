#!/usr/bin/env python3
"""
Quick test of improved login in headless mode.
"""

import asyncio
from mbt_automation_final import MBTAutomationFinal

async def test_login_quick():
    """Quick test of login functionality."""
    mbt = MBTAutomationFinal()
    
    try:
        print("Testing login in headless mode...")
        await mbt.start_browser(headless=True)
        
        login_result = await mbt.login()
        print(f"Login result: {login_result}")
        
        if login_result:
            print("✅ Headless login working!")
        else:
            print("❌ Headless login failed")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await mbt.close()

if __name__ == "__main__":
    asyncio.run(test_login_quick())