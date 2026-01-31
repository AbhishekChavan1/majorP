"""Streamlit app launcher script"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Ensure GROQ_API_KEY is set
if not os.getenv("GROQ_API_KEY"):
    print("❌ GROQ_API_KEY environment variable not set")
    print("Please set it before running:")
    print("  Windows (PowerShell): $env:GROQ_API_KEY='your-key'")    
    print("  Linux/Mac: export GROQ_API_KEY='your-key'")
    sys.exit(1)

# Run Streamlit app
if __name__ == "__main__":
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "src/ui/streamlit_app.py",
        "--logger.level=error"
    ])
