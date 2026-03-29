"""
Data Access Layer
Low-level database operations abstraction
"""

from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, Optional, List, Any
from src.config import SessionLocal

T = TypeVar('T')


class DataAccessLayer(Generic[T]):
    """Generic data access layer for all database operations"""
    
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
    
    def create(self, obj_in: Any) -> T:
        """Create a new record"""
        db_obj = self.model(**obj_in.dict() if hasattr(obj_in, 'dict') else obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def read(self, id: Any) -> Optional[T]:
        """Read a record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def read_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Read all records with pagination"""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, id: Any, obj_in: Any) -> Optional[T]:
        """Update a record"""
        db_obj = self.read(id)
        if db_obj:
            update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: Any) -> bool:
        """Delete a record"""
        db_obj = self.read(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
    
    def filter(self, **kwargs) -> List[T]:
        """Filter records by conditions"""
        return self.db.query(self.model).filter_by(**kwargs).all()
    
    def filter_one(self, **kwargs) -> Optional[T]:
        """Filter for a single record"""
        return self.db.query(self.model).filter_by(**kwargs).first()
