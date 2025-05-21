"""
Algorithm API endpoints.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.algorithms import ALGORITHMS
from app.core.tasks.background_manager import BackgroundManager, TaskType
from app.models.knowledge_node import KnowledgeNode
from app.schemas.algorithm import (
    AlgorithmInfo,
    AlgorithmList,
    AlgorithmExecuteRequest,
    AlgorithmExecuteResponse,
    BatchExecuteRequest,
    TaskResponse
)
from app.db.session import get_db

router = APIRouter(prefix="/algorithms", tags=["algorithms"])

@router.get("/", response_model=AlgorithmList)
async def list_algorithms() -> AlgorithmList:
    """
    List available algorithms.
    
    Features:
    - Algorithm metadata
    - Parameter specifications
    - Required axis information
    """
    algorithms = []
    for algo_id, algo in ALGORITHMS.items():
        algorithms.append(
            AlgorithmInfo(
                id=algo_id,
                name=algo.__name__,
                description=algo.__doc__ or "",
                parameters=getattr(algo, "parameters", {}),
                required_axes=getattr(algo, "required_axes", []),
                output_type=getattr(algo, "output_type", "any")
            )
        )
    return AlgorithmList(items=algorithms)

@router.get("/{algorithm_id}", response_model=AlgorithmInfo)
async def get_algorithm(algorithm_id: str) -> AlgorithmInfo:
    """Get algorithm details"""
    if algorithm_id not in ALGORITHMS:
        raise HTTPException(status_code=404, detail="Algorithm not found")
        
    algo = ALGORITHMS[algorithm_id]
    return AlgorithmInfo(
        id=algorithm_id,
        name=algo.__name__,
        description=algo.__doc__ or "",
        parameters=getattr(algo, "parameters", {}),
        required_axes=getattr(algo, "required_axes", []),
        output_type=getattr(algo, "output_type", "any")
    )

@router.post("/{algorithm_id}/execute", response_model=AlgorithmExecuteResponse)
async def execute_algorithm(
    algorithm_id: str,
    request: AlgorithmExecuteRequest,
    db: Session = Depends(get_db)
) -> AlgorithmExecuteResponse:
    """
    Execute an algorithm synchronously.
    
    Features:
    - Parameter validation
    - Axis value validation
    - Result validation
    """
    if algorithm_id not in ALGORITHMS:
        raise HTTPException(status_code=404, detail="Algorithm not found")
        
    # Get node
    node = db.query(KnowledgeNode).filter(KnowledgeNode.id == request.node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
        
    # Execute algorithm
    try:
        algo = ALGORITHMS[algorithm_id]
        result = algo(
            node=node.to_dict(),
            parameters=request.parameters,
            context=request.context or {}
        )
        return AlgorithmExecuteResponse(
            node_id=str(node.id),
            algorithm_id=algorithm_id,
            result=result["result"],
            confidence=result.get("confidence", 0.0),
            metadata=result.get("metadata", {})
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Algorithm execution failed: {str(e)}"
        )

@router.post("/batch-execute", response_model=TaskResponse)
async def batch_execute(
    request: BatchExecuteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Execute algorithms on multiple nodes in the background.
    
    Features:
    - Batch processing
    - Priority handling
    - Progress tracking
    - Result aggregation
    """
    # Validate nodes exist
    nodes = (
        db.query(KnowledgeNode)
        .filter(KnowledgeNode.id.in_([str(id) for id in request.node_ids]))
        .all()
    )
    if len(nodes) != len(request.node_ids):
        raise HTTPException(status_code=400, detail="One or more nodes not found")
        
    # Validate algorithms exist
    for algo_id in request.algorithm_ids:
        if algo_id not in ALGORITHMS:
            raise HTTPException(
                status_code=400,
                detail=f"Algorithm not found: {algo_id}"
            )
            
    # Schedule batch task
    background_manager = BackgroundManager()
    task_id = await background_manager.schedule_task(
        TaskType.BATCH_PROCESS,
        None,  # No specific node ID for batch
        {
            "node_ids": [str(id) for id in request.node_ids],
            "algorithm_ids": request.algorithm_ids,
            "parameters": request.parameters,
            "context": request.context
        },
        priority=request.priority
    )
    
    return TaskResponse(
        task_id=str(task_id),
        status="scheduled",
        message="Batch execution scheduled"
    )

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: UUID) -> TaskResponse:
    """Get batch execution task status"""
    background_manager = BackgroundManager()
    task = background_manager.tasks.get(str(task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return TaskResponse(
        task_id=str(task_id),
        status=task.status.value,
        progress=task.progress,
        result=task.result if task.is_complete else None,
        error=task.error if task.error else None
    )