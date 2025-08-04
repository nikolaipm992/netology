from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./advertisements.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Integer, nullable=False)
    author = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Create tables
Base.metadata.create_all(bind=engine)

# Schemas
class AdvertisementBase(BaseModel):
    title: str
    description: str
    price: int
    author: str

class AdvertisementCreate(AdvertisementBase):
    pass

class AdvertisementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    author: Optional[str] = None

class AdvertisementResponse(AdvertisementBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI(title="Advertisement Service", version="1.0.0")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/advertisement", response_model=AdvertisementResponse, status_code=201)
def create_advertisement(advertisement: AdvertisementCreate, db: Session = Depends(get_db)):
    """Создание нового объявления"""
    db_advertisement = Advertisement(**advertisement.model_dump())
    db.add(db_advertisement)
    db.commit()
    db.refresh(db_advertisement)
    return db_advertisement

@app.get("/advertisement/{advertisement_id}", response_model=AdvertisementResponse)
def get_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    """Получение объявления по ID"""
    advertisement = db.query(Advertisement).filter(Advertisement.id == advertisement_id).first()
    if advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return advertisement

@app.patch("/advertisement/{advertisement_id}", response_model=AdvertisementResponse)
def update_advertisement(
    advertisement_id: int, 
    advertisement_update: AdvertisementUpdate, 
    db: Session = Depends(get_db)
):
    """Обновление объявления по ID"""
    db_advertisement = db.query(Advertisement).filter(Advertisement.id == advertisement_id).first()
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    update_data = advertisement_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_advertisement, key, value)
    
    db.commit()
    db.refresh(db_advertisement)
    return db_advertisement

@app.delete("/advertisement/{advertisement_id}", status_code=204)
def delete_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    """Удаление объявления по ID"""
    advertisement = db.query(Advertisement).filter(Advertisement.id == advertisement_id).first()
    if advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    db.delete(advertisement)
    db.commit()
    return None

@app.get("/advertisement", response_model=List[AdvertisementResponse])
def search_advertisements(
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Поиск объявлений по полям"""
    query = db.query(Advertisement)
    
    if title:
        query = query.filter(Advertisement.title.contains(title))
    
    if author:
        query = query.filter(Advertisement.author.contains(author))
    
    if min_price is not None:
        query = query.filter(Advertisement.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Advertisement.price <= max_price)
    
    return query.all()