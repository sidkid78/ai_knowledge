"""
Tests for agent recursion and validation.
"""
import pytest
from uuid import uuid4
from datetime import datetime

from app.core.persona_agent import Persona
from app.core.orchestrator import Orchestrator
from app.core.tasks.background_manager import BackgroundManager, TaskType, TaskStatus
from app.models.persona import AgentState
# Use TestingSessionLocal from conftest for test-specific session handling
# from app.db.session import SessionLocal 
from app.tests.conftest import TestingSessionLocal as SessionLocal 
from app.models.knowledge_node import KnowledgeNode
from app.models.pillar_level import PillarLevel
from app.tests.utils import (
    create_test_node,
    create_test_agent,
    create_test_result,
    validate_trace,
    validate_ensemble_results,
    validate_validation_results,
    mock_algorithm_response,
    MockResearchSource,
    MockValidationService
)

@pytest.fixture(scope="function")
def setup_database():
    """Set up test database for each function, ensuring cleanup."""
    db = SessionLocal()
    try:
        # Ensure clean state before test
        existing_pillar = db.query(PillarLevel).filter(PillarLevel.id == "PL04").first()
        if existing_pillar:
            db.delete(existing_pillar)
            db.commit()
            
        # Create test pillar level for the test
        pillar = PillarLevel(
            id="PL04",
            name="Test Pillar",
            description="Test domain",
            domain_type="test"
        )
        db.add(pillar)
        db.commit()
        db.refresh(pillar) # Ensure the object is up-to-date
        
        yield db # Provide the db session to the test function
        
    finally:
        # Clean up after test
        db.rollback() # Rollback any uncommitted changes from the test itself
        
        # Delete dependent nodes first
        dependent_nodes = db.query(KnowledgeNode).filter(KnowledgeNode.pillar_level_id == "PL04").all()
        for node in dependent_nodes:
            db.delete(node)
        db.commit() # Commit node deletions
        
        # Now delete the pillar level
        existing_pillar = db.query(PillarLevel).filter(PillarLevel.id == "PL04").first()
        if existing_pillar:
            db.delete(existing_pillar)
            db.commit()
            
        db.close()

@pytest.fixture
def test_node(setup_database):
    """Create a test node"""
    node_dict = create_test_node()
    
    # Create node in database
    db = SessionLocal()
    try:
        node = KnowledgeNode(
            id=node_dict["id"],
            label=node_dict["label"],
            pillar_level_id=node_dict["pillar_level_id"],
            axis_values=node_dict["axis_values"]
        )
        db.add(node)
        db.commit()
    finally:
        db.close()
    
    return node_dict

@pytest.fixture
def test_agent():
    """Create a test agent"""
    return create_test_agent()

@pytest.fixture
def orchestrator():
    """Create test orchestrator"""
    algorithm_options = {
        "ai_knowledge_discovery": {
            "name": "AI Knowledge Discovery",
            "parameters": {}
        }
    }
    pillar_map = {
        "PL04": {
            "name": "Quantum Computing",
            "description": "Test domain"
        }
    }
    return Orchestrator(algorithm_options, pillar_map)

@pytest.fixture
def background_manager(orchestrator):
    """Create test background manager"""
    return BackgroundManager(orchestrator)

def test_agent_missing_axis(test_agent, test_node):
    """Test agent handling of missing axis"""
    # Remove required axis
    test_node["axis_values"] = {}
    
    # Process node
    result = test_agent.process_query(
        node=test_node,
        algorithm_id="ai_knowledge_discovery",
        pillar_levels_map={}
    )
    
    # Validate trace
    assert validate_trace(
        test_agent.learning_trace,
        expected_depth=1,
        expected_actions=["Gap detected - missing required axis"]
    )
    
    # Check recursive processing
    assert len(result["subcalls"]) > 0
    assert result["actions"][-1] == "Attempted axis imputation"

def test_agent_unknown_pillar(test_agent, test_node):
    """Test agent handling of unknown pillar"""
    # Set unknown pillar
    test_node["pillar_level_id"] = "PL99"
    
    # Process node
    result = test_agent.process_query(
        node=test_node,
        algorithm_id="ai_knowledge_discovery",
        pillar_levels_map={}
    )
    
    # Validate trace
    assert validate_trace(
        test_agent.learning_trace,
        expected_depth=1,
        expected_actions=["Domain expertise gap detected"]
    )
    
    # Check peer escalation
    assert any(
        "Escalating to peer agent" in action
        for action in result["actions"]
    )

def test_agent_failed_algorithm(test_agent, test_node):
    """Test agent handling of algorithm failure"""
    # Set up mock algorithm that fails
    test_agent.algorithms_available = ["failing_algorithm"]
    
    # Process node
    result = test_agent.process_query(
        node=test_node,
        algorithm_id="failing_algorithm",
        pillar_levels_map={}
    )
    
    # Validate trace
    assert validate_trace(
        test_agent.learning_trace,
        expected_depth=1,
        expected_actions=["Algorithm execution failed", "Attempting alternate algorithm"]
    )
    
    # Check recovery attempt
    assert result["error"] is not None
    assert len(result["subcalls"]) > 0

