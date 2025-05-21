"""
Agent operation endpoints.
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.persona_agent import Persona
from app.core.tasks.background_manager import BackgroundManager, TaskType
from app.core.auth import get_current_active_user
from app.models.persona import PersonaAgent, AgentState
from app.models.knowledge_node import KnowledgeNode
from app.models.validation_result import ValidationResult
from app.models.user import User
from app.schemas.node import BackgroundProcessRequest
from app.db.session import get_db

router = APIRouter(prefix="/agents", tags=["agents"])

def hydrate_persona_agent(db_row: PersonaAgent) -> Persona:
    """Create Persona instance from database row"""
    return Persona(
        id=db_row.id,
        name=db_row.name,
        domain_coverage=db_row.domain_coverage,
        algorithms_available=db_row.algorithms_available,
        learning_trace=db_row.learning_trace
    )

@router.get("/", response_model=List[Dict[str, Any]])
async def list_agents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """List all agents"""
    agents = db.query(PersonaAgent).all()
    return [
        {
            "id": str(a.id),
            "name": a.name,
            "domain_coverage": a.domain_coverage,
            "algorithms_available": a.algorithms_available,
            "state": a.state.value
        }
        for a in agents
    ]

@router.get("/{agent_id}", response_model=Dict[str, Any])
async def get_agent(
    agent_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get agent details"""
    agent = db.query(PersonaAgent).filter(PersonaAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {
        "id": str(agent.id),
        "name": agent.name,
        "domain_coverage": agent.domain_coverage,
        "algorithms_available": agent.algorithms_available,
        "state": agent.state.value
    }

@router.get("/{agent_id}/trace", response_model=List[Dict[str, Any]])
async def get_agent_trace(
    agent_id: UUID,
    limit: Optional[int] = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get agent learning trace"""
    agent = db.query(PersonaAgent).filter(PersonaAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.learning_trace[-limit:] if limit else agent.learning_trace

@router.post("/{agent_id}/process_query")
async def process_query(
    agent_id: UUID,
    request: BackgroundProcessRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
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
    agent = hydrate_persona_agent(agent_db)
    
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
        # Get all agents for peer recursion
        all_agents = db.query(PersonaAgent).filter(PersonaAgent.id != agent_id).all()
        peer_agents = [hydrate_persona_agent(a) for a in all_agents]
        bg_agents = [agent] + peer_agents
        
        # Process synchronously
        result = agent.process_query(
            node=node.to_dict(),
            algorithm_id=request.algorithm_id,
            pillar_levels_map={},  # TODO: Load from database
            max_recursion=request.parameters.get("max_recursion", 3),
            background_agents=bg_agents
        )
        
        # Save trace back
        agent_db.learning_trace = agent.learning_trace
        db.commit()
        
        return result