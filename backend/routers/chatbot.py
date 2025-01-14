import logging
import os
from fastapi import APIRouter, HTTPException, Depends
from services.database import comments_collection, posts_collection, honeytraps_collection, users_collection, detected_collection
from utils.auth import get_current_user
from bson import ObjectId
from .log import log_action
from dotenv import load_dotenv
from groq import Groq
import random,datetime

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

GROOQ_API_KEY = os.getenv("GROOQ_API_KEY")  # Load the Grooq API key from the .env file

client = Groq(api_key=GROOQ_API_KEY)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_comment_suspicious(comment, post_title, post_content):
    """
    Determines if a comment is suspicious based on input data.

    Args:
        comment (str): The comment text.
        post_title (str): The title of the post.
        post_content (str): The content of the post.

    Returns:
        str: "yes" if the comment is suspicious, otherwise "no".
    """
    input_message = (
        f"User commented '{comment}' on a post titled '{post_title}' "
        f"with content '{post_content}'. Is this comment suspicious? Respond with 'yes' or 'no' only."
    )
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an comment suspicious analyser that determines if comments are suspicious. "
                            "Analyze the following comment for signs of suspicious activity. Consider factors such as excessive promotional language, presence of malicious links,Deviates from the topic of the post,Mimics a scam attempt (e.g., offers, requests for sensitive information) overly generic responses, or unusual patterns that deviate from normal user behavior."
                           "Always respond with 'yes' if the comment is suspicious or 'no' if not suspicious only."
            },
            {
                "role": "user",
                "content": input_message,
            }
        ],
        model="llama3-8b-8192",
    )

    # Extract the one-word response
    return chat_completion.choices[0].message.content.strip().lower()

async def check_comment(comment_id: str, user: dict = Depends(get_current_user)):
    try:
        comment = await comments_collection.find_one({"_id": ObjectId(comment_id)})
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        post = await posts_collection.find_one({"_id": ObjectId(comment["post_id"])})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        honeytrap = await honeytraps_collection.find_one({"username": post["author_id"]})
        if honeytrap:
            is_suspicious = is_comment_suspicious(comment["content"], post["title"], post["content"])
            print(f"Is suspicious: {is_suspicious}")
            if is_suspicious == "yes":
                await log_action(comment["author_id"], f"Suspicious comment on honeytrap post: {post['title']}")
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
                return {"message": "Suspicious user detected", "is_genuine": False}
            else:
                return {"message": "User is genuine", "is_genuine": True}
        else:
            return {"message": "Not a honeytrap post", "is_genuine": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def generate_conversation(user_input, conversation_history=None):
    """
    Generates a conversation response with the user to subtly detect suspicious behavior.
    
    Args:
        user_input (str): The user's latest input in the conversation.
        conversation_history (list, optional): A list of dictionaries containing the conversation history.
                                               Each dictionary should have keys 'is_user' (bool) and 'message' (str).
    
    Returns:
        str: The assistant's next response in the conversation.
    """
    context = conversation_history or []
    messages = [
        {
            "role": "system",
            "content": "You are engaging in a natural and conversational dialogue to interact with the user. "
                       "Maintain the flow of conversation and ask relevant follow-up questions to gather more details. "
                       "Be conversational and friendly, and avoid revealing any AI identity."
        }
    ]
    
    # Add conversation history
    for msg in context:
        messages.append({"role": "user" if msg["is_user"] else "assistant", "content": msg["message"]})
    
    messages.append({"role": "user", "content": user_input})
    
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama3-8b-8192",
    )
    
    return chat_completion.choices[0].message.content.strip()


def is_user_genuine(conversation_transcript):
    """
    Analyzes a conversation transcript to determine if the user is suspicious, a fraud, or a bot.

    Args:
        conversation_transcript (str): The full conversation transcript.

    Returns:
        str: "genuine" if the user appears genuine, "suspicious" if suspicious behavior is detected,
             "fraud" if fraudulent intent is identified, or "bot" if the user appears to be a bot.
    """
    input_message = (
        f"Analyze the following conversation transcript to determine if the user is suspicious, fraudulent, or a bot:\n\n"
        f"{conversation_transcript}\n\n"
        f"Consider the following criteria:\n"
        f"- Consistency: Are the responses logical and aligned with the context?\n"
        f"- Detail: Do they provide specific and meaningful details?\n"
        f"- Relevance: Do their replies stay on topic?\n"
        f"- Engagement: Is their tone and interaction style natural and human-like?\n"
        f"- Patterns: Do responses show repetitive, generic, or automated behavior?\n"
        f"- Red Flags: Do they exhibit signs of evasion, manipulation, or unusual language patterns?\n\n"
        f"Classify the user as one of the following:\n"
        f"1. 'genuine' if they are consistent, detailed, relevant, and naturally engaged.\n"
        f"2. 'suspicious' if their behavior raises mild concerns or inconsistencies.\n"
        f"3. 'fraud' if they exhibit clear signs of deceit or malicious intent.\n"
        f"4. 'bot' if their behavior appears automated or non-human.\n\n"
        f"Always respond with one word: 'genuine', 'suspicious', 'fraud', or 'bot'."
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a user behavior analyst. Your task is to classify users as 'genuine', 'suspicious', 'fraud', or 'bot' "
                           "based on their conversation transcripts. Assess consistency, detail, relevance, engagement, repetitive patterns, "
                           "and potential red flags in their responses. Provide a one-word classification only."
            },
            {
                "role": "user",
                "content": input_message,
            }
        ],
        model="llama3-8b-8192",
    )

    # Extract and return the one-word response
    return chat_completion.choices[0].message.content.strip().lower()

