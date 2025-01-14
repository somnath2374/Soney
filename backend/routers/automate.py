import random
import datetime
import logging
import asyncio
from services.database import honeytraps_collection, users_collection, posts_collection, comments_collection
from .log import log_action
import string
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from routers.analyser import analyze_interactions
from routers.chatbot import generate_enticing_post_content,generate_comment_content

scheduler = AsyncIOScheduler()
scheduler.start()

async def create_enticing_post(username: str):
    honeytrap = await honeytraps_collection.find_one({"username": username})
    purpose = honeytrap["purpose"]
    title, content = await generate_enticing_post_content(purpose)
    post_data = {
        "title": title,
        "content": content,
        "author_id": username,
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat(),
        "likes_count": 0,
        "dislikes_count": 0,
        "comments_count": 0,
        "comments": [],
        "hashtags": [],
        "pictures": [],
        "videos": []
    }
    await posts_collection.insert_one(post_data)
    await log_action(username, f"Created post: {title}")

async def get_random_honeytrap(exclude_username: str) -> str:
    honeytraps = await honeytraps_collection.find({"username": {"$ne": exclude_username}}).to_list(length=100)
    if not honeytraps:
        return None
    return random.choice(honeytraps)["username"]

async def send_friend_request(sender_username: str):
    receiver_username = await get_random_honeytrap(sender_username)
    if receiver_username:
        receiver = await users_collection.find_one({"username": receiver_username})
        if sender_username not in receiver["friend_requests"] and sender_username not in receiver["friends"]:
            await users_collection.update_one(
                {"username": receiver_username},
                {"$push": {"friend_requests": sender_username}}
            )
            await honeytraps_collection.update_one(
                {"username": receiver_username},
                {"$push": {"friend_requests": sender_username}}
            )
            await log_action(sender_username, f"Sent friend request to {receiver_username}")

            # Accept the friend request after a delay
            await asyncio.sleep(20)  # Delay of 20 seconds before accepting the friend request
            await accept_friend_request(receiver_username, sender_username)

async def accept_friend_request(username: str, friend_username: str):
    user = await users_collection.find_one({"username": username})
    if user and friend_username in user["friend_requests"]:
        await users_collection.update_one(
            {"username": username},
            {"$pull": {"friend_requests": friend_username},
             "$addToSet": {"friends": friend_username}}
        )
        await users_collection.update_one(
            {"username": friend_username},
            {"$addToSet": {"friends": username}}
        )
        await honeytraps_collection.update_one(
            {"username": username},
            {"$pull": {"friend_requests": friend_username},
             "$addToSet": {"friends": friend_username}}
        )
        await honeytraps_collection.update_one(
            {"username": friend_username},
            {"$addToSet": {"friends": username}}
        )
        await log_action(username, f"Accepted friend request from {friend_username}")

async def interact_with_posts(username: str):
    posts = await posts_collection.find({"author_id": {"$ne": username}}).to_list(length=100)
    if posts:
        post = random.choice(posts)
        action = random.choice(["like", "dislike", "comment"])
        if action == "like":
            await posts_collection.update_one(
                {"_id": post["_id"]},
                {"$inc": {"likes_count": 1}}
            )
            await log_action(username, f"Liked post {post['title']}")
        elif action == "dislike":
            await posts_collection.update_one(
                {"_id": post["_id"]},
                {"$inc": {"dislikes_count": 1}}
            )
            await log_action(username, f"Disliked post {post['title']}")
        elif action == "comment":
            comment_content = await generate_comment_content(post["title"],post["content"])
            comment_data = {
                "post_id": post["_id"],
                "author_id": username,
                "content": comment_content,
                "created_at": datetime.datetime.now().isoformat(),
                "comments": []
            }
            result = await comments_collection.insert_one(comment_data)
            await posts_collection.update_one(
                {"_id": post["_id"]},
                {"$inc": {"comments_count": 1},
                 "$push": {"comments": str(result.inserted_id)}}
            )
            await log_action(username, f"Commented on post {post['title']}: {comment_content}")

def schedule_post_creation(username: str):
    for i in range(5):  # Schedule 5 posts
        delay = random.randint(1, 2)  # Delay between 1 and 2 minutes
        scheduler.add_job(create_enticing_post, 'date', run_date=datetime.datetime.now() + datetime.timedelta(minutes=delay), args=[username], misfire_grace_time=60)

def schedule_friend_requests(username: str):
    scheduler.add_job(send_friend_request, 'interval', minutes=1, args=[username], misfire_grace_time=60)

def schedule_interactions(username: str):
    scheduler.add_job(interact_with_posts, 'interval', minutes=2, args=[username], misfire_grace_time=60)

def schedule_analysis():
    scheduler.add_job(analyze_interactions, 'interval', minutes=3, misfire_grace_time=60)
