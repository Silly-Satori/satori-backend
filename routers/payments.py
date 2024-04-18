
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import pymongo
import razorpay
from functions.auth import TokenGenerator
import time
import certifi
import hmac
import hashlib


from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

import os
import asyncio

from dotenv import load_dotenv
from .user import get_user_courses, add_user_course

load_dotenv()

router = APIRouter(
    prefix="/pay",
    tags=["Payments"],
    responses={
        404: {"description": "Not found @ /pay"},
        500: {"description": "Internal Server Error @ /pay"}
    }
)

mongo_client = pymongo.MongoClient(
    os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
db = mongo_client["payments"]
course_db = mongo_client["courses"]["courses"]

rpay_client = razorpay.Client(
    auth=(os.getenv("RPAY_KEY"), os.getenv("RPAY_SECRET")))


@router.get("/")
async def root():
    """Returns a simple message"""
    return {"message": "Payments API"}


@router.get("/create-test")
async def create_payment():
    """Create a test payment, for testing purposes
    Not to be used for front-end"""
    payment = rpay_client.order.create({
        "amount": 500,
        "currency": "INR",
        "receipt": "test_order"+str(int(time.time())),
        # "method": "upi",

        "notes": {
            "age": "24",
            "name": "test"
        }
    })

    return payment


@router.post("/purchase/{course_id}")
async def purchase_course(course_id: str, request: Request):
    """Purchase a course, given the course_id
    Returns a payment object, which can be used to show the payment modal in the front-end"""
    # request is a form data
    body: dict = {}
    try:
        body = await request.json()
    except:
        body = await request.form()
    token = body.get("token")
    user = TokenGenerator.decode_jwt_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Token")
    # Check if the course exists
    course = course_db.find_one({"_id": str(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    # Check if the user has already purchased the course
    # we make a get request to /user/user_data/courses
    user_courses = await get_user_courses(token)
    if course_id in user_courses:
        raise HTTPException(status_code=400, detail="Course already purchased")
    # Create a payment
    payment = rpay_client.order.create({
        "amount": course["price"] * 100,
        "currency": "INR",
        "receipt": "order_"+str(int(time.time())),
        "notes": {
            "course_id": course_id,
            "user_id": user["sub"]
        }
    })
    return payment

@router.post("/verify")
async def verify_payment(request: Request):
    """
    Callback function for verifying the payment
    Cryptographically verifies the payment by comparing the signature with our own digest
    If the payment is verified, the course is added to the user's account
    """
    body = {}
    try:
        body = await request.json()
    except:
        body = await request.form()
    orderCreationId = body.get("orderCreationId")
    razorpayPaymentId = body.get("razorpayPaymentId")
    razorpayOrderId = body.get("razorpayOrderId")
    razorpaySignature = body.get("razorpaySignature")
    notes: dict = body.get("notes")
    token = TokenGenerator.decode_jwt_token(body.get("token"))
    print(token)
    print(notes)

    try:
        # Creating our own digest
        # The format should be like this:
        # digest = hmac_sha256(orderCreationId + "|" + razorpayPaymentId, secret)
        secret = os.getenv("RPAY_SECRET")
        message = f"{orderCreationId}|{razorpayPaymentId}".encode("utf-8")
        digest = hmac.new(secret.encode("utf-8"), message,
                          hashlib.sha256).hexdigest()

        # Comparing our digest with the actual signature
        if digest != razorpaySignature:
            return JSONResponse({"msg": "Transaction not legit!"}, status_code=400)

        # THE PAYMENT IS LEGIT & VERIFIED
        # YOU CAN SAVE THE DETAILS IN YOUR DATABASE IF YOU WANT

        # get course id from notes
        course_id = notes.get("course_id")
        user_id = notes.get("user_id")

        await add_user_course(user_id, course_id)
        print("Course added to user")


        return {
            "msg": "success",
            "orderId": razorpayOrderId,
            "paymentId": razorpayPaymentId
        }
    except Exception as e:
        return JSONResponse(str(e), status_code=500)
