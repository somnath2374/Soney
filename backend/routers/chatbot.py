import logging
import os
from fastapi import APIRouter, HTTPException, Depends
from services.database import comments_collection, posts_collection, honeytraps_collection, users_collection
from utils.auth import get_current_user
from bson import ObjectId
from .log import log_action
from dotenv import load_dotenv
from groq import Groq

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
                return {"message": "Suspicious user detected", "is_genuine": False}
            else:
                return {"message": "User is genuine", "is_genuine": True}
        else:
            return {"message": "Not a honeytrap post", "is_genuine": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def generate_conversation(user_input, conversation_history=None):
    context = conversation_history or []
    messages = [
        {
            "role": "system",
            "content": "You are engaging in a natural conversation to evaluate user genuineness. Maintain context and ask relevant follow-up questions."
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
    Analyzes a conversation transcript to determine if the user is genuine.

    Args:
        conversation_transcript (str): The full conversation transcript.

    Returns:
        str: "yes" if the user is genuine, otherwise "no".
    """
    input_message = (
        f"Analyze the following conversation transcript to determine if the user is genuine:\n\n"
        f"{conversation_transcript}\n\n"
        f"Consider factors such as consistency, detail, relevance, and natural engagement. "
        f"Respond with 'yes' if the user is genuine, and 'no' if not."
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a conversation genuineness analyzer. Your task is to determine if a user is genuine based on their responses. "
                           "Assess the transcript for consistency (are their answers logical and aligned?), detail (do they provide specific, non-generic responses?), "
                           "relevance (do their replies stay on topic?), and natural engagement (do they contribute meaningfully to the conversation?). "
                           "Always respond with 'yes' if the user appears genuine and 'no' if they do not, followed by a one-sentence reason."
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

