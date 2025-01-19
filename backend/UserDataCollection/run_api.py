import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from user_data_api import app

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5002, debug=True)
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        print("Make sure all required environment variables are set and dependencies are installed.") 