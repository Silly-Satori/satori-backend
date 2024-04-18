# Backend for Satori

This is the backend for Satori, a web application that allows to publish and share courses, and learn from them as well. 

## Installation

1. Clone the repository
2. Make sure you have Python 3.8+ installed. If not, you can download it [here](https://www.python.org/downloads/)
3. You simply need to have uvicorn (server) installed. You can install it by running the following command:
```bash
pip install uvicorn[srv]
```
4. Set up the environment variables by creating a `.env` file in the root directory of the project. The file should contain the following variables:
```bash
GOOGLE_CLIENT_ID = Your_Google_Client_ID from Google Cloud Console
GOOGLE_CLIENT_SECRET = Your_Google_Client_Secret from Google Cloud Console
GOOGLE_REDIRECT_URI = http://localhost:8000/auth/google/callback # This is the default redirect URI for the Google OAuth2.0, replace it with your own if you host the server on a different port.

FRONTEND_URL = http://localhost:5173 # This is the default URL for the frontend, replace it with your own if you host the frontend on a different port/URL.


SECRET_KEY = Your Secret Key for the FastAPI application

JWT_SECRET = Any random string for the JWT token, Acts like a salt for the JWT token
RPAY_KEY = Public Key for Razorpay
RPAY_SECRET = Secret Key for Razorpay


MONGO_URI = Your MongoDB server URI

```

4. Run the server by running the following command:
```bash
python run.py
```
> This script will install all the dependencies needed for the project and run the server on port 8000.

## API Documentation

The API documentation can be found at `http://localhost:8000/docs` once the server is running. FastAPI provides an interactive documentation for the API which can be used to test the API endpoints.

## License

No license

```