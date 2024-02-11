from fastapi import APIRouter, Depends, HTTPException

from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

import os

from functions.auth import TokenGenerator

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

config = Config('.env')  # read config from .env file
oauth: OAuth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    },
    authorize_state= os.environ["SECRET_KEY"]
)


@router.get('/login')
async def login(request: Request):
    # redirect to google/callback
    current_url = request.url
    print(current_url)
    redirect_uri = str(current_url).replace('login', 'google/callback')
    print("\n"*2)
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/google/callback')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = token.get('userinfo', None)
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
    # set the cookie with the session token
    resp = RedirectResponse(url=f'http://localhost:3000/auth/{session_token}')
    resp.set_cookie(key="user", value=user, samesite="lax", secure=True)

    return resp


@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')
