from fastapi import Request
import jwt
from pydantic import BaseModel
from app.core.config import settings
import textwrap

class AuthException(Exception):
    def __init__(self, message: str):
        self.message = message

class UserAuth(BaseModel):
    id: str
    token: str

def format_public_key(key: str) -> str:
    key = key.replace('\\n', '\n')
    header = "-----BEGIN PUBLIC KEY-----"
    footer = "-----END PUBLIC KEY-----"
    
    if header in key and footer in key:
        body = key.replace(header, "").replace(footer, "")
        body = "".join(body.split())
        body = "\n".join(textwrap.wrap(body, width=64))
        return f"{header}\n{body}\n{footer}"
    return key

def get_current_user(request: Request) -> UserAuth:
    auth_header = request.headers.get("authorization")
    
    if not auth_header:
        raise AuthException("Missing Authorization header")
        
    parts = auth_header.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthException("Authorization must be Bearer token")
        
    token = parts[1]
    
    try:
        public_key = format_public_key(settings.JWT_PUBLIC_KEY_PEM)
        
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE
        )
        
        sub = payload.get("sub")
        if not sub or not str(sub).strip():
            raise AuthException("Invalid token claims")
            
        return UserAuth(id=str(sub), token=token)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise AuthException("Invalid or expired access token")
