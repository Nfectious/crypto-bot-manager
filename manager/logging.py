"""
CSV logging for trade history
"""
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict

LOGS_DIR = Path("repo/data/logs")

def log_trade_csv(bot_name: str, side: str, pair: str, price: float, amount: float, fee: float = 0):
    """Log trade to CSV file"""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = LOGS_DIR / f"{bot_name}_trades.csv"
    
    file_exists = csv_path.exists()
    with open(csv_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'side', 'pair', 'price', 'amount', 'fee'])
        writer.writerow([datetime.now().isoformat(), side, pair, price, amount, fee])

def read_bot_trades(bot_name: str, limit: int = 100) -> List[Dict]:
    """Read trades from CSV"""
    csv_path = LOGS_DIR / f"{bot_name}_trades.csv"
    if not csv_path.exists():
        return []
    
    trades = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            trades.append(row)
    
    return trades[-limit:]
