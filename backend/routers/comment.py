from fastapi import APIRouter, HTTPException, Depends, status
from models.comment import CommentCreate, CommentResponse
from utils.auth import get_current_user
from services.database import comments_collection, posts_collection, honeytraps_collection
from pymongo.errors import PyMongoError
from bson import ObjectId
from .log import log_action  # Import the log_action function
from .chatbot import check_comment  # Import the check_comment function

router = APIRouter()

@router.post("/", response_model=CommentResponse)
async def create_comment(comment: CommentCreate, user: dict = Depends(get_current_user)):
    try:
        comment_dict = comment.model_dump()
        comment_dict["author_id"] = user["username"]
        result = await comments_collection.insert_one(comment_dict)

        # Check if the comment is related to a honeytrap post
        post = await posts_collection.find_one({"_id": ObjectId(comment_dict["post_id"])})
        if post:
            honeytrap = await honeytraps_collection.find_one({"username": post["author_id"]})
            if honeytrap:
                await log_action(user["username"], f"Commented {comment_dict['content']} on honeytrap post: {post['title']}")
                await check_comment(str(result.inserted_id), user)
        return CommentResponse(**comment_dict, id=str(result.inserted_id))
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: str):
    try:
        comment = await comments_collection.find_one({"_id": ObjectId(comment_id)})
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        return CommentResponse(**comment, id=str(comment["_id"]))
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{comment_id}", response_model=dict)
async def delete_comment(comment_id: str, user: dict = Depends(get_current_user)):
    try:
        comment = await comments_collection.find_one({"_id": ObjectId(comment_id)})
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        if comment["author_id"] != user["username"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this comment")
        await comments_collection.delete_one({"_id": ObjectId(comment_id)})
        return {"message": "Comment deleted successfully"}
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
