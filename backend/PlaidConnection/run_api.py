import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from plaid_api import app
    print("Starting Plaid API server on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
except Exception as e:
    print(f"Error starting server: {str(e)}")
    print("Make sure all required environment variables are set and dependencies are installed.")
    sys.exit(1) 