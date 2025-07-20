#!/usr/bin/env python3
"""
Setup script for Striking Distance On-Page Analysis Tool
This script helps install all required dependencies and checks system compatibility.
"""

import subprocess
import sys
import importlib.util
import platform

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {platform.python_version()}")
        return False
    print(f"✅ Python {platform.python_version()} is compatible")
    return True

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def check_package(package):
    """Check if a package is installed"""
    spec = importlib.util.find_spec(package)
    return spec is not None

def main():
    """Main setup function"""
    print("🎯 Setting up Striking Distance On-Page Analysis Tool")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Required packages
    required_packages = [
        "streamlit",
        "pandas",
        "openpyxl",
        "xlrd",
        "crawl4ai"
    ]
    
    # Check and install packages
    missing_packages = []
    for package in required_packages:
        if check_package(package):
            print(f"✅ {package} is already installed")
        else:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            if not install_package(package):
                print(f"\n❌ Failed to install {package}")
                print("Please install manually: pip install", package)
                sys.exit(1)
    
    # Verify crawl4ai installation
    try:
        from crawl4ai import AsyncWebCrawler
        print("✅ crawl4ai is working correctly")
    except ImportError as e:
        print(f"❌ crawl4ai import error: {e}")
        print("\n🔧 Troubleshooting crawl4ai:")
        print("1. Try: pip install --upgrade crawl4ai")
        print("2. Ensure Chrome/Chromium is installed")
        print("3. Check: https://github.com/unclecode/crawl4ai for latest instructions")
        sys.exit(1)
    
    print("\n🎉 Setup complete!")
    print("\nTo run the application:")
    print("streamlit run app.py")
    
    # Test run suggestion
    print("\n🧪 Want to test the setup?")
    print("The app will open in your browser automatically.")

if __name__ == "__main__":
    main()
