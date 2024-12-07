# analyser.py
import datetime
import logging
from services.database import logs_collection

logging.basicConfig(level=logging.INFO)

# High-Frequency Interactors
async def detect_high_frequency_interactors():
    logs = await logs_collection.find().to_list(length=1000)
    interaction_counts = {}
    suspicious_users = set()
    for log in logs:
        username = log["username"]
        timestamp = datetime.datetime.fromisoformat(log["timestamp"])
        if username not in interaction_counts:
            interaction_counts[username] = []
        interaction_counts[username].append(timestamp)
    
    for username, timestamps in interaction_counts.items():
        timestamps.sort()
        for i in range(len(timestamps) - 10):
            if (timestamps[i + 10] - timestamps[i]).total_seconds() < 60:  # 10 interactions in 1 minute
                suspicious_users.add(username)
                break
    
    for user in suspicious_users:
        logging.warning(f"High-frequency interaction detected for user: {user}")

# Content Analysis
async def detect_spammy_content():
    logs = await logs_collection.find({"action": {"$regex": "commented"}}).to_list(length=1000)
    spammy_patterns = ["http", "www", "click here", "buy now", "free", "!!!", "###"]
    suspicious_users = set()
    for log in logs:
        username = log["username"]
        action = log["action"]
        if any(pattern in action.lower() for pattern in spammy_patterns):
            suspicious_users.add(username)
    
    for user in suspicious_users:
        logging.warning(f"Spammy content detected for user: {user}")

# Time-Based Patterns
async def detect_time_based_patterns():
    logs = await logs_collection.find().to_list(length=1000)
    interaction_times = {}
    suspicious_users = set()
    for log in logs:
        username = log["username"]
        timestamp = datetime.datetime.fromisoformat(log["timestamp"]).time()
        if username not in interaction_times:
            interaction_times[username] = []
        interaction_times[username].append(timestamp)
    
    for username, times in interaction_times.items():
        times.sort()
        for i in range(len(times) - 10):
            if (datetime.datetime.combine(datetime.date.today(), times[i + 10]) - datetime.datetime.combine(datetime.date.today(), times[i])).total_seconds() < 60:  # 10 interactions in 1 minute
                suspicious_users.add(username)
                break
    
    for user in suspicious_users:
        logging.warning(f"Time-based interaction pattern detected for user: {user}")

# Schedule Analysis
async def analyze_interactions():
    await detect_high_frequency_interactors()
    await detect_spammy_content()
    await detect_time_based_patterns()