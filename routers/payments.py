
from fastapi import APIRouter, Depends, HTTPException
import pymongo
import razorpay
from functions.auth import TokenGenerator
import time


from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

import os
import asyncio

from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/pay",
    tags=["Payments"],
    responses={
        404: {"description": "Not found @ /pay"},
        500: {"description": "Internal Server Error @ /pay"}
    }
)

mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = mongo_client["payments"]

rpay_client = razorpay.Client(auth=(os.getenv("RPAY_KEY"), os.getenv("RPAY_SECRET")))

@router.get("/")
async def root():
    """Returns a simple message"""
    return {"message": "Payments API"}

@router.get("/create-test")
async def create_payment():
    payment = rpay_client.order.create({
        "amount": 500,
        "currency": "INR",
        "receipt": "test_order"+str(int(time.time())),
        "method": "upi",
        "notes": {
            "age": "24",
            "name": "test"
        }
    })
    
    return payment