#!/usr/bin/env python3
"""
Setup script for Striking Distance On-Page Analysis Tool
This script helps install dependencies and check system requirements
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_chrome():
    """Check if Chrome/Chromium is available"""
    chrome_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        "chrome",
        "chromium",
        "google-chrome"
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            return True
    
    return False

def main():
    print("🔧 Setting up Striking Distance On-Page Analysis Tool")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Install requirements
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Check for Chrome/Chromium
    print("\n🔍 Checking for Chrome/Chromium...")
    if check_chrome():
        print("✅ Chrome/Chromium found")
    else:
        print("⚠️ Chrome/Chromium not found. Please install Chrome for crawl4ai to work properly")
        print("   Download: https://www.google.com/chrome/")
    
    print("\n🎉 Setup complete!")
    print("\nTo run the tool:")
    print("  streamlit run app.py")

if __name__ == "__main__":
    main()
