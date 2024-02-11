import uuid
import secrets
import jwt
import os


class TokenGenerator:
    def generate_session_token():
        # generate a secure session token
        session = secrets.token_urlsafe(16)+str(uuid.uuid4())
        return session

    def generate_jwt_token(data):
        # generate a jwt token
        encoded_jwt = jwt.encode(
            data,
            os.getenv("JWT_SECRET"),
            algorithm="HS256",
        )
        
        return encoded_jwt

    def decode_jwt_token(token):
        # decode a jwt token
        try:
            decoded_jwt = jwt.decode(
                token,
                os.getenv("JWT_SECRET"),
                algorithms=["HS256"]
            )
            return decoded_jwt
        except jwt.exceptions.InvalidSignatureError:
            return "invalid_sign"
        except jwt.exceptions.DecodeError:
            return "decode_error"
        except:
            return False
