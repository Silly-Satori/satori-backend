"""
This file contains the routes various routes for the courses. 
Includes fettching all courses, fetching a single course, fetching a course's content after checking if the user is enrolled in the course 
TBD
"""

from fastapi import APIRouter, Depends, HTTPException
import pymongo

from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

import os
import asyncio

router = APIRouter(
    prefix="/courses",
    tags=["Courses"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal Server Error"}
    }
)

mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"))


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
    

def restart_mongo_client():
    global mongo_client
    mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"))