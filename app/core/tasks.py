"""
Background tasks for agent recursion and autonomous operations.
"""
from typing import Dict, Any, List
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from app.models.knowledge_node import KnowledgeNode
from app.models.persona import PersonaAgent
from app.core.persona_agent import Persona
from app.db.session import SessionLocal

def process_agent_recursion(
    node_id: str,
    algorithm_id: str,
    agent_ids: List[str],
    max_recursion: int = 3,
    background_tasks: BackgroundTasks = None
) -> None:
    """
    Process agent recursion as a background task.
    
    Args:
        node_id: ID of the node to process
        algorithm_id: ID of the algorithm to apply
        agent_ids: List of agent IDs to involve
        max_recursion: Maximum recursion depth
        background_tasks: FastAPI background tasks instance
    """
    def _process():
        db = SessionLocal()
        try:
            # Get node and agents
            node = db.query(KnowledgeNode).filter(KnowledgeNode.id == node_id).first()
            agents = db.query(PersonaAgent).filter(PersonaAgent.id.in_(agent_ids)).all()
            
            # Convert to domain objects
            persona_agents = [
                Persona(
                    id=agent.id,
                    name=agent.name,
                    domain_coverage=agent.domain_coverage,
                    algorithms_available=agent.algorithms_available,
                    learning_trace=agent.learning_trace
                )
                for agent in agents
            ]
            
            # Process recursively
            for agent in persona_agents:
                result = agent.process_query(
                    node=node.to_dict(),
                    algorithm_id=algorithm_id,
                    pillar_levels_map={},  # Load from DB as needed
                    recursion_depth=0,
                    max_recursion=max_recursion,
                    background_agents=persona_agents
                )
                
                # Update agent trace in DB
                db_agent = db.query(PersonaAgent).filter(PersonaAgent.id == agent.id).first()
                if db_agent:
                    db_agent.learning_trace = agent.learning_trace
                    db.commit()
                
                # If more processing needed, schedule another background task
                if result.get("needs_more_processing"):
                    if background_tasks:
                        background_tasks.add_task(
                            process_agent_recursion,
                            node_id=node_id,
                            algorithm_id=result["next_algorithm"],
                            agent_ids=[str(a.id) for a in persona_agents],
                            max_recursion=max_recursion - 1
                        )
        
        finally:
            db.close()
    
    if background_tasks:
        background_tasks.add_task(_process)
    else:
        _process() 