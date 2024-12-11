import random
import datetime
from services.database import logs_collection

async def log_action(username: str, action: str):
    log_entry = {
        "username": username,
        "action": action,
        "timestamp": datetime.datetime.now().isoformat()
    }
    await logs_collection.insert_one(log_entry)
    
