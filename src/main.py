import os
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from prometheus_client import make_asgi_app

class LogMessage(BaseModel):
    message: str

app = FastAPI()

# Directory to store the log file
LOG_DIR = "/data"
LOG_FILE = os.path.join(LOG_DIR, "logfile.txt")

# Ensure the directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Global variable to track number of calls to the API
response_count = 0

# Add prometheus asgi middleware to route /metrics requests
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/")
async def read_root():
    global response_count  # Declare response_count as global
    response_count += 1
    return {"Hello": "World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    global response_count  # Declare response_count as global
    response_count += 1
    return {"item_id": item_id, "desc": f"This is where description of item {item_id} should be"}

@app.get("/stats")
async def get_stats():
    global response_count  # Declare response_count as global
    return {"Number of responses": response_count}

@app.post("/log")
async def log_text(log_message: LogMessage):
    with open(LOG_FILE, "a") as f:
        f.write(f"{str(datetime.now())} - {log_message.message}\n")


    return {"Message": "Log added"}

@app.get("/log")
async def get_logs():
    if os.path.exists(LOG_FILE):
        logs = []
        with open(LOG_FILE, "r") as f:
            for line in f:
                log_parts = line.split(" - ", 1)
                if len(log_parts) == 2:
                    logs.append({"time": log_parts[0], "message": log_parts[1]})
        
        return {"Logs": logs}
    
    return {"Message": "No logs to show"}

@app.get("/error")
async def trigger_error():
    # This will raise an exception, effectively "crashing" the app
    os._exit(1)
