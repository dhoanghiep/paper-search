from sqlalchemy.orm import Session
from app.models import Category
from typing import List, Optional

class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        return self.db.query(Category).filter(Category.id == category_id).first()
    
    def get_by_name(self, name: str) -> Optional[Category]:
        """Get category by name"""
        return self.db.query(Category).filter(Category.name == name).first()
    
    def get_all(self) -> List[Category]:
        """Get all categories"""
        return self.db.query(Category).all()
    
    def count_all(self) -> int:
        """Count all categories"""
        return self.db.query(Category).count()
    
    def create(self, name: str, description: str = None) -> Category:
        """Create new category"""
        category = Category(name=name, description=description)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def get_or_create(self, name: str, description: str = None) -> Category:
        """Get existing category or create new one"""
        category = self.get_by_name(name)
        if not category:
            category = self.create(name, description)
        return category
    
    def update(self, category: Category) -> Category:
        """Update category"""
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def delete(self, category_id: int) -> bool:
        """Delete category"""
        category = self.get_by_id(category_id)
        if category:
            self.db.delete(category)
            self.db.commit()
            return True
        return False
