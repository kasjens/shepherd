#!/usr/bin/env python3
"""
Shepherd Chrome App Mode Launcher
A reliable desktop app experience using Chrome's app mode
"""

import sys
import threading
import time
import subprocess
import signal
import os
import requests
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger
from app import create_interface


class ShepherdAppMode:
    def __init__(self):
        self.logger = get_logger('app_mode')
        self.demo = None
        self.port = 7862  # Different port to avoid conflicts
        self.chrome_process = None
        
    def start_gradio_server(self):
        """Start Gradio server in background"""
        self.logger.info(f"Starting Gradio server on port {self.port}")
        
        try:
            self.demo = create_interface()
            # Start server without opening browser
            self.demo.launch(
                server_name="127.0.0.1",
                server_port=self.port,
                share=False,
                inbrowser=False,
                quiet=True,
                prevent_thread_lock=True
            )
            self.logger.info("Gradio server started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start Gradio server: {e}")
            return False
    
    def wait_for_server(self, timeout=10):
        """Wait for server to be ready"""
        url = f"http://127.0.0.1:{self.port}"
        for i in range(timeout):
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    self.logger.info(f"Server ready at {url}")
                    return True
            except:
                pass
            time.sleep(1)
        
        self.logger.error("Server failed to start within timeout")
        return False
    
    def launch_chrome_app(self):
        """Launch Chrome in app mode"""
        url = f"http://127.0.0.1:{self.port}"
        
        chrome_commands = [
            "google-chrome",
            "google-chrome-stable", 
            "chromium",
            "chromium-browser"
        ]
        
        for chrome_cmd in chrome_commands:
            try:
                # Check if Chrome/Chromium is available
                subprocess.run([chrome_cmd, "--version"], 
                             capture_output=True, check=True)
                
                # Launch Chrome in app mode
                self.chrome_process = subprocess.Popen([
                    chrome_cmd,
                    f"--app={url}",
                    "--no-first-run",
                    "--disable-default-apps",
                    "--disable-extensions",
                    "--disable-infobars",
                    "--disable-features=TranslateUI",
                    "--disable-web-security",
                    "--window-size=1200,800",
                    "--class=Shepherd"  # Custom window class
                ])
                
                self.logger.info(f"Launched Shepherd in {chrome_cmd} app mode")
                return True
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        # Fallback to default browser
        import webbrowser
        webbrowser.open(url)
        self.logger.warning("Chrome not found, opened in default browser")
        return True
    
    def launch_app(self):
        """Launch the complete application"""
        self.logger.info("Launching Shepherd in Chrome App Mode")
        
        # Start Gradio server in background thread
        server_thread = threading.Thread(target=self.start_gradio_server, daemon=True)
        server_thread.start()
        
        # Wait for server to be ready
        if not self.wait_for_server():
            self.logger.error("Failed to start application server")
            return False
        
        # Launch Chrome app
        if not self.launch_chrome_app():
            self.logger.error("Failed to launch Chrome app")
            return False
        
        # Keep the application running
        print(f"\n🐑 Shepherd Desktop App")
        print(f"Running at: http://127.0.0.1:{self.port}")
        print("Opened in Chrome app mode for desktop-like experience")
        print("Press Ctrl+C to stop the application\n")
        
        try:
            # Wait for Chrome process or keep server alive
            if self.chrome_process:
                self.chrome_process.wait()
            else:
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        
        return True
    
    def cleanup(self):
        """Clean up resources"""
        self.logger.info("Cleaning up application")
        
        if self.chrome_process:
            try:
                self.chrome_process.terminate()
                self.chrome_process.wait(timeout=5)
            except:
                try:
                    self.chrome_process.kill()
                except:
                    pass
        
        if self.demo:
            try:
                self.demo.close()
            except:
                pass


def main():
    logger = get_logger('app_mode_main')
    
    # Create and launch app
    app = ShepherdAppMode()
    
    # Set up signal handlers
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        app.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        success = app.launch_app()
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Application failed: {e}", exc_info=True)
        return 1
    finally:
        app.cleanup()


if __name__ == "__main__":
    sys.exit(main())