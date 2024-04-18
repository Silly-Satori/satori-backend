from fastapi import APIRouter, Depends, HTTPException
import pymongo
from functions.auth import TokenGenerator
import certifi

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

mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"), tlsCAFile= certifi.where())
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
            "required": ["sub", "courses", "reviews", "courses_created", "user_type"],
            "additionalProperties": True,
            "properties": {
                "sub": {
                    "bsonType": "string",
                    "description": "user's sub"
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

    db.command({"collMod": "user_data", "validator": validator,
               "validationLevel": "moderate"})

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
    """Get the user data from the database"""
    db = mongo_client["users"]
    collection = db["user_data"]
    user_data = collection.find_one({"sub": sub})
    if user_data:
        return user_data
    else:
        new_user = {
            "_id": sub,
            "sub": sub,
            "courses": [],
            "reviews": [],
            "courses_created": [],
            "user_type": "student"
        }
        collection.insert_one(new_user)
        return new_user


@router.get('/user_data/courses')
async def get_user_courses(token: str):
    """Get the courses the user has purchased"""
    # decode the jwt token
    sub = TokenGenerator.decode_jwt_token(token)["sub"]
    db = mongo_client["users"]
    # make a request to the /user_data endpoint to get the user data
    user_data = await get_user_data(sub)  # Add 'await' keyword here
    if user_data:
        return user_data["courses"]
    else:
        return []
    
async def add_user_course(sub: str, course_id: str):
    """Add a course to the user's list of purchased courses, no route"""
    db = mongo_client["users"]
    collection = db["user_data"]
    user_data:list = collection.find_one({"sub": sub})
    if user_data:
        user_data["courses"].append(course_id)
        collection.update_one({"sub": sub}, {"$set": user_data})
        return user_data
    else:
        return None


@router.post('/info')
async def get_user_info(request: Request):
    """Get the user info from the jwt token"""
    # read the token from the request body
    try:
        data = await request.json()
        token = data["token"]
        # decode the jwt token
        user_data = TokenGenerator.decode_jwt_token(token)
        return user_data
    except:
        raise HTTPException(status_code=400, detail="Invalid form data")
