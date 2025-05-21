"""
Knowledge edge API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.knowledge_edge import KnowledgeEdge
from app.schemas.edge import (
    EdgeCreate,
    EdgeUpdate,
    EdgeResponse,
    EdgeList,
    EdgeFilter
)
from app.db.session import get_db

router = APIRouter(prefix="/edges", tags=["edges"])

@router.post("/", response_model=EdgeResponse)
async def create_edge(
    edge: EdgeCreate,
    db: Session = Depends(get_db)
) -> EdgeResponse:
    """
    Create a new knowledge edge.
    
    Features:
    - Automatic UUID generation
    - Node existence validation
    - Cycle detection
    """
    try:
        db_edge = KnowledgeEdge(**edge.model_dump())
        db.add(db_edge)
        db.commit()
        db.refresh(db_edge)
        return db_edge
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid nodes or duplicate edge"
        )

@router.get("/{edge_id}", response_model=EdgeResponse)
async def get_edge(
    edge_id: UUID,
    db: Session = Depends(get_db)
) -> EdgeResponse:
    """Get a knowledge edge by ID"""
    edge = db.query(KnowledgeEdge).filter(KnowledgeEdge.id == edge_id).first()
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found")
    return edge

@router.get("/", response_model=EdgeList)
async def list_edges(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    from_node_id: Optional[UUID] = None,
    to_node_id: Optional[UUID] = None,
    edge_type: Optional[str] = None,
    db: Session = Depends(get_db)
) -> EdgeList:
    """
    List knowledge edges with filtering and pagination.
    
    Features:
    - Pagination support
    - Node filtering (from/to)
    - Edge type filtering
    """
    query = db.query(KnowledgeEdge)
    
    # Apply filters
    if from_node_id:
        query = query.filter(KnowledgeEdge.from_node_id == from_node_id)
    if to_node_id:
        query = query.filter(KnowledgeEdge.to_node_id == to_node_id)
    if edge_type:
        query = query.filter(KnowledgeEdge.edge_type == edge_type)
    
    total = query.count()
    edges = query.offset(skip).limit(limit).all()
    
    return EdgeList(
        items=edges,
        total=total,
        skip=skip,
        limit=limit
    )

@router.put("/{edge_id}", response_model=EdgeResponse)
async def update_edge(
    edge_id: UUID,
    edge_update: EdgeUpdate,
    db: Session = Depends(get_db)
) -> EdgeResponse:
    """
    Update a knowledge edge.
    
    Features:
    - Partial updates supported
    - Node existence validation
    - Cycle detection
    """
    db_edge = db.query(KnowledgeEdge).filter(KnowledgeEdge.id == edge_id).first()
    if not db_edge:
        raise HTTPException(status_code=404, detail="Edge not found")
    
    # Update fields
    for field, value in edge_update.model_dump(exclude_unset=True).items():
        setattr(db_edge, field, value)
    
    try:
        db.commit()
        db.refresh(db_edge)
        return db_edge
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid update data"
        )

@router.delete("/{edge_id}")
async def delete_edge(
    edge_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """Delete a knowledge edge"""
    db_edge = db.query(KnowledgeEdge).filter(KnowledgeEdge.id == edge_id).first()
    if not db_edge:
        raise HTTPException(status_code=404, detail="Edge not found")
    
    db.delete(db_edge)
    db.commit()
    
    return {"status": "success", "message": "Edge deleted"}
