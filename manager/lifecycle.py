"""
Bot lifecycle management - start/stop/restart bots
"""
import subprocess
import signal
from pathlib import Path
from typing import Dict, Optional
from manager import db

class BotSupervisor:
    def __init__(self):
        self.processes: Dict[int, subprocess.Popen] = {}
    
    def start_bot(self, bot_id: int) -> bool:
        """Start a bot process"""
        bot = db.get_bot(bot_id)
        if not bot:
            return False
        
        if bot_id in self.processes:
            return False  # Already running
        
        bot_path = Path(bot['path'])
        if not bot_path.exists():
            return False
        
        try:
            proc = subprocess.Popen(
                ['python3', str(bot_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=bot_path.parent
            )
            self.processes[bot_id] = proc
            db.update_bot_status(bot_id, 'running', heartbeat=True)
            return True
        except Exception as e:
            print(f"Failed to start bot {bot_id}: {e}")
            return False
    
    def stop_bot(self, bot_id: int) -> bool:
        """Stop a bot process"""
        if bot_id not in self.processes:
            return False
        
        proc = self.processes[bot_id]
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=10)
        del self.processes[bot_id]
        db.update_bot_status(bot_id, 'stopped')
        return True
    
    def restart_bot(self, bot_id: int) -> bool:
        """Restart a bot"""
        self.stop_bot(bot_id)
        return self.start_bot(bot_id)
    
    def get_status(self, bot_id: int) -> str:
        """Get runtime status"""
        if bot_id in self.processes:
            proc = self.processes[bot_id]
            if proc.poll() is None:
                return 'running'
            else:
                del self.processes[bot_id]
                db.update_bot_status(bot_id, 'crashed')
                return 'crashed'
        return 'stopped'
    
    def stop_all(self):
        """Stop all bots"""
        for bot_id in list(self.processes.keys()):
            self.stop_bot(bot_id)

supervisor = BotSupervisor()
