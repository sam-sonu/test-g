"""
Startup script for the AI Question Generator Server
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {missing_packages}")
        print("Please install dependencies using: pip install fastapi uvicorn pydantic python-multipart")
        return False
    
    return True

def start_server():
    """Start the AI Question Generator server"""
    if not check_dependencies():
        sys.exit(1)
    
    # Change to the model server directory
    model_server_dir = Path(__file__).parent / "model_server"
    os.chdir(model_server_dir)
    
    print("Starting AI Question Generator Server...")
    print("Server will be available at: http://localhost:8001")
    print("API Documentation: http://localhost:8001/docs")
    print("\nPress Ctrl+C to stop the server")
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app:app",
            "--host", "0.0.0.0",
            "--port", "8001",
            "--reload",
            "--log-level", "info"
        ], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
