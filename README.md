# Crypto Bot Manager

Bot lifecycle management system with web dashboard.

## Setup

```bash
pip install -r requirements.txt
python run_manager.py
```

Visit: http://localhost:8000

## Register a bot

```python
from manager.db import seed_bot
seed_bot("bot1", "path/to/bot.py")
```
