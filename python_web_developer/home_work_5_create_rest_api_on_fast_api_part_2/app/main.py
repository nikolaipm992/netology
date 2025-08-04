from fastapi import FastAPI, HTTPException, Depends, Query, Header, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from . import models, schemas
from .database import SessionLocal, engine
from .auth import get_password_hash, create_access_token, authenticate_user
from .dependencies import get_db, get_current_user, get_token_from_header

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Advertisement Service with Auth", version="2.0.0")

# User endpoints
@app.post("/user", response_model=schemas.UserResponse, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Создание нового пользователя"""
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=models.UserRole.USER
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/user/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Получение пользователя по ID"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/user/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление пользователя (только себя или админ)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if current_user.id != user_id and current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    if 'password' in update_data:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/user/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление пользователя (только себя или админ)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if current_user.id != user_id and current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return None

# Auth endpoints
@app.post("/login", response_model=schemas.Token)
def login_for_access_token(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    """Аутентификация пользователя и выдача токена"""
    user = authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"user_id": user.id, "role": user.role.value}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Advertisement endpoints
@app.post("/advertisement", response_model=schemas.AdvertisementResponse, status_code=201)
def create_advertisement(
    advertisement: schemas.AdvertisementCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание нового объявления (только авторизованные пользователи)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db_advertisement = models.Advertisement(
        **advertisement.model_dump(),
        author_id=current_user.id
    )
    db.add(db_advertisement)
    db.commit()
    db.refresh(db_advertisement)
    return db_advertisement

@app.get("/advertisement/{advertisement_id}", response_model=schemas.AdvertisementResponse)
def get_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    """Получение объявления по ID (доступно всем)"""
    advertisement = db.query(models.Advertisement).filter(models.Advertisement.id == advertisement_id).first()
    if advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return advertisement

@app.patch("/advertisement/{advertisement_id}", response_model=schemas.AdvertisementResponse)
def update_advertisement(
    advertisement_id: int,
    advertisement_update: schemas.AdvertisementUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление объявления (только автор или админ)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db_advertisement = db.query(models.Advertisement).filter(models.Advertisement.id == advertisement_id).first()
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    # Проверка прав доступа
    if current_user.id != db_advertisement.author_id and current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = advertisement_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_advertisement, key, value)
    
    db.commit()
    db.refresh(db_advertisement)
    return db_advertisement

@app.delete("/advertisement/{advertisement_id}", status_code=204)
def delete_advertisement(
    advertisement_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление объявления (только автор или админ)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db_advertisement = db.query(models.Advertisement).filter(models.Advertisement.id == advertisement_id).first()
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    # Проверка прав доступа
    if current_user.id != db_advertisement.author_id and current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(db_advertisement)
    db.commit()
    return None

@app.get("/advertisement", response_model=List[schemas.AdvertisementResponse])
def search_advertisements(
    title: Optional[str] = Query(None),
    author_id: Optional[int] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Поиск объявлений по полям (доступно всем)"""
    query = db.query(models.Advertisement)
    
    if title:
        query = query.filter(models.Advertisement.title.contains(title))
    
    if author_id:
        query = query.filter(models.Advertisement.author_id == author_id)
    
    if min_price is not None:
        query = query.filter(models.Advertisement.price >= min_price)
    
    if max_price is not None:
        query = query.filter(models.Advertisement.price <= max_price)
    
    return query.all()