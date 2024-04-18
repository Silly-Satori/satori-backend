from fastapi import FastAPI, Form, WebSocket, Request
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import asyncio
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
import pymongo
import os
from dotenv import load_dotenv
import datetime as Datetime
from functions import *
import json

from routers import auth, courses, user, payments

load_dotenv()


app = FastAPI()
version_info = "0.1b"

CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = os.environ["GOOGLE_REDIRECT_URI"]

class DataModel(BaseModel):
    session: str
    
FRONTEND_URL = os.environ.get("FRONTEND_URL")
origins = [
    "http://localhost:3000",
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    FRONTEND_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Set-Cookie"]
)
app.add_middleware(SessionMiddleware, secret_key= os.environ["SECRET_KEY"])

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(payments.router)
app.include_router(user.router)

# mongo = pymongo.MongoClient(os.environ["MONGO_URI"])


@app.get("/")
async def root():
    """Returns a simple message"""
    return {"message": "Satori's Backend API", "version": version_info}
        

@app.get("/version")
async def version():
    """Gets the version of the API"""
    return {"version": version_info}

@app.get("/data")
async def data(request: Request):
    return(
        [
            request.session,
        ]
    )
    
@app.post("/post")
async def post(request: Request, DataModel: DataModel):
    print(DataModel)
    request.session["mod"] = DataModel.session
    return "hello"

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <title>My Project - ReDoc</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <style>
        body {
            margin: 0;
            padding: 0;
        }
    </style>
    <style data-styled="" data-styled-version="4.4.1"></style>
</head>
<body>
    <div id="redoc-container"></div>
    <script src="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js"> </script>
    <script>
        var spec = %s;
        Redoc.init(spec, {}, document.getElementById("redoc-container"));
    </script>
</body>
</html>
"""
@app.get("/docs/{password}")
async def generate_docs(password: str):
    if password != os.environ["SECRET_KEY"]:
        return {"message": "Invalid password"}
    with open(f"docs.html", "w") as fd:
        # update the docs.html file on whenever a get request is made to the /docs endpoint with passwword
        print(HTML_TEMPLATE % json.dumps(app.openapi()), file=fd)
    
    return {"message": "Docs updated"}


