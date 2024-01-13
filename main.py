from fastapi import FastAPI, Form, WebSocket
import asyncio
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
import pymongo
import os
from dotenv import load_dotenv
import datetime as Datetime

load_dotenv()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mongo = pymongo.MongoClient(os.environ["MONGO_URI"])


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/version")
async def version():
    return {"version": "0.1b"}


