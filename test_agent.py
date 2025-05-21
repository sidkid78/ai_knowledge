"""
Simple test script for the Persona agent.
"""
import asyncio
from uuid import uuid4
from app.core.persona_agent import Persona
from app.core.llm.azure_llm import AzureLLM
from app.core.config import settings

async def test_agent():
    """Test the Persona agent with a simple query"""
    
    # Initialize Azure LLM
    llm = AzureLLM()
    
    # Create test agent
    agent = Persona(
        id=uuid4(),
        name="Test Agent",
        domain_coverage=["PL04"],  # Quantum Computing domain
        algorithms_available=["ai_knowledge_discovery"]
    )
    
    # Create test node data
    node_data = {
        "id": str(uuid4()),
        "label": "Quantum Computing Fundamentals",
        "description": "Basic principles of quantum computing and qubits",
        "pillar_level_id": "PL04",
        "query": {
            "type": "knowledge_discovery",
            "focus": "quantum_principles"
        },
        "axis_values": {
            "complexity": {"values": [0.7]},
            "uncertainty": {"values": [0.4]},
            "impact": {"values": [0.8]},
            "temporal_axis": {"values": [0.5]},
            "confidence_axis": {"values": [0.6]}
        },
        "weights": {
            "complexity": 1.2,
            "uncertainty": 0.8,
            "impact": 1.0,
            "temporal_axis": 0.9,
            "confidence_axis": 1.1
        }
    }
    
    # Process query
    print("\nProcessing test query...")
    result = await agent.process_query(
        node=node_data,
        algorithm_id="ai_knowledge_discovery",
        pillar_levels_map={
            "PL04": {
                "name": "Quantum Computing",
                "description": "Quantum computing domain knowledge"
            }
        }
    )
    
    # Print results
    print("\nResults:")
    print(f"Confidence: {result.get('confidence', 'N/A')}")
    print("\nActions taken:")
    for action in result.get('actions', []):
        print(f"- {action}")
    
    print("\nLearning trace:")
    for trace in agent.learning_trace:
        print(f"- {trace}")
    
    if result.get('discoveries'):
        print("\nDiscoveries:")
        for discovery in result['discoveries']:
            print(f"- {discovery}")

if __name__ == "__main__":
    asyncio.run(test_agent()) 