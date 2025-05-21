"""
Knowledge node API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.knowledge_node import KnowledgeNode
from app.schemas.node import (
    NodeCreate,
    NodeUpdate,
    NodeResponse,
    NodeList,
    NodeFilter
)
from app.db.session import get_db

router = APIRouter(prefix="/nodes", tags=["nodes"])

@router.post("/", response_model=NodeResponse)
async def create_node(
    node: NodeCreate,
    db: Session = Depends(get_db)
) -> NodeResponse:
    """
    Create a new knowledge node.
    
    Features:
    - Automatic UUID generation
    - Axis value validation
    - Pillar level verification
    """
    try:
        db_node = KnowledgeNode(**node.model_dump())
        db.add(db_node)
        db.commit()
        db.refresh(db_node)
        return db_node
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid pillar level or duplicate node"
        )

@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: UUID,
    db: Session = Depends(get_db)
) -> NodeResponse:
    """Get a knowledge node by ID"""
    node = db.query(KnowledgeNode).filter(KnowledgeNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@router.get("/", response_model=NodeList)
async def list_nodes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    pillar_level_id: Optional[str] = None,
    confidence_threshold: Optional[float] = None,
    db: Session = Depends(get_db)
) -> NodeList:
    """
    List knowledge nodes with filtering and pagination.
    
    Features:
    - Pagination support
    - Pillar level filtering
    - Confidence threshold filtering
    """
    query = db.query(KnowledgeNode)
    
    # Apply filters
    if pillar_level_id:
        query = query.filter(KnowledgeNode.pillar_level_id == pillar_level_id)
    if confidence_threshold:
        query = (
            query.join(KnowledgeNode.validation_results)
            .filter(ValidationResult.confidence >= confidence_threshold)
        )
    
    total = query.count()
    nodes = query.offset(skip).limit(limit).all()
    
    return NodeList(
        items=nodes,
        total=total,
        skip=skip,
        limit=limit
    )

@router.put("/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: UUID,
    node_update: NodeUpdate,
    db: Session = Depends(get_db)
) -> NodeResponse:
    """
    Update a knowledge node.
    
    Features:
    - Partial updates supported
    - Axis value validation
    - Update timestamp management
    """
    db_node = db.query(KnowledgeNode).filter(KnowledgeNode.id == node_id).first()
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Update fields
    for field, value in node_update.model_dump(exclude_unset=True).items():
        setattr(db_node, field, value)
    
    try:
        db.commit()
        db.refresh(db_node)
        return db_node
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid update data"
        )

@router.delete("/{node_id}")
async def delete_node(
    node_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """Delete a knowledge node"""
    db_node = db.query(KnowledgeNode).filter(KnowledgeNode.id == node_id).first()
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    db.delete(db_node)
    db.commit()
    
    return {"status": "success", "message": "Node deleted"}


# Repeat similar pattern for Edges, PillarLevels (api/v1/edges.py, etc.)