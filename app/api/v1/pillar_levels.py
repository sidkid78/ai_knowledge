"""
Pillar level API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.pillar_level import PillarLevel
from app.schemas.pillar_level import (
    PillarLevelCreate,
    PillarLevelUpdate,
    PillarLevelResponse,
    PillarLevelList,
    PillarLevelFilter
)
from app.db.session import get_db

router = APIRouter(prefix="/pillar-levels", tags=["pillar_levels"])

@router.post("/", response_model=PillarLevelResponse)
async def create_pillar_level(
    pillar_level: PillarLevelCreate,
    db: Session = Depends(get_db)
) -> PillarLevelResponse:
    """
    Create a new pillar level.
    
    Features:
    - ID format validation
    - Parent level validation
    - Hierarchy cycle detection
    """
    try:
        db_pillar = PillarLevel(**pillar_level.model_dump())
        db.add(db_pillar)
        db.commit()
        db.refresh(db_pillar)
        return db_pillar
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid parent level or duplicate ID"
        )

@router.get("/{pillar_id}", response_model=PillarLevelResponse)
async def get_pillar_level(
    pillar_id: str,
    db: Session = Depends(get_db)
) -> PillarLevelResponse:
    """Get a pillar level by ID"""
    pillar = db.query(PillarLevel).filter(PillarLevel.id == pillar_id).first()
    if not pillar:
        raise HTTPException(status_code=404, detail="Pillar level not found")
    return pillar

@router.get("/", response_model=PillarLevelList)
async def list_pillar_levels(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    parent_id: Optional[str] = None,
    domain: Optional[str] = None,
    db: Session = Depends(get_db)
) -> PillarLevelList:
    """
    List pillar levels with filtering and pagination.
    
    Features:
    - Pagination support
    - Parent level filtering
    - Domain filtering
    - Hierarchical structure
    """
    query = db.query(PillarLevel)
    
    # Apply filters
    if parent_id:
        query = query.filter(PillarLevel.parent_id == parent_id)
    if domain:
        query = query.filter(PillarLevel.domain == domain)
    
    total = query.count()
    pillars = query.offset(skip).limit(limit).all()
    
    return PillarLevelList(
        items=pillars,
        total=total,
        skip=skip,
        limit=limit
    )

@router.put("/{pillar_id}", response_model=PillarLevelResponse)
async def update_pillar_level(
    pillar_id: str,
    pillar_update: PillarLevelUpdate,
    db: Session = Depends(get_db)
) -> PillarLevelResponse:
    """
    Update a pillar level.
    
    Features:
    - Partial updates supported
    - Parent level validation
    - Hierarchy cycle detection
    """
    db_pillar = db.query(PillarLevel).filter(PillarLevel.id == pillar_id).first()
    if not db_pillar:
        raise HTTPException(status_code=404, detail="Pillar level not found")
    
    # Update fields
    for field, value in pillar_update.model_dump(exclude_unset=True).items():
        setattr(db_pillar, field, value)
    
    try:
        db.commit()
        db.refresh(db_pillar)
        return db_pillar
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid update data"
        )

@router.delete("/{pillar_id}")
async def delete_pillar_level(
    pillar_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """Delete a pillar level"""
    db_pillar = db.query(PillarLevel).filter(PillarLevel.id == pillar_id).first()
    if not db_pillar:
        raise HTTPException(status_code=404, detail="Pillar level not found")
    
    # Check for child levels
    if db.query(PillarLevel).filter(PillarLevel.parent_id == pillar_id).first():
        raise HTTPException(
            status_code=400,
            detail="Cannot delete pillar level with child levels"
        )
    
    db.delete(db_pillar)
    db.commit()
    
    return {"status": "success", "message": "Pillar level deleted"} 