@pytest.mark.asyncio
async def test_ensemble_reasoning(background_manager, test_node):
    """Test ensemble reasoning with multiple agents"""
    # Create multiple test agents
    agents = [
        create_test_agent(f"Agent {i}")
        for i in range(3)
    ]
    background_manager.orchestrator.agents = agents
    
    # Schedule ensemble task
    task_id = await background_manager.schedule_task(
        TaskType.ENSEMBLE,
        test_node["id"],
        {
            "algorithm_id": "ai_knowledge_discovery",
            "ensemble_size": 3
        }
    )
    
    # Process task
    await background_manager._process_task(task_id)
    task = background_manager.tasks[task_id]
    
    # Validate results
    assert task.status == TaskStatus.COMPLETED
    assert validate_ensemble_results(
        task.result["individual_results"],
        min_agents=3
    )

@pytest.mark.asyncio
async def test_validation_chain(background_manager, test_node):
    """Test validation chain with multiple methods"""
    # Set up mock validation service
    validation_service = MockValidationService()
    background_manager.validation_service = validation_service
    
    # Schedule validation task
    task_id = await background_manager.schedule_task(
        TaskType.VALIDATION,
        test_node["id"],
        {
            "algorithm_id": "ai_knowledge_discovery",
            "validation_type": "hybrid"
        }
    )
    
    # Process task
    await background_manager._process_task(task_id)
    task = background_manager.tasks[task_id]
    
    # Validate results
    assert task.status == TaskStatus.COMPLETED
    assert task.result is not None
    assert "validations" in task.result
    assert len(task.result["validations"]) > 0
    assert all(
        v.get("type") in ["knowledge_base", "statistical", "pattern"]
        for v in task.result["validations"]
    )

@pytest.mark.asyncio
async def test_research_enrichment(background_manager, test_node):
    """Test research leading to enrichment"""
    # Set up mock research source
    research_source = MockResearchSource()
    background_manager.research_source = research_source
    
    # Schedule research task
    task_id = await background_manager.schedule_task(
        TaskType.RESEARCH,
        test_node["id"],
        {
            "algorithm_id": "ai_knowledge_discovery",
            "depth": 2
        }
    )
    
    # Process task
    await background_manager._process_task(task_id)
    task = background_manager.tasks[task_id]
    
    # Validate results
    assert task.status == TaskStatus.COMPLETED
    assert task.result is not None
    assert "findings" in task.result
    assert len(task.result["findings"]) > 0
    assert all(
        isinstance(f, dict) and "relevance" in f
        for f in task.result["findings"]
    )

def test_trace_inspection(test_agent, test_node):
    """Test comprehensive trace inspection"""
    # Process node with various conditions
    result = test_agent.process_query(
        node=test_node,
        algorithm_id="ai_knowledge_discovery",
        pillar_levels_map={},
        max_recursion=3
    )
    
    # Validate trace structure
    trace = test_agent.learning_trace
    assert all(
        isinstance(entry, dict) and
        "timestamp" in entry and
        "action" in entry and
        "confidence" in entry
        for entry in trace
    )
    
    # Check recursion tracking
    recursion_depths = [
        len(entry.get("subcalls", []))
        for entry in trace
    ]
    if recursion_depths:
        assert max(recursion_depths) <= 3
    
    # Check action sequence
    actions = [
        action
        for entry in trace
        for action in entry.get("actions", [])
    ]
    if actions:
        assert any(
            "algorithm" in action.lower()
            for action in actions
        )

def test_error_recovery(test_agent, test_node):
    """Test error recovery and fallback mechanisms"""
    # Simulate cascading failures
    def failing_process():
        raise ValueError("Simulated process failure")
    
    test_agent._apply_algorithm = failing_process
    
    # Process node
    result = test_agent.process_query(
        node=test_node,
        algorithm_id="ai_knowledge_discovery",
        pillar_levels_map={}
    )
    
    # Check error handling
    assert result["error"] is not None
    assert test_agent.state == AgentState.ERROR
    
    # Validate error actions
    trace = test_agent.learning_trace
    error_actions = [
        action
        for entry in trace
        for action in entry.get("actions", [])
        if "error" in action.lower() or "failed" in action.lower()
    ]
    assert len(error_actions) > 0

@pytest.mark.asyncio
async def test_concurrent_processing(background_manager, test_node):
    """Test concurrent processing with multiple tasks"""
    # Schedule multiple tasks
    task_ids = []
    for _ in range(background_manager.max_concurrent + 2):
        task_id = await background_manager.schedule_task(
            TaskType.RESEARCH,
            test_node["id"],
            {"algorithm_id": "ai_knowledge_discovery"}
        )
        task_ids.append(task_id)
    
    # Process tasks
    for task_id in task_ids:
        await background_manager._process_task(task_id)
    
    # Check concurrent execution
    running_tasks = len(background_manager.running_tasks)
    assert running_tasks <= background_manager.max_concurrent
    
    # Check task completion
    tasks = list(background_manager.tasks.values())
    assert len(tasks) > 0
    assert all(task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] for task in tasks) 