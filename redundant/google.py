import jwt
import requests
from time import time
import os

class Google:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_user(self, access_token):
        url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
        resp = requests.get(url, headers=headers)
        
        # obtain the refresh token from https://www.googleapis.com/oauth2/v4/token
        
        req = requests.post("https://www.googleapis.com/oauth2/v4/token", data={
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
        })
        
        print(req.json())
        
        print(resp.json())
        return resp.json()
    
    
    def get_google_tokens(self, auth_code):
        # Set up the data for the POST request
        data = {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://localhost:3000'  # Replace with your redirect URI
        }

        # Send the POST request to Google's token endpoint
        response = requests.post('https://oauth2.googleapis.com/token', data=data)

        # If the request was successful, return the tokens
        if response.status_code == 200:
            return response.json()

        # If the request was not successful, return the error
        return response.json()