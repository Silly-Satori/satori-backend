import uuid
import secrets
def generate_session_token():
    # generate a secure session token
    
    session = secrets.token_urlsafe(16)+str(uuid.uuid4())
    return session
