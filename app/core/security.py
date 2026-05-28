from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel
from app.core.config import settings

security = HTTPBearer()

class UserAuth(BaseModel):
    id: str
    token: str

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserAuth:
    token = credentials.credentials
    
    try:
        # A chave pública pode vir com '\n' escapado do .env
        public_key = settings.JWT_PUBLIC_KEY_PEM.replace('\\n', '\n')
        
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
