#!/usr/bin/env python3
"""
Test script to check if Chrome/Chromium app mode is available
"""

import subprocess
import webbrowser

def test_chrome_app_mode():
    """Test if Chrome/Chromium app mode is available"""
    chrome_commands = [
        "google-chrome",
        "google-chrome-stable", 
        "chromium",
        "chromium-browser"
    ]
    
    print("🐑 Testing Chrome/Chromium App Mode Support")
    print("=" * 50)
    
    for chrome_cmd in chrome_commands:
        try:
            # Check if Chrome/Chromium is available
            result = subprocess.run([chrome_cmd, "--version"], 
                                  capture_output=True, check=True, text=True)
            
            print(f"✅ Found: {chrome_cmd}")
            print(f"   Version: {result.stdout.strip()}")
            print(f"   App mode will work with: {chrome_cmd} --app=<url>")
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ Not found: {chrome_cmd}")
            continue
    
    print("\n⚠️  No Chrome/Chromium found")
    print("   Will fall back to default browser")
    print("   To get app mode, install Chrome or Chromium:")
    print("   sudo apt install google-chrome-stable")
    print("   # or")
    print("   sudo apt install chromium-browser")
    
    return False

if __name__ == "__main__":
    test_chrome_app_mode()