"""
This file contains the routes various routes for the courses. 
Includes fettching all courses, fetching a single course, fetching a course's content after checking if the user is enrolled in the course 
TBD
"""

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

from .user import get_user_courses


router = APIRouter(
    prefix="/courses",
    tags=["Courses"],
    responses={
        404: {"description": "Not found @ /courses"},
        500: {"description": "Internal Server Error @ /courses"}
    },
    
)

mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"), tlsCAFile= certifi.where())
db = mongo_client["courses"]
# check if the collection exists and create it if it doesn't
if "courses" not in db.list_collection_names():
    db.create_collection("courses")

    # create a validator for the collection
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["courseId", "name", "description", "price", "content", "rating", "reviews", "author", "category", "difficulty", "language"],
            "additionalProperties": True,
            "properties": {
                "courseId": {
                    "bsonType": "string",
                    "description": "ID of the course"
                },
                "name": {
                    "bsonType": "string",
                    "description": "Name of the course"
                },
                "description": {
                    "bsonType": "string",
                    "description": "Description of the course"
                },
                "price": {
                    "bsonType": "int",
                    "description": "Price of the course"
                },
                "content": {
                    "bsonType": "string",
                    "description": "Content of the course"
                },
                "rating": {
                    "bsonType": "double",
                    "description": "Rating of the course"
                },
                "reviews": {
                    "bsonType": "array",
                    "description": "Reviews of the course"
                },
                "author": {
                    "bsonType": "string",
                    "description": "Author of the course, _id of the author"
                },
                "category": {
                    "bsonType": "string",
                    "description": "Category of the course, like 'Web Development', 'Data Science', etc."
                },
                "difficulty": {
                    "bsonType": "string",
                    "description": "Difficulty of the course, like 'Beginner', 'Intermediate', 'Advanced'"
                },
                "language": {
                    "bsonType": "string",
                    "description": "Language of the course, like 'English', 'Hindi', etc."
                }
            }
        }
    }
    
    try:
        # add the validator to the collection
        db.command({"collMod": "courses", "validator": validator, "validationLevel": "moderate"})
    except:
        db.drop_collection("courses")
        raise Exception("Failed to create the collection 'courses' with the validator")

if "course_content" not in db.list_collection_names():
    db.create_collection("course_content")

    # create a validator for the collection
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["courseId", "videos", "resources", "quizzes", "other"],
            "additionalProperties": True,
            "properties": {
                "courseId": {
                    "bsonType": "string",
                    "description": "ID of the course"
                },
                "videos": {
                    "bsonType": "array",
                    "description": "List of video links"
                },
                "resources": {
                    "bsonType": "array",
                    "description": "List of resources"
                },
                "quizzes": {
                    "bsonType": "array",
                    "description": "List of quizzes"
                },
                "other": {
                    "bsonType": "array",
                    "description": "List of other resources"
                }
            }
        }
    }

    try:
        db.command({"collMod": "course_content", "validator": validator, "validationLevel": "moderate"})
    except:
        db.drop_collection("course_content")
        raise Exception("Failed to create the collection 'course_content' with the validator")


@router.get("/")
async def read_root():
    """Default route for the courses router, nothing special here, unused"""
    return {"message": "Courses"}

@router.get("/fetch/{start}")
async def fetch_courses(start: int, restart_count: int = 0):
    """
    Fetches all courses from the database in chunks of 15
    """
    
    try:
        db = mongo_client["courses"]
        collection = db["courses"]
        courses = collection.find().skip(start).limit(15)
        courses = list(courses)
        return courses
    except:
        if restart_count == 0:
            restart_mongo_client()
            await asyncio.sleep(1)
            return await fetch_courses(start, 1)
        else:
            return HTTPException(status_code=500, detail="Internal Server Error")
        
@router.get("/fetch/purchased/{token}")
async def fetch_purchased_courses(token: str, restart_count: int = 0):
    """
    Fetches all courses that the user has purchased
    """
    if restart_count > 3:
        return HTTPException(status_code=500, detail="Internal Server Error")
    try:
        token = TokenGenerator.decode_jwt_token(token)
        if token == "invalid_sign" or token == "decode_error":
            return HTTPException(status_code=401, detail="Unauthorized")
        db = mongo_client["courses"]
        return {
            "message": "To be implemented",
            "data": token
        }
    except:
        restart_mongo_client()
        await asyncio.sleep(1)
        return await fetch_purchased_courses(token, 1)
        

@router.get("/fetch_id/{course_id}")
async def fetch_course(course_id: str, restart_count: int = 0):
    """
    Fetches a single course from the database
    """
    try:
        db = mongo_client["courses"]
        collection = db["courses"]
        course = collection.find_one({"_id": course_id})
        return course
    except:
        restart_mongo_client()
        await asyncio.sleep(1)
        return await fetch_course(course_id, 1)
    

@router.post("/get_content/{course_id}")
async def get_course_content(request: Request, course_id: str):
    """
    Fetches the content of a course after checking if the user is enrolled in the course
    """
    data:dict
    try:
        data = await request.json()
    except:
        data = await request.form()


    token = data.get("token")
    if token is None:
        return HTTPException(status_code=400, detail="Invalid form data")
    user  = TokenGenerator.decode_jwt_token(token)
    if user == "invalid_sign" or user == "decode_error":
        return HTTPException(status_code=401, detail="Unauthorized")
    
    # get user purchased courses
    user_courses = await get_user_courses(token)
    print(user_courses)

    if course_id not in user_courses:
        return HTTPException(status_code=401, detail="Unauthorized")
    
    course_db = mongo_client["courses"]["courses"]
    content_db = mongo_client["courses"]["course_content"]
    course = course_db.find_one({"_id": course_id})
    content = content_db.find_one({"_id": course_id})
    if content is None and course is not None:
        # create a new content document
        content = {
            "_id": course_id,
            "videos": [],
            "resources": [],
            "quizzes": [],
            "other": []
        }
        content_db.insert_one(content)
    return content
    
    
# temporary function for course creation
@router.post("/create/{password}")
async def create_course(course: dict, password: str):
    """
    Create a new course
    """
    if password != os.getenv("SECRET_KEY"):
        return HTTPException(status_code=401, detail="Unauthorized")
    db = mongo_client["courses"]
    collection = db["courses"]
    course_id = collection.insert_one(course)
    return {"_id": str(course_id.inserted_id)}

# Course creation route
@router.post("/new")
async def create_course(data: dict, token: str):
    """ _description_
    Create a new course with user authentication

    Args:
    data (dict): Course data
    token (str): User token
    """
    token = TokenGenerator.decode_jwt_token(token)
    if token == "invalid_sign" or token == "decode_error":
        return HTTPException(status_code=401, detail="Unauthorized")
    
    # to be implemented
    

def restart_mongo_client():
    global mongo_client
    mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"), tlsCAFile= certifi.where())
    

