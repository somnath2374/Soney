# analyser.py
import datetime
import logging
from services.database import logs_collection, detected_collection

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
        existing_record = await detected_collection.find_one({"username": user})
        if existing_record:
            if "High-frequency interaction" not in existing_record["reasons"]:
                await detected_collection.update_one(
                    {"username": user},
                    {"$push": {"reasons": "High-frequency interaction"}}
                )
        else:
            await detected_collection.insert_one({
                "username": user,
                "reasons": ["High-frequency interaction"],
                "timestamp": datetime.datetime.now().isoformat()
            })

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
        existing_record = await detected_collection.find_one({"username": user})
        if existing_record:
            if "Spammy content" not in existing_record["reasons"]:
                await detected_collection.update_one(
                    {"username": user},
                    {"$push": {"reasons": "Spammy content"}}
                )
        else:
            await detected_collection.insert_one({
                "username": user,
                "reasons": ["Spammy content"],
                "timestamp": datetime.datetime.now().isoformat()
            })

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
        existing_record = await detected_collection.find_one({"username": user})
        if existing_record:
            if "Time-based interaction pattern" not in existing_record["reasons"]:
                await detected_collection.update_one(
                    {"username": user},
                    {"$push": {"reasons": "Time-based interaction pattern"}}
                )
        else:
            await detected_collection.insert_one({
                "username": user,
                "reasons": ["Time-based interaction pattern"],
                "timestamp": datetime.datetime.now().isoformat()
            })

# Schedule Analysis
async def analyze_interactions():
    await detect_high_frequency_interactors()
    await detect_spammy_content()
    await detect_time_based_patterns()