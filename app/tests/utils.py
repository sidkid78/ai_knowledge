"""
Test utilities for UKG system.
"""
from typing import Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime

from app.core.persona_agent import Persona
from app.models.persona import AgentState

def create_test_node(
    label: str = "Test Node",
    pillar_level_id: str = "PL04",
    axis_values: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create a test knowledge node"""
    return {
        "id": str(uuid4()),
        "label": label,
        "pillar_level_id": pillar_level_id,
        "axis_values": axis_values or {
            "pillar_function": {
                "values": [0.9],
                "weights": [1.0]
            }
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

def create_test_agent(
    name: str = "Test Agent",
    domain_coverage: List[str] = None,
    algorithms_available: List[str] = None
) -> Persona:
    """Create a test persona agent"""
    return Persona(
        id=uuid4(),
        name=name,
        domain_coverage=domain_coverage or ["PL04"],
        algorithms_available=algorithms_available or ["ai_knowledge_discovery"]
    )

def create_test_result(
    agent_name: str = "Test Agent",
    confidence: float = 0.8,
    actions: List[str] = None,
    subcalls: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a test processing result"""
    return {
        "agent_id": str(uuid4()),
        "agent_name": agent_name,
        "confidence": confidence,
        "actions": actions or ["Applied algorithm"],
        "subcalls": subcalls or [],
        "timestamp": datetime.utcnow().isoformat()
    }

def validate_trace(
    trace: List[Dict[str, Any]],
    expected_depth: int = 0,
    expected_actions: List[str] = None
) -> bool:
    """
    Validate agent trace for proper recursion and actions.
    
    Args:
        trace: Agent learning trace
        expected_depth: Expected recursion depth
        expected_actions: Expected actions in trace
        
    Returns:
        bool: Whether trace is valid
    """
    if not trace:
        return False
    
    # Check trace structure
    for entry in trace:
        required_fields = [
            "timestamp", "action", "algorithm",
            "node_id", "confidence", "subcalls"
        ]
        if not all(field in entry for field in required_fields):
            return False
    
    # Check recursion depth
    max_depth = 0
    for entry in trace:
        subcalls = entry.get("subcalls", [])
        if subcalls:
            max_depth = max(max_depth, len(subcalls))
    if max_depth != expected_depth:
        return False
    
    # Check actions
    if expected_actions:
        # Get all unique actions
        trace_actions = set()
        for entry in trace:
            # Add the main action
            trace_actions.add(entry["action"])
            # Add actions from the actions list
            trace_actions.update(entry.get("actions", []))
            # Add actions from subcalls
            for subcall in entry.get("subcalls", []):
                trace_actions.update(subcall.get("actions", []))
        
        # Check that each expected action appears exactly once
        for action in expected_actions:
            matching_actions = [a for a in trace_actions if action in a]
            if len(matching_actions) != 1:
                return False
    
    return True

def validate_ensemble_results(
    results: List[Dict[str, Any]],
    min_agents: int = 2,
    required_metrics: List[str] = None
) -> bool:
    """
    Validate ensemble processing results.
    
    Args:
        results: List of agent results
        min_agents: Minimum number of agents required
        required_metrics: Required metrics in results
        
    Returns:
        bool: Whether results are valid
    """
    if len(results) < min_agents:
        return False
    
    # Check individual results
    for result in results:
        if "confidence" not in result:
            return False
    
    # Check metrics
    metrics = results[0].get("ensemble_metrics", {})
    required = required_metrics or [
        "agreement_score",
        "disagreement_level",
        "confidence_stats"
    ]
    if not all(metric in metrics for metric in required):
        return False
    
    return True

def validate_validation_results(
    results: List[Dict[str, Any]],
    required_validations: List[str] = None
) -> bool:
    """
    Validate validation results.
    
    Args:
        results: List of validation results
        required_validations: Required validation types
        
    Returns:
        bool: Whether results are valid
    """
    if not results:
        return False
    
    # Check validation types
    validation_types = [
        v.get("type")
        for r in results
        for v in r.get("validations", [])
    ]
    required = required_validations or [
        "knowledge_base",
        "statistical",
        "pattern"
    ]
    if not all(vtype in validation_types for vtype in required):
        return False
    
    # Check consensus
    consensus = results[0].get("consensus", {})
    if not consensus or "confidence" not in consensus:
        return False
    
    return True

def mock_algorithm_response(
    algorithm_id: str,
    confidence: float = 0.8,
    with_error: bool = False
) -> Dict[str, Any]:
    """Create a mock algorithm response"""
    if with_error:
        raise ValueError("Mock algorithm error")
    
    return {
        "algorithm_id": algorithm_id,
        "confidence": confidence,
        "output": {
            "prediction": 0.85,
            "features": ["feature1", "feature2"],
            "metadata": {
                "processing_time": 0.5,
                "model_version": "1.0"
            }
        }
    }

class MockResearchSource:
    """Mock research source for testing"""
    def __init__(
        self,
        source_type: str = "knowledge_base",
        success_rate: float = 0.8
    ):
        self.source_type = source_type
        self.success_rate = success_rate
        self.calls = []
    
    async def search(
        self,
        query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform mock search"""
        self.calls.append(query)
        
        if len(self.calls) * self.success_rate < len(self.calls):
            raise ValueError("Mock search error")
        
        return {
            "source": self.source_type,
            "results": [
                {
                    "id": str(uuid4()),
                    "relevance": 0.9,
                    "content": "Mock search result"
                }
            ],
            "metadata": {
                "total_results": 1,
                "processing_time": 0.2
            }
        }

class MockValidationService:
    """Mock validation service for testing"""
    def __init__(self, validation_type: str = "hybrid"):
        self.validation_type = validation_type
        self.validations = []
    
    async def validate(
        self,
        node: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Perform mock validation"""
        self.validations.append((node, context))
        
        return {
            "type": self.validation_type,
            "is_valid": True,
            "confidence": 0.85,
            "checks": [
                {
                    "name": "format_check",
                    "passed": True
                },
                {
                    "name": "content_check",
                    "passed": True
                }
            ]
        } 