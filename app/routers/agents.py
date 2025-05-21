"""
Agent operation endpoints.
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.core.persona_agent import Persona
from app.core.tasks.background_manager import BackgroundManager, TaskType
from app.models.persona import PersonaAgent, AgentState
from app.models.knowledge_node import KnowledgeNode
from app.models.validation_result import ValidationResult
from app.schemas.node import BackgroundProcessRequest
from app.db.session import get_db

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/{agent_id}/process_query")
async def process_query(
    agent_id: UUID,
    request: BackgroundProcessRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Trigger agent reasoning for a node/query.
    
    Features:
    - Synchronous or background processing
    - Optional peer agent collaboration
    - Trace logging
    - Validation results
    """
    # Get agent from database
    agent_db = db.query(PersonaAgent).filter(PersonaAgent.id == agent_id).first()
    if not agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    # Create agent instance
    agent = Persona(
        id=agent_db.id,
        name=agent_db.name,
        domain_coverage=agent_db.domain_coverage,
        algorithms_available=agent_db.algorithms_available,
        learning_trace=agent_db.learning_trace
    )
    
    # Get node from database
    node = db.query(KnowledgeNode).filter(KnowledgeNode.id == request.node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
        
    # Process query
    if request.background:
        # Schedule background task
        background_manager = BackgroundManager()
        task_id = await background_manager.schedule_task(
            TaskType.PROCESS,
            request.node_id,
            {
                "agent_id": str(agent_id),
                "algorithm_id": request.algorithm_id,
                "parameters": request.parameters
            },
            priority=request.priority
        )
        return {"task_id": task_id}
    else:
        # Process synchronously
        result = agent.process_query(
            node=node.to_dict(),
            algorithm_id=request.algorithm_id,
            pillar_levels_map={},  # TODO: Load from database
            max_recursion=request.parameters.get("max_recursion", 3)
        )
        return result

@router.get("/{agent_id}/state")
async def get_agent_state(
    agent_id: UUID,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current agent state"""
    agent = db.query(PersonaAgent).filter(PersonaAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {
        "id": str(agent.id),
        "name": agent.name,
        "state": agent.state.value,
        "domain_coverage": agent.domain_coverage
    }

@router.get("/{agent_id}/trace")
async def get_agent_trace(
    agent_id: UUID,
    limit: Optional[int] = 100,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get agent learning trace"""
    agent = db.query(PersonaAgent).filter(PersonaAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.learning_trace[-limit:] if limit else agent.learning_trace

@router.post("/batch_research")
async def batch_research(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Trigger autonomous batch research on low-confidence nodes.
    
    Features:
    - Confidence threshold filtering
    - Domain-specific agent selection
    - Parallel processing
    - Progress tracking
    """
    # Get nodes below confidence threshold
    nodes = (
        db.query(KnowledgeNode)
        .join(ValidationResult)
        .filter(ValidationResult.confidence < request.get("confidence_threshold", 0.7))
        .limit(request.get("batch_size", 100))
        .all()
    )
    
    # Schedule background tasks
    background_manager = BackgroundManager()
    task_ids = []
    
    for node in nodes:
        # Find suitable agent for node's domain
        agent = (
            db.query(PersonaAgent)
            .filter(PersonaAgent.domain_coverage.contains([node.pillar_level_id]))
            .first()
        )
        if agent:
            task_id = await background_manager.schedule_task(
                TaskType.RESEARCH,
                str(node.id),
                {
                    "agent_id": str(agent.id),
                    "algorithm_id": request.get("algorithm_id", "ai_knowledge_discovery")
                }
            )
            task_ids.append(task_id)
    
    return {"task_ids": task_ids}

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: UUID) -> Dict[str, Any]:
    """Get background task status and results"""
    background_manager = BackgroundManager()
    task = background_manager.tasks.get(str(task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "id": str(task.id),
        "status": task.status.value,
        "progress": task.progress,
        "result": task.result if task.is_complete else None
    } 