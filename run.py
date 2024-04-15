import uvicorn
import os
import sys
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    
    python_path = str(sys.executable)
    print("Initializing...")
    print("Python version: " + sys.version)
    print("Python executable path: " + python_path)
    
    # change cwd to the directory of this file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Working directory: " + os.getcwd())
    
    # install dependencies
    print("Installing dependencies...")
    os.system(sys.executable + " -m pip install -r requirements.txt --quiet")
    print("All dependencies installed.")
    
    frontend = os.environ.get("FRONTEND_URL")
    print("Using frontend at", frontend)
    
    # start server
    print("Starting server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)