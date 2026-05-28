from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, String
from typing import List, Optional
import re
import unicodedata

from app.schemas.game import GameCreate, GameUpdate, GameResponse, StandardResponse
from app.models.game import Game
from app.db.database import get_db
from app.core.security import get_current_user, UserAuth

router = APIRouter()

def generate_slug(title: str) -> str:
    # Remove acentos
    text = unicodedata.normalize('NFKD', title).encode('ASCII', 'ignore').decode('utf-8')
    # Transforma para lowercase e substitui espaços por hifens
    text = text.lower()
    # Remove caracteres especiais
    text = re.sub(r'[^a-z0-9\-]', '-', text)
    # Remove hifens duplicados
    text = re.sub(r'-+', '-', text).strip('-')
    return text

@router.get("/", response_model=StandardResponse)
def read_games(skip: int = 0, limit: int = 100, genre: Optional[str] = None, platform: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Game)
    
    if genre:
        query = query.filter(Game.genres.contains([genre]))
    
    if platform:
        query = query.filter(Game.platforms.contains([platform]))
        
    games = query.offset(skip).limit(limit).all()
    data = [GameResponse.model_validate(g).model_dump(mode='json') for g in games]
    
    return {"success": True, "message": "Lista de jogos", "data": data}

@router.post("/", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def create_game(game: GameCreate, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    slug = generate_slug(game.title)
    
    # Verifica se já existe um jogo com esse slug
    db_game = db.query(Game).filter(Game.slug == slug).first()
    if db_game:
        raise HTTPException(status_code=400, detail="Um jogo com este título/slug já existe.")
        
    # Cria o modelo no DB
    game_data = game.model_dump(mode='json')
    db_game = Game(**game_data, slug=slug)
    
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    
    data = GameResponse.model_validate(db_game).model_dump()
    return {"success": True, "message": "Jogo criado com sucesso", "data": data}

@router.get("/{id_ou_slug}", response_model=StandardResponse)
def read_game(id_ou_slug: str, db: Session = Depends(get_db)):
    if id_ou_slug.isdigit():
        db_game = db.query(Game).filter(Game.id == int(id_ou_slug)).first()
    else:
        db_game = db.query(Game).filter(Game.slug == id_ou_slug).first()
    
    if not db_game:
        raise HTTPException(status_code=404, detail="Jogo não encontrado.")
        
    data = GameResponse.model_validate(db_game).model_dump(mode='json')
    return {"success": True, "message": "Detalhes do jogo", "data": data}

@router.patch("/{id}", response_model=StandardResponse)
def update_game(id: int, game: GameUpdate, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    db_game = db.query(Game).filter(Game.id == id).first()
    
    if not db_game:
        raise HTTPException(status_code=404, detail="Jogo não encontrado.")
        
    update_data = game.model_dump(mode='json', exclude_unset=True)
    
    if "title" in update_data:
        new_slug = generate_slug(update_data["title"])
        # Verifica se o novo slug conflita com outro jogo existente
        existing_slug = db.query(Game).filter(Game.slug == new_slug, Game.id != id).first()
        if existing_slug:
            raise HTTPException(status_code=400, detail="Um jogo com este título/slug já existe.")
        db_game.slug = new_slug
        
    for key, value in update_data.items():
        setattr(db_game, key, value)
        
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    
    data = GameResponse.model_validate(db_game).model_dump(mode='json')
    return {"success": True, "message": "Jogo atualizado com sucesso", "data": data}

@router.delete("/{id_ou_slug}", response_model=StandardResponse)
def delete_game(id_ou_slug: str, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    if id_ou_slug.isdigit():
        db_game = db.query(Game).filter(Game.id == int(id_ou_slug)).first()
    else:
        db_game = db.query(Game).filter(Game.slug == id_ou_slug).first()
        
    if not db_game:
        raise HTTPException(status_code=404, detail="Jogo não encontrado.")
        
    db.delete(db_game)
    db.commit()
    
    return {"success": True, "message": "Jogo removido com sucesso", "data": None}
