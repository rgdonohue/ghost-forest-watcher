#!/usr/bin/env python3
"""
Ghost Forest Watcher - Main Entry Point

Simple entry point to launch the Ghost Forest Watcher application.
This script provides an easy way to run the app from the project root.

Usage:
    python main.py                # Start the main application
    python main.py --safe         # Start in safe mode (no AI components)
    python main.py --test         # Run tests
"""

import sys
import subprocess
import argparse
from pathlib import Path

def main():
    """Main entry point for the Ghost Forest Watcher application"""
    
    parser = argparse.ArgumentParser(
        description="Ghost Forest Watcher - AI-Powered Forest Recovery Monitoring"
    )
    parser.add_argument(
        "--safe", 
        action="store_true", 
        help="Run in safe mode without AI components"
    )
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Run the test suite"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8501, 
        help="Port to run the Streamlit app on (default: 8501)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.test:
            # Run tests
            print("🧪 Running Ghost Forest Watcher test suite...")
            result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/", "-v"
            ], check=True)
            return result.returncode
            
        elif args.safe:
            # Run safe mode
            print("🔒 Starting Ghost Forest Watcher in safe mode...")
            cmd = [
                "streamlit", "run", "ghost_forest_watcher/app_safe.py",
                "--server.port", str(args.port)
            ]
            
        else:
            # Run main application
            print("🌲 Starting Ghost Forest Watcher...")
            cmd = [
                "streamlit", "run", "ghost_forest_watcher/app.py",
                "--server.port", str(args.port)
            ]
        
        # Execute the command
        print(f"🚀 Command: {' '.join(cmd)}")
        print(f"🌐 Access at: http://localhost:{args.port}")
        
        result = subprocess.run(cmd, check=True)
        return result.returncode
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 