async def generate_realistic_username(purpose: str):
    prompt = f"""
    Generate a realistic username based on the given purpose for social media accounts.
    Purpose: {purpose}
    Requirements:
    - The username must be realistic, concise, and align with the given purpose.
    - The username should only consist of alphanumeric characters, underscores, or dots.
    - Return **only** the username, without any additional text, comments, or explanations.

    Example:
    Coolboy12
    """
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a username generator. Create realistic usernames that align with the given purpose, adhering strictly to the format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama3-8b-8192"
    )
    
    response = chat_completion.choices[0].message.content.strip()
    
    # Validate the response
    if not response.isalnum() and not all(c.isalnum() or c in "_." for c in response):
        # Fallback to a generated username if invalid
        response = purpose.replace(" ", "_").lower()
        if len(response) > 15:
            response = response[:15]  # Truncate to a reasonable length
        response = f"{response}_user"
    
    return response

async def generate_realistic_email(username: str):
    # Clean username to max 20 chars and remove special characters
    clean_username = ''.join(e for e in username if e.isalnum())[:20].lower()
    
    domains = ["example.com", "mail.com", "webmail.com", "domain.com"]
    email = f"{clean_username}@{random.choice(domains)}"
    
    return email

async def generate_enticing_post_content(purpose: str):
    prompt = f"""
    Generate a demo social media post based on the given purpose. 
    Follow these instructions strictly:
    - The title must be concise, engaging, and no longer than 50 characters.
    - The content must be clear, focused, and relevant to the purpose.
    - The response **must** follow this exact format, without additional text or deviation:
    
    TITLE: <brief engaging title>
    CONTENT: <detailed post content>
    
    Example:
    TITLE: Unlock Your Fitness Potential
    CONTENT: Discover easy tips to stay active and healthy every day. Learn more about improving your fitness journey and embracing a healthier lifestyle.
    
    Purpose: {purpose}
    """
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a professional social media content creator. Generate engaging posts that strictly follow the given format and align with the provided purpose."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama3-8b-8192"
    )
    response = chat_completion.choices[0].message.content.strip()
    
    # Enhanced parsing with length limits
    parts = response.split("\n")
    if len(parts)>=3:
        title = parts[1].replace("TITLE:", "").strip()[:50]
        content = parts[2].replace("CONTENT:", "").strip()
    else:
        title = parts[0].replace("TITLE:", "").strip()[:50]
        content = parts[1].replace("CONTENT:", "").strip()
    
    # Validate and adjust outputs
    if len(title) < 5:
        title = f"Learn About: {purpose}"
    if len(content) < 10:
        content = f"Exploring {purpose} concepts for better understanding."
        
    return title, content



async def generate_comment_content(post_title: str, post_content: str):
    prompt = f"""
    Generate a realistic, contextually relevant comment for a social media post.
    Post Title: '{post_title}'
    Post Content: '{post_content}'
    Requirements:
    - The comment should be concise, thoughtful, and relevant to the post's content.
    - Avoid generic responses like "Great post!" or "Nice!" unless highly contextually appropriate.
    - Return **only** the comment text without any additional text or formatting.
    """
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a professional comment generator creating contextually relevant and meaningful comments for posts."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama3-8b-8192"
    )
    
    response = chat_completion.choices[0].message.content.strip()
    
    # Validate the response
    if len(response) < 5 or response.lower() in {"great post!", "nice!", "interesting!", "cool!"}:
        # Generate a fallback comment if the response is too short or generic
        response = f"I really enjoyed reading about '{post_title}'. Your insights on '{post_content[:50]}...' are truly thought-provoking!"
    
    return response


