"""
Agent orchestration module for coordinating recursive learning.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
import logging
from datetime import datetime

from app.core.persona_agent import Persona, load_persona_agents
from app.models.persona import AgentState
from app.core.axes import validate_axis_params
from app.db.session import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessingResult:
    """Container for agent processing results"""
    def __init__(
        self,
        agent_name: str,
        success: bool,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        self.agent_name = agent_name
        self.success = success
        self.result = result
        self.error = error
        self.timestamp = datetime.utcnow().isoformat()

class Orchestrator:
    """
    Coordinates agent processing and recursive learning.
    
    Features:
    - Agent loading and validation
    - Node preprocessing
    - Parallel agent processing
    - Result aggregation
    - Error handling and recovery
    """
    
    def __init__(
        self,
        algorithm_options: Dict[str, Any],
        pillar_map: Dict[str, Any],
        max_recursion: int = 3,
        parallel: bool = False
    ):
        self.algorithm_options = algorithm_options
        self.pillar_map = pillar_map
        self.max_recursion = max_recursion
        self.parallel = parallel
        self.agents: List[Persona] = []
        self._processing_history: List[Dict[str, Any]] = []

    def load_agents(self) -> None:
        """Load agents from database"""
        db = SessionLocal()
        try:
            # Get agent rows from database
            from app.models.persona import PersonaAgent
            agent_rows = db.query(PersonaAgent).all()
            
            # Convert to list of dicts for agent loader
            persona_rows = [
                {
                    "id": str(agent.id),
                    "name": agent.name,
                    "domain_coverage": agent.domain_coverage,
                    "algorithms_available": agent.algorithms_available,
                    "confidence_threshold": agent.confidence_threshold,
                    "validation_rules": agent.validation_rules,
                    "research_sources": agent.research_sources,
                    "learning_trace": agent.learning_trace
                }
                for agent in agent_rows
            ]
            
            # Load agents
            self.agents = load_persona_agents(
                persona_rows,
                self.algorithm_options,
                self.pillar_map
            )
            
            logger.info(f"Loaded {len(self.agents)} agents")
            
        finally:
            db.close()

    def validate_node(self, node: Dict[str, Any]) -> bool:
        """
        Validate node structure and axis values.
        
        Args:
            node: Knowledge node to validate
            
        Returns:
            bool: Whether the node is valid
            
        Raises:
            ValueError: If node is invalid
        """
        required_fields = ["id", "label", "pillar_level_id", "axis_values"]
        for field in required_fields:
            if field not in node:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate pillar level
        if node["pillar_level_id"] not in self.pillar_map:
            raise ValueError(f"Invalid pillar level: {node['pillar_level_id']}")
        
        # Validate axis values
        for axis_name, axis_values in node["axis_values"].items():
            try:
                validate_axis_params(axis_name, axis_values)
            except Exception as e:
                raise ValueError(f"Invalid axis values for {axis_name}: {str(e)}")
        
        return True

    def process_node(
        self,
        node: Dict[str, Any],
        algorithm_id: str,
        specific_agents: Optional[List[str]] = None
    ) -> List[ProcessingResult]:
        """
        Process a node with all relevant agents.
        
        Args:
            node: Knowledge node to process
            algorithm_id: Algorithm to apply
            specific_agents: Optional list of agent names to use
            
        Returns:
            List of ProcessingResult objects
        """
        try:
            # Validate node
            self.validate_node(node)
            
            # Filter agents if specific ones requested
            agents_to_use = self.agents
            if specific_agents:
                agents_to_use = [
                    agent for agent in self.agents
                    if agent.name in specific_agents
                ]
                if not agents_to_use:
                    raise ValueError("No matching agents found")
            
            # Process with each agent
            results = []
            for agent in agents_to_use:
                try:
                    # Skip if agent doesn't support algorithm
                    if algorithm_id not in agent.algorithms_available:
                        logger.warning(f"Agent {agent.name} does not support algorithm {algorithm_id}")
                        continue
                    
                    # Process node
                    result = agent.process_query(
                        node=node,
                        algorithm_id=algorithm_id,
                        pillar_levels_map=self.pillar_map,
                        recursion_depth=0,
                        max_recursion=self.max_recursion,
                        background_agents=agents_to_use
                    )
                    
                    # Record result
                    results.append(ProcessingResult(
                        agent_name=agent.name,
                        success=True,
                        result=result
                    ))
                    
                except Exception as e:
                    logger.error(f"Error processing with agent {agent.name}: {str(e)}")
                    results.append(ProcessingResult(
                        agent_name=agent.name,
                        success=False,
                        error=str(e)
                    ))
            
            # Update processing history
            self._update_history(node["id"], algorithm_id, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in process_node: {str(e)}")
            raise

    def get_processing_history(
        self,
        node_id: Optional[str] = None,
        agent_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get processing history with optional filtering"""
        history = self._processing_history
        
        if node_id:
            history = [h for h in history if h["node_id"] == node_id]
        if agent_name:
            history = [h for h in history if h["agent_name"] == agent_name]
            
        return history

    def _update_history(
        self,
        node_id: str,
        algorithm_id: str,
        results: List[ProcessingResult]
    ) -> None:
        """Update processing history"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "node_id": node_id,
            "algorithm_id": algorithm_id,
            "results": [
                {
                    "agent_name": r.agent_name,
                    "success": r.success,
                    "error": r.error if not r.success else None,
                    "timestamp": r.timestamp
                }
                for r in results
            ]
        }
        self._processing_history.append(entry)

# Example usage
if __name__ == "__main__":
    # Sample data
    algorithm_options = {
        "ai_knowledge_discovery": {
            "name": "AI Knowledge Discovery",
            "parameters": {}
        }
    }
    
    pillar_map = {
        "PL04": {
            "name": "Quantum Computing",
            "description": "Quantum computing and related technologies"
        }
    }
    
    # Create orchestrator
    orchestrator = Orchestrator(algorithm_options, pillar_map)
    
    # Load agents
    orchestrator.load_agents()
    
    # Sample node
    target_node = {
        "id": "uuid-here",
        "label": "Quantum Computing",
        "pillar_level_id": "PL04",
        "axis_values": {
            "pillar_function": {
                "values": [0.9],
                "weights": [1.0]
            }
        }
    }
    
    # Process node
    results = orchestrator.process_node(
        node=target_node,
        algorithm_id="ai_knowledge_discovery"
    )
    
    # Print results
    for result in results:
        if result.success:
            print(f"Success - Agent {result.agent_name}:", result.result)
        else:
            print(f"Error - Agent {result.agent_name}:", result.error) 