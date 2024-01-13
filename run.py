import uvicorn
import os
import sys

if __name__ == "__main__":
    print("Initializing...")
    print("Python version: " + sys.version)
    
    # change cwd to the directory of this file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Working directory: " + os.getcwd())
    
    # install dependencies
    print("Installing dependencies...")
    os.system("pip install -r requirements.txt --quiet")
    print("All dependencies installed.")
    
    # start server
    print("Starting server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)