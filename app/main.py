from fastapi import FastAPI, Depends
from app.core.security import get_current_user, UserAuth
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.database import Base, engine

# Cria as tabelas do banco de dados (idealmente usaríamos Alembic em produção)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root(current_user: UserAuth = Depends(get_current_user)):
    return {"message": "Bem-vindo ao Microsserviço de Catálogo do GameVerse"}
