#!/usr/bin/env python3
"""
Setup script for Striking Distance On-Page Analysis Tool
This script helps install all required dependencies and checks the environment.
"""

import subprocess
import sys
import importlib.util
import os

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def check_package(package_name):
    """Check if a package is installed."""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def main():
    """Main setup function."""
    print("🎯 Setting up Striking Distance On-Page Analysis Tool")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Required packages
    required_packages = [
        "streamlit",
        "pandas",
        "numpy",
        "openpyxl",
        "xlrd",
        "crawl4ai"
    ]
    
    print("\n📦 Checking and installing required packages...")
    
    missing_packages = []
    for package in required_packages:
        if check_package(package):
            print(f"✅ {package} is already installed")
        else:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📥 Installing {len(missing_packages)} missing packages...")
        for package in missing_packages:
            print(f"Installing {package}...")
            if not install_package(package):
                print(f"Failed to install {package}. Please install manually.")
                sys.exit(1)
    
    # Verify crawl4ai installation
    try:
        from crawl4ai import AsyncWebCrawler
        print("✅ crawl4ai is working correctly")
    except ImportError as e:
        print(f"❌ crawl4ai import error: {e}")
        print("Please install crawl4ai manually:")
        print("pip install crawl4ai")
        sys.exit(1)
    
    print("\n🎉 Setup complete!")
    print("\nTo run the tool:")
    print("streamlit run app.py")
    
    # Test run option
    response = input("\nWould you like to test the tool now? (y/n): ").lower()
    if response == 'y':
        print("Starting Streamlit app...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    main()
