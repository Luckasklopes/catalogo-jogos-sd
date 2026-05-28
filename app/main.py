from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.security import get_current_user, UserAuth, AuthException
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.database import Base, engine

# Cria as tabelas do banco de dados (idealmente usaríamos Alembic em produção)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://sistema-distribuido-trabalho-faculd.vercel.app"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(
        status_code=401,
        content={"message": exc.message}
    )

@app.get("/")
def root(current_user: UserAuth = Depends(get_current_user)):
    return {"message": "Bem-vindo ao Microsserviço de Catálogo do GameVerse"}
