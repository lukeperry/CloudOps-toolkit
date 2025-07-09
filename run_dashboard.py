#!/usr/bin/env python3
"""
Main entry point for CloudOps Toolkit Dashboard
This script properly sets up the Python path and runs the Streamlit app.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now run the dashboard from the root directory
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import sys
    
    # Set up the dashboard file path
    dashboard_file = project_root / "app" / "dashboard.py"
    
    # Set up streamlit arguments
    sys.argv = ["streamlit", "run", str(dashboard_file)]
    
    # Run streamlit
    stcli.main()
