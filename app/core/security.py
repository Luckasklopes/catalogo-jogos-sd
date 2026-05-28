from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel
from app.core.config import settings

security = HTTPBearer()

class UserAuth(BaseModel):
    id: str
    token: str

def format_public_key(key: str) -> str:
    key = key.replace('\\n', '\n')
    header = "-----BEGIN PUBLIC KEY-----"
    footer = "-----END PUBLIC KEY-----"
    
    if header in key and footer in key:
        # Extrai o miolo, remove todos os espaços e quebras de linha
        body = key.replace(header, "").replace(footer, "")
        body = "".join(body.split())
        return f"{header}\n{body}\n{footer}"
    return key

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserAuth:
    token = credentials.credentials
    
    try:
        # Garante que a chave terá o formato PEM válido, independentemente de como foi definida no .env
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return UserAuth(id=str(sub), token=token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        import traceback
        traceback.print_exc() # Imprime no log do docker para ajudar a debugar
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
