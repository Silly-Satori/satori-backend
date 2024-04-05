from fastapi import APIRouter, Depends, HTTPException
import pymongo
from functions.auth import TokenGenerator

from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

import os
import asyncio

router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={
        404: {"description": "Not found @ /user"},
        500: {"description": "Internal Server Error @ /user"}
    }
)

mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = mongo_client["users"]

""" 
User data collection:
    - sub (str): user's sub
    - _id (str): user's id, same as sub
    - name (str): user's name
    - email (str): user's email
    - courses (list): list of courses the user has purchased
    - reviews (list): list of reviews the user has made
    - courses_created (list): list of courses the user has created
    - user_type (str): user's type (student, teacher, admin)
"""

# check if the user_data collection exists and create it if it doesn't
if "user_data" not in db.list_collection_names():
    db.create_collection("user_data")

    # create a validator for the collection
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["sub", "name", "email", "courses", "reviews", "courses_created", "user_type"],
            "additionalProperties": True,
            "properties": {
                "sub": {
                    "bsonType": "string",
                    "description": "user's sub"
                },
                "name": {
                    "bsonType": "string",
                    "description": "user's name"
                },
                "email": {
                    "bsonType": "string",
                    "description": "user's email"
                },
                "courses": {
                    "bsonType": "array",
                    "description": "list of courses the user has purchased"
                },
                "reviews": {
                    "bsonType": "array",
                    "description": "list of reviews the user has made"
                },
                "courses_created": {
                    "bsonType": "array",
                    "description": "list of courses the user has created"
                },
                "user_type": {
                    "bsonType": "string",
                    "description": "user's type (student, teacher, admin)"
                }
            }
        }
    }
        
    db.command({"collMod": "user_data", "validator": validator, "validationLevel": "moderate"})
        
router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={
        404: {"description": "Not found @ /user"},
        500: {"description": "Internal Server Error @ /user"}
    }
)

@router.get('/user_data')
async def get_user_data(sub: str):
    db = mongo_client["users"]
    collection = db["user_data"]
    user_data = collection.find_one({"sub": sub})
    if user_data:
        return user_data
    else:
        return {"error": "User not found"}
    
@router.post('/info')
async def get_user_info(request: Request):
    # read the token from the request body
    try:
        data = await request.json()
        token = data["token"]
        # decode the jwt token 
        user_data = TokenGenerator.decode_jwt_token(token)
        return user_data
    except:
        raise HTTPException(status_code=400, detail="Invalid form data")
    
    
