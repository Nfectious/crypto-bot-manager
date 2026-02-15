"""
Entrypoint to run the bot manager API
"""
import uvicorn
from manager.db import create_tables

if __name__ == "__main__":
    create_tables()
    uvicorn.run("manager.api:app", host="0.0.0.0", port=8000, reload=True)
