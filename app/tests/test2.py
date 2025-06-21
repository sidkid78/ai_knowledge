"""
Comprehensive test suite for UKG core functionality including:
- Data model validation
- API endpoint integration
- Algorithmic reasoning
- Agent recursion
- Edge case handling
"""
import pytest
from uuid import UUID
from fastapi.testclient import TestClient
from app.main import app
from app.models import KnowledgeNodeCreate, KnowledgeNodeUpdate
from app.schemas import PillarLevel
from app.core.persona_agent import Persona
from app.core.algorithms import pillar_function, ai_knowledge_discovery
from app.core.config import settings

# Fixtures
@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)

@pytest.fixture
def sample_node_data():
    return {
        "label": "Quantum Entanglement Basics",
        "description": "Fundamentals of quantum entanglement phenomena",
        "pillar_level_id": "PL04",
        "axis_values": {
            "complexity": {"values": [0.8], "weights": [1.2]},
            "temporal_axis": {"values": [0.6], "weights": [0.9]}
        }
    }

# Test Classes
class TestDataModels:
    """Test core data model validation"""
    
    def test_valid_node_creation(self, sample_node_data):
        node = KnowledgeNodeCreate(**sample_node_data)
        assert UUID(node.id, version=4)  # Validate UUID4
        assert node.label == sample_node_data["label"]
        
    def test_invalid_pillar_level(self):
        with pytest.raises(ValueError):
            PillarLevel(id="PL99", name="Invalid Pillar")

class TestAPIEndpoints:
    """Test CRUD operations through API endpoints"""
    
    @pytest.mark.asyncio
    async def test_node_lifecycle(self, test_client, sample_node_data):
        # Create
        response = test_client.post("/nodes/", json=sample_node_data)
        assert response.status_code == 201
        node_id = response.json()["id"]
        
        # Read
        response = test_client.get(f"/nodes/{node_id}")
        assert response.status_code == 200
        assert response.json()["label"] == sample_node_data["label"]
        
        # Update
        update_data = KnowledgeNodeUpdate(description="Updated description")
        response = test_client.patch(f"/nodes/{node_id}", json=update_data.dict())
        assert response.status_code == 200
        assert response.json()["description"] == "Updated description"
        
        # Delete
        response = test_client.delete(f"/nodes/{node_id}")
        assert response.status_code == 204

class TestAlgorithms:
    """Test core algorithmic functionality"""
    
    @pytest.mark.parametrize("weights,values,expected", [
        ([1.0, 0.5], [0.8, 0.6], 1.1),
        ([0.0, 1.0], [0.5, 0.5], 0.5),
        ([], [], 0.0)  # Edge case
    ])
    def test_pillar_function(self, weights, values, expected):
        assert pillar_function(weights, values) == pytest.approx(expected, rel=1e-3)
        
    @pytest.mark.asyncio
    async def test_knowledge_discovery(self, sample_node_data):
        result = await ai_knowledge_discovery(
            node_data=sample_node_data,
            weights={"complexity": 1.2, "temporal_axis": 0.9},
            parameters={"confidence_threshold": 0.7}
        )
        assert 0 <= result["confidence"] <= 1
        assert "reasoning_steps" in result

class TestAgentSystem:
    """Test persona agent functionality"""
    
    @pytest.fixture
    def test_agent(self):
        return Persona(
            id=uuid4(),
            name="Test Agent",
            domain_coverage=["PL04"],
            algorithms_available=["ai_knowledge_discovery"]
        )
    
    @pytest.mark.asyncio
    async def test_agent_processing(self, test_agent, sample_node_data):
        result = await test_agent.process_query(
            node=sample_node_data,
            algorithm_id="ai_knowledge_discovery",
            max_recursion=2
        )
        assert "primary_result" in result
        assert len(result["subcalls"]) <= 2  # Verify recursion limit
        
    @pytest.mark.asyncio
    async def test_agent_error_handling(self, test_agent):
        with pytest.raises(ValueError):
            await test_agent.process_query(
                node={},
                algorithm_id="invalid_algorithm",
                max_recursion=0
            )

class TestEdgeCases:
    """Test boundary conditions and error scenarios"""
    
    @pytest.mark.asyncio
    async def test_invalid_axis_values(self, test_client):
        invalid_data = {
            "label": "Invalid Node",
            "pillar_level_id": "PL04",
            "axis_values": {"invalid_axis": {"values": [2.0]}}  # Value > 1.0
        }
        response = test_client.post("/nodes/", json=invalid_data)
        assert response.status_code == 422
        
    @pytest.mark.asyncio
    async def test_algorithm_failure(self, sample_node_data):
        with pytest.raises(RuntimeError):
            await ai_knowledge_discovery(
                node_data={**sample_node_data, "axis_values": {}},
                weights={},
                parameters={"invalid_param": True}
            )
            
    @pytest.mark.asyncio
    async def test_max_recursion_depth(self, test_agent, sample_node_data):
        result = await test_agent.process_query(
            node=sample_node_data,
            algorithm_id="ai_knowledge_discovery",
            max_recursion=5
        )
        assert len(result["subcalls"]) == 5
        assert "max_recursion_reached" in result["subcalls"][-1]["status"]
