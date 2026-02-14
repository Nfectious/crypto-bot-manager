"""
FastAPI web interface for bot management
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import List, Dict, Any
from manager import db
from manager.lifecycle import supervisor
from manager.logging import read_bot_trades

app = FastAPI(title="Crypto Bot Manager")

# Serve static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def index():
    """Serve dashboard"""
    dashboard_path = static_dir / "dashboard.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    return {"message": "Dashboard not found"}

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok"}

@app.get("/api/bots")
async def list_all_bots() -> List[Dict[str, Any]]:
    """List all bots with runtime status"""
    bots = db.list_bots()
    for bot in bots:
        bot['runtime_status'] = supervisor.get_status(bot['id'])
    return bots

@app.get("/api/bots/{bot_id}")
async def get_bot_details(bot_id: int) -> Dict[str, Any]:
    """Get specific bot details"""
    bot = db.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    bot['runtime_status'] = supervisor.get_status(bot_id)
    return bot

@app.get("/api/bots/{bot_id}/trades")
async def get_bot_trades(bot_id: int, limit: int = 100) -> Dict[str, Any]:
    """Get trade history from both DB and CSV"""
    bot = db.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
db_trades = db.list_trades(bot_id, limit)
    csv_trades = read_bot_trades(bot['name'], limit=limit)
    
    return {
        "bot_id": bot_id,
        "bot_name": bot['name'],
        "db_trades": db_trades,
        "csv_trades": csv_trades
    }

@app.post("/api/bots/{bot_id}/start")
async def start_bot_endpoint(bot_id: int):
    """Start a bot"""
    success = supervisor.start_bot(bot_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to start bot")
    return {"status": "started", "bot_id": bot_id}

@app.post("/api/bots/{bot_id}/stop")
async def stop_bot_endpoint(bot_id: int):
    """Stop a bot"""
    success = supervisor.stop_bot(bot_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to stop bot")
    return {"status": "stopped", "bot_id": bot_id}

@app.post("/api/bots/{bot_id}/restart")
async def restart_bot_endpoint(bot_id: int):
    """Restart a bot"""
    success = supervisor.restart_bot(bot_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to restart bot")
    return {"status": "restarted", "bot_id": bot_id}

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    db.create_tables()

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    supervisor.stop_all()