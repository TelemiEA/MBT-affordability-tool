#!/usr/bin/env python3
"""
Install export dependencies
"""

import subprocess
import sys

def install_export_dependencies():
    """Install the required dependencies for export functionality."""
    
    print("📦 INSTALLING EXPORT DEPENDENCIES")
    print("=" * 50)
    
    dependencies = [
        "pandas>=1.5.0",
        "openpyxl>=3.1.0",
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
        except Exception as e:
            print(f"❌ Error installing {dep}: {e}")
    
    # Test imports
    print("\n🧪 TESTING IMPORTS")
    print("-" * 30)
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
    
    try:
        import openpyxl
        print("✅ openpyxl imported successfully")
    except ImportError as e:
        print(f"❌ openpyxl import failed: {e}")
    
    print("\n🎉 Dependency installation complete!")
    print("Export functionality should now work properly.")

if __name__ == "__main__":
    install_export_dependencies()