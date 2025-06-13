#!/usr/bin/env python3
"""
Streamlit app launcher with PyTorch compatibility fixes
"""
import os
import sys
import subprocess

def setup_environment():
    """Set up environment variables to prevent PyTorch-Streamlit conflicts"""
    
    # Disable PyTorch JIT compilation which can cause issues with Streamlit
    os.environ['PYTORCH_JIT'] = '0'
    
    # Disable PyTorch distributed backend
    os.environ['TORCH_DISTRIBUTED_DEBUG'] = 'OFF'
    
    # Set MPS fallback to CPU for problematic operations
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
    
    # Prevent Streamlit from watching torch modules
    os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
    
    # Disable automatic rerun on file changes to prevent conflicts
    os.environ['STREAMLIT_SERVER_RUNON_SAVE'] = 'false'
    
    print("🔧 Environment configured for PyTorch-Streamlit compatibility")

def run_streamlit():
    """Run the Streamlit application"""
    
    setup_environment()
    
    # Default arguments
    args = [
        'streamlit', 'run', 'app.py',
        '--server.headless', 'false',
        '--server.port', '8501',
        '--server.address', '0.0.0.0',
        '--browser.serverAddress', 'localhost',
        '--browser.gatherUsageStats', 'false'
    ]
    
    # Allow command line arguments to override defaults
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    
    print("🌲 Starting Ghost Forest Watcher...")
    print(f"🚀 Command: {' '.join(args)}")
    
    try:
        # Run streamlit
        result = subprocess.run(args, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        return 0

if __name__ == "__main__":
    sys.exit(run_streamlit()) 