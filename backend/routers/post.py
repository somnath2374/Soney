from fastapi import APIRouter, HTTPException, Depends, status, Body
from typing import List
from models.post import PostCreate, PostResponse
from models.comment import Comment, CommentCreate, CommentResponse
from models.user import UserResponse
from utils.auth import get_current_user
from services.database import posts_collection, comments_collection, honeytraps_collection
from pymongo import errors
from bson import ObjectId
from .log import log_action  # Import the log_action function
from .chatbot import check_comment
import datetime

router = APIRouter()

@router.post("/create", response_model=PostResponse)
async def create_post(post: PostCreate, user: UserResponse = Depends(get_current_user)):
    try:
        post_dict = post.model_dump()
        post_dict["author_id"] = user.username
        post_dict["created_at"] = datetime.datetime.now().isoformat()
        post_dict["updated_at"] = datetime.datetime.now().isoformat()
        post_dict["likes_count"] = 0
        post_dict["dislikes_count"] = 0
        post_dict["comments_count"] = 0
        post_dict["comments"] = []
        result = await posts_collection.insert_one(post_dict)
        return PostResponse(**post_dict, id=str(result.inserted_id))
    except errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts", response_model=List[PostResponse])
async def get_posts():
    try:
        posts = await posts_collection.find().to_list(100)
        post_responses = []
        for post in posts:
            comments = await comments_collection.find({"post_id": str(post["_id"])}).to_list(100)
            comment_responses = [
                Comment(
                    **{k: str(v) if isinstance(v, ObjectId) else v for k, v in comment.items()},
                    id=str(comment["_id"])
                ) 
                for comment in comments
            ]
            post_responses.append(PostResponse(
                id=str(post["_id"]),
                title=post["title"],
                author_id=post["author_id"],
                content=post["content"],
                hashtags=post["hashtags"],
                pictures=post.get("pictures", []),
                videos=post.get("videos", []),
                likes_count=post["likes_count"],
                dislikes_count=post["dislikes_count"],
                comments_count=post["comments_count"],
                comments=comment_responses
            ))
        return post_responses
    except errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/post/{post_id}", response_model=PostResponse)
async def get_post(post_id: str):
    try:
        post = await posts_collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        comments = await comments_collection.find({"post_id": post_id}).to_list(100)
        comment_responses = [Comment(**comment, id=str(comment["_id"])) for comment in comments]
        return PostResponse(
            id=str(post["_id"]),
            title=post["title"],
            author_id=post["author_id"],
            content=post["content"],
            hashtags=post["hashtags"],
            pictures=post.get("pictures", []),
            videos=post.get("videos", []),
            likes_count=post["likes_count"],
            dislikes_count=post["dislikes_count"],
            comments_count=post["comments_count"],
            comments=comment_responses
        )
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid post ID")
    except errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/user/{author_id}", response_model=List[PostResponse])
async def get_post(author_id):
    try:
        cursor = posts_collection.find({"author_id": author_id})
        posts = await cursor.to_list(100)
        post_responses = []
        for post in posts:
            comments = await comments_collection.find({"post_id": str(post["_id"])}).to_list(100)
            comment_responses = [Comment(**comment, id=str(comment["_id"])) for comment in comments]
            post_responses.append(PostResponse(
                id=str(post["_id"]),
                title=post["title"],
                author_id=post["author_id"],
                content=post["content"],
                hashtags=post["hashtags"],
                pictures=post.get("pictures", []),
                videos=post.get("videos", []),
                likes_count=post["likes_count"],
                dislikes_count=post["dislikes_count"],
                comments_count=post["comments_count"],
                comments=comment_responses
            ))
        return post_responses
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid post ID")
    except errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/like/{post_id}")
async def like_post(post_id: str, user: UserResponse = Depends(get_current_user)):
    try:
        post = await posts_collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        await posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$inc": {"likes_count": 1}}
        )

        # Check if the like is related to a honeytrap post
        honeytrap = await honeytraps_collection.find_one({"username": post["author_id"]})
        if honeytrap:
            await log_action(user.username, f"Liked honeytrap post: {post['title']}")

        return {"message": "Post liked"}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dislike/{post_id}")
async def dislike_post(post_id: str, user: UserResponse = Depends(get_current_user)):
    try:
        post = await posts_collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        await posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$inc": {"dislikes_count": 1}}
        )

        # Check if the dislike is related to a honeytrap post
        honeytrap = await honeytraps_collection.find_one({"username": post["author_id"]})
        if honeytrap:
            await log_action(user.username, f"Disliked honeytrap post: {post['title']}")

        return {"message": "Post disliked"}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/comment/{post_id}")
async def comment_post(post_id: str, comment: str = Body(..., embed=True), user: UserResponse = Depends(get_current_user)):
    try:
        post = await posts_collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        comment_dict = {
            "post_id": post_id,
            "author_id": user.username,
            "content": comment,
            "created_at": datetime.datetime.now().isoformat()
        }
        result = await comments_collection.insert_one(comment_dict)
        await posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$inc": {"comments_count": 1},
             "$push": {"comments": str(result.inserted_id)}}
        )

        # Check if the comment is related to a honeytrap post
        honeytrap = await honeytraps_collection.find_one({"username": post["author_id"]})
        if honeytrap:
            await log_action(user.username, f"Commented {comment} on honeytrap post: {post['title']}")
            await check_comment(str(result.inserted_id), user.username)
        return {"message": "Comment added", "comment_id": str(result.inserted_id)}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))