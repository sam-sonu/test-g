"""
Setup script for AI Question Generator
Automates the complete setup process
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🤖 AI Question Generator for QuizHive - Setup")
    print("=" * 60)
    print()


def check_python_version():
    """Check Python version"""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {sys.version}")
        return False
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True


def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Install essential packages first
        essential_packages = [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.4.0",
            "python-multipart>=0.0.6",
            "requests>=2.31.0",
            "pandas>=2.0.0"
        ]
        
        for package in essential_packages:
            print(f"   Installing {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to install {package}")
                print(f"   Error: {result.stderr}")
                return False
        
        print("✅ Dependencies installed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def analyze_questions():
    """Analyze existing questions"""
    print("\n📊 Analyzing existing questions...")
    
    try:
        # Check if question bank exists
        question_bank_path = Path("../quizhive/app/question_bank")
        if not question_bank_path.exists():
            print("⚠️  Question bank not found at ../quizhive/app/question_bank")
            print("   Using sample data for analysis")
            return True
        
        # Run analysis
        result = subprocess.run([
            sys.executable, "training/extract_question_patterns.py"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ Question analysis completed")
            print("   Analysis saved to data/ directory")
            return True
        else:
            print(f"⚠️  Question analysis failed: {result.stderr}")
            return True  # Continue even if analysis fails
            
    except Exception as e:
        print(f"⚠️  Error during question analysis: {e}")
        return True  # Continue even if analysis fails


def test_server():
    """Test the AI server"""
    print("\n🧪 Testing AI server...")
    
    try:
        # Give server a moment to start
        time.sleep(3)
        
        # Run API tests
        result = subprocess.run([
            sys.executable, "test_api.py"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ AI server tests passed")
            return True
        else:
            print(f"❌ AI server tests failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False


def start_ai_server():
    """Start the AI server"""
    print("\n🚀 Starting AI Question Generator server...")
    
    try:
        # Start server in background
        subprocess.Popen([
            sys.executable, "start_server.py"
        ], cwd=Path(__file__).parent)
        
        print("✅ AI server starting...")
        print("   Server will be available at: http://localhost:8001")
        print("   API Documentation: http://localhost:8001/docs")
        return True
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False


def show_next_steps():
    """Show next steps"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print()
    print("📋 Next Steps:")
    print()
    print("1. 🤖 AI Server is running at: http://localhost:8001")
    print("2. 📚 View API docs at: http://localhost:8001/docs")
    print("3. 🔗 QuizHive integration available at: /ai/* endpoints")
    print()
    print("🧪 Test the API:")
    print("   curl http://localhost:8001/health")
    print()
    print("📝 Generate Questions:")
    print("   curl -X POST http://localhost:8001/generate-questions \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"topic\":\"AWS\",\"level\":\"beginner\",\"num_questions\":3}'")
    print()
    print("📖 For more information, see README.md")
    print()
    print("🔧 To stop the server: Press Ctrl+C in the server terminal")
    print()


def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Analyze questions
    if not analyze_questions():
        print("\n⚠️  Continuing with setup despite analysis issues")
    
    # Start server
    if not start_ai_server():
        print("\n❌ Setup failed during server startup")
        sys.exit(1)
    
    # Test server
    if not test_server():
        print("\n⚠️  Server started but tests failed")
        print("   Check the server logs for details")
    
    # Show next steps
    show_next_steps()


if __name__ == "__main__":
    main()
