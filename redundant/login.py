import pymongo
import os
import re

# Login and signup functions

class Login:
    def __init__(self):
        self.mongo = pymongo.MongoClient(os.getenv("MONGO_URI"))
        self.db = self.mongo["satori_users"]
    
    def create_user(self, email, username, password):
        # Creates a user
        # check if user exists
        users = self.db["users"]
        if users.find_one({"email": email}):
            return {"error": "User already exists"}
        
    def check_email_and_username(self, email, username):
        users = self.db["users"]
        errors = {
            "email": False,
            "username": False
        }
        
        if email is None:
            errors["email"] = "Email is required"
        else:
            if re.fullmatch(r"r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'", email):
                if users.find_one({"email": email}):
                    errors["email"] = "Email already exists"
            else:
                errors["email"] = "Invalid email"
        
        if username is None:
            errors["username"] = "Username is required"
        else:
            if re.fullmatch(r"^[a-zA-Z][a-zA-Z0-9_]{4,}$", username):
                if users.find_one({"username": username}):
                    errors["username"] = "Username already exists"
            else:
                errors["username"] = "Invalid username"
                
        if errors["email"] or errors["username"]:
            return {
                "valid": False,
                "errors": errors
            }
        
        return {
            "valid": True,
            "errors": None
        }
        