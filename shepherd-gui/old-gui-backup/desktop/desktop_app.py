#!/usr/bin/env python3
"""
Shepherd Desktop App
A native desktop wrapper for the Shepherd application using webview
"""

import sys
import threading
import time
import subprocess
import signal
import os
from pathlib import Path

try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger
from app import create_interface


class ShepherdDesktopApp:
    def __init__(self):
        self.logger = get_logger('desktop_app')
        self.gradio_process = None
        self.demo = None
        self.port = 7861  # Different port to avoid conflicts
        
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
        import requests
        
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
    
    def check_webview_platform(self):
        """Check if webview platform dependencies are available"""
        if not WEBVIEW_AVAILABLE:
            return False, "webview package not installed"
        
        # Test GTK platform
        try:
            import gi
            gi.require_version('Gtk', '3.0')
            gi.require_version('WebKit2', '4.0')
            return True, "GTK platform available"
        except ImportError as e:
            pass
        
        # Test Qt platform  
        try:
            from PyQt6.QtCore import QCoreApplication
            from PyQt6.QtWebEngineWidgets import QWebEngineView
            return True, "Qt platform available"
        except ImportError as e:
            pass
        
        return False, "No suitable platform (GTK/Qt) dependencies found"
    
    def create_webview_window(self):
        """Create native desktop window"""
        # Check platform availability first
        platform_ok, platform_msg = self.check_webview_platform()
        if not platform_ok:
            self.logger.warning(f"Webview platform check failed: {platform_msg}")
            return False
        
        self.logger.info(f"Creating desktop window - {platform_msg}")
        
        try:
            # Create window
            window = webview.create_window(
                title="🐑 Shepherd - Intelligent Workflow Orchestrator",
                url=f"http://127.0.0.1:{self.port}",
                width=1200,
                height=800,
                min_size=(800, 600),
                resizable=True,
                shadow=True,
                on_top=False
            )
            
            # Start webview
            webview.start(debug=False)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create webview window: {e}")
            self.logger.info("System dependencies missing - falling back to browser mode")
            return False
    
    def launch_desktop_app(self):
        """Launch the complete desktop application"""
        self.logger.info("Launching Shepherd Desktop App")
        
        # Start Gradio server in background thread
        server_thread = threading.Thread(target=self.start_gradio_server, daemon=True)
        server_thread.start()
        
        # Wait for server to be ready
        if not self.wait_for_server():
            self.logger.error("Failed to start application server")
            return False
        
        # Create and show desktop window
        if WEBVIEW_AVAILABLE:
            self.logger.info("Attempting native webview window")
            if self.create_webview_window():
                return True
            else:
                self.logger.warning("Native webview failed, falling back to browser")
        else:
            self.logger.warning("webview not available, using browser fallback")
        
        # Fallback to browser with app mode
        return self.fallback_to_browser()
    
    def fallback_to_browser(self):
        """Fallback to browser if webview not available"""
        import webbrowser
        
        self.logger.info("Opening in default browser with app-like experience")
        url = f"http://127.0.0.1:{self.port}"
        
        try:
            # Try to open in app mode if Chrome/Chromium is available
            chrome_commands = [
                "google-chrome",
                "google-chrome-stable", 
                "chromium",
                "chromium-browser"
            ]
            
            app_mode_opened = False
            for chrome_cmd in chrome_commands:
                try:
                    # Check if Chrome/Chromium is available
                    subprocess.run([chrome_cmd, "--version"], 
                                 capture_output=True, check=True)
                    
                    # Open in app mode (kiosk-like experience)
                    subprocess.Popen([
                        chrome_cmd,
                        f"--app={url}",
                        "--no-first-run",
                        "--disable-default-apps",
                        "--disable-extensions",
                        "--disable-infobars",
                        "--disable-features=TranslateUI",
                        "--window-size=1200,800"
                    ])
                    
                    self.logger.info(f"Opened {url} in {chrome_cmd} app mode")
                    app_mode_opened = True
                    break
                    
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            # If Chrome app mode failed, use default browser
            if not app_mode_opened:
                webbrowser.open(url)
                self.logger.info(f"Opened {url} in default browser")
            
            # Keep the server running
            print(f"\n🐑 Shepherd Desktop App")
            print(f"Running at: {url}")
            if app_mode_opened:
                print("Opened in app mode for better desktop experience")
            print("Press Ctrl+C to stop the application\n")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("Received shutdown signal")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to open browser: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        self.logger.info("Cleaning up application")
        
        if self.demo:
            try:
                self.demo.close()
            except:
                pass
        
        if self.gradio_process:
            try:
                self.gradio_process.terminate()
            except:
                pass


def install_webview():
    """Install webview package for native desktop experience"""
    logger = get_logger('installer')
    logger.info("Installing webview package for native desktop support...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview[qt]"])
        logger.info("Successfully installed pywebview with Qt backend")
        return True
    except subprocess.CalledProcessError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview[gtk]"])
            logger.info("Successfully installed pywebview with GTK backend")
            return True
        except subprocess.CalledProcessError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview"])
                logger.info("Successfully installed pywebview with default backend")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install pywebview: {e}")
                return False


def main():
    logger = get_logger('desktop_main')
    
    # Handle arguments
    if "--install-webview" in sys.argv:
        return 0 if install_webview() else 1
    
    # Check if webview is available
    if not WEBVIEW_AVAILABLE:
        print("🐑 Shepherd Desktop App")
        print("=" * 50)
        print("For the best desktop experience, install the webview package:")
        print(f"  {sys.executable} -m pip install 'pywebview[qt]'")
        print("Or run: python desktop_app.py --install-webview")
        print()
        print("Falling back to browser mode...")
        print()
    
    # Create and launch app
    app = ShepherdDesktopApp()
    
    # Set up signal handlers
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        app.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        success = app.launch_desktop_app()
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