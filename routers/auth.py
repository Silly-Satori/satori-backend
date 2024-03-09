from fastapi import APIRouter, Depends, HTTPException

from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

import pymongo
import os
from dotenv import load_dotenv

from datetime import datetime

from functions.auth import TokenGenerator

load_dotenv()
mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = mongo_client["users"]
# check if the collection exists
if "users" not in db.list_collection_names():
    db.create_collection("users")

    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["name", "sub", "email"],
            "additionalProperties": True,
            "properties": {
                "name": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                },
                "sub": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                },
                "email": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                },
            }
        }
    }
    
    db.command({"collMod": "users", "validator": validator, "validationLevel": "moderate"})


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

config = Config('.env')  # read config from .env file
oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    },
    authorize_state= os.getenv("SECRET_KEY"),
)


@router.get('/login')
async def login(request: Request):
    # redirect to google/callback
    current_url = request.url
    print(current_url)
    redirect_uri = str(current_url).replace('login', 'google/callback')
    print("\n"*2)
    return await oauth.google.authorize_redirect(request, redirect_uri, access_type='offline', prompt = 'consent')


@router.get('/google/callback')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = token.get('userinfo', None)
    access_token = token.get('access_token', None)
    refesh_token = token.get('refresh_token', None)
    print(user)
    if user:
        user = dict(user)
        user = {
            key: user[key]
            for key in ["name",
                        "sub",
                        "email",
                        "email_verified",
                        "picture"]
        }

    # save the user to database
    # TODO: save the user to database
    # Generate session token
    session_token = TokenGenerator.generate_session_token()
    
    # test if database is connected or not
    try:
        print(mongo_client.server_info())
    except:
        restart_mongo_client()
        try:
            mongo_client.server_info()
        except:
            return HTTPException(status_code=500, detail="Database connection failed, please contact support@parthb.xyz")
    # save data to database
    db = mongo_client["users"]
    collection = db["users"]
    # check if user exists
    user_exists = collection.find_one({"email": user["email"]})
    timestamp = datetime.now().timestamp()
    user["access_token"] = access_token
    user["refresh_token"] = refesh_token
    user["last_login"] = timestamp
    # if user does not exist, create a new user
    if not user_exists:
        user["created_at"] = timestamp
        user["_id"] = user["sub"]
        # set _id to sub
        collection.insert_one(user)
        # remove _id from user
        user.pop("_id")
        user.pop("created_at")
    else:
        collection.update_one({"_id": user["sub"]}, {"$set": user}, upsert=True)
    
    # remove the access token and refresh token from the user
    user.pop("access_token")
    user.pop("refresh_token")
      
    # set the cookie with the session token
    resp = RedirectResponse(url=f'http://localhost:3000/auth/{session_token}')
    resp.set_cookie(key="user", value=user, samesite="lax", secure=True)

    return resp


@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')


def restart_mongo_client():
    global mongo_client
    mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"))
    return True
