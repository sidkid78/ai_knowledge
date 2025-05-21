from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.knowledge_node import KnowledgeNode
from app.models.knowledge_edge import KnowledgeEdge
from app.models.pillar_level import PillarLevel
from app.models.persona import PersonaAgent
from app.models.algorithm import Algorithm
from .session import SessionLocal

def create_initial_pillar_levels(db: Session) -> dict:
    """Create initial pillar level hierarchy"""
    pillars = {
        # Root domains
        'PL01': PillarLevel(
            id='PL01',
            name='Mathematics',
            description='Mathematical concepts and theories',
            domain_type='STEM',
            schema_extensions={
                'notation_systems': ['LaTeX', 'MathML'],
                'proof_requirements': True
            }
        ),
        'PL02': PillarLevel(
            id='PL02',
            name='Computer Science',
            description='Computing theory and practice',
            domain_type='STEM',
            schema_extensions={
                'programming_paradigms': True,
                'computational_complexity': True
            }
        ),
        'PL03': PillarLevel(
            id='PL03',
            name='Law',
            description='Legal frameworks and regulations',
            domain_type='Legal',
            schema_extensions={
                'jurisdiction': True,
                'precedent_tracking': True
            }
        ),
        
        # Mathematics sub-domains
        'PL04': PillarLevel(
            id='PL04',
            name='Algebra',
            description='Study of mathematical structures',
            domain_type='Mathematics',
            parent_id='PL01'
        ),
        'PL05': PillarLevel(
            id='PL05',
            name='Analysis',
            description='Study of continuous mathematical change',
            domain_type='Mathematics',
            parent_id='PL01'
        ),
        
        # Computer Science sub-domains
        'PL06': PillarLevel(
            id='PL06',
            name='Artificial Intelligence',
            description='Study of intelligent agents and systems',
            domain_type='Computer Science',
            parent_id='PL02'
        ),
        'PL07': PillarLevel(
            id='PL07',
            name='Quantum Computing',
            description='Computing using quantum phenomena',
            domain_type='Computer Science',
            parent_id='PL02',
            schema_extensions={
                'quantum_gates': True,
                'qubit_operations': True
            }
        )
    }
    
    for pillar in pillars.values():
        db.add(pillar)
    
    return pillars

def create_initial_algorithms(db: Session) -> dict:
    """Create initial algorithms"""
    algorithms = {
        'ai_discovery': Algorithm(
            id='ai_knowledge_discovery',
            name='AI Knowledge Discovery',
            description='Discovers AI knowledge by evaluating multiple axes',
            version='1.0',
            axis_parameters=[
                {'axis': 'pillar_function', 'required': True, 'weight': 1.0},
                {'axis': 'level_hierarchy', 'required': True, 'weight': 0.8}
            ],
            implementation_ref='app.core.algorithms.ai_knowledge_discovery'
        ),
        'risk_assessment': Algorithm(
            id='risk_assessment',
            name='Risk Assessment',
            description='Evaluates risks across multiple dimensions',
            version='1.0',
            axis_parameters=[
                {'axis': 'unified_system_function', 'required': True, 'weight': 1.0}
            ],
            implementation_ref='app.core.algorithms.risk_assessment'
        )
    }
    
    for algo in algorithms.values():
        db.add(algo)
    
    return algorithms

def create_initial_personas(db: Session) -> dict:
    """Create initial persona agents"""
    personas = {
        'math_expert': PersonaAgent(
            id=uuid4(),
            name='Mathematical Analysis Expert',
            domain_coverage=['PL01', 'PL04', 'PL05'],
            algorithms_available=['ai_knowledge_discovery'],
            running_state='idle',
            learning_trace=[]
        ),
        'quantum_expert': PersonaAgent(
            id=uuid4(),
            name='Quantum Computing Specialist',
            domain_coverage=['PL02', 'PL07'],
            algorithms_available=['ai_knowledge_discovery', 'risk_assessment'],
            running_state='idle',
            learning_trace=[]
        )
    }
    
    for persona in personas.values():
        db.add(persona)
    
    return personas

def create_initial_nodes(db: Session, pillars: dict) -> dict:
    """Create initial knowledge nodes"""
    nodes = {
        'quantum_basics': KnowledgeNode(
            id=uuid4(),
            label='Quantum Computing Fundamentals',
            description='Basic principles of quantum computing and qubits',
            pillar_level_id='PL07',
            axis_values={
                'pillar_function': {'values': [0.9], 'weights': [1.0]},
                'level_hierarchy': {'values': [1.0], 'time_deltas': [1.0]},
                'unified_system_function': {'values': [0.8], 'weights': [1.0]}
            }
        ),
        'algebra_basics': KnowledgeNode(
            id=uuid4(),
            label='Algebraic Structures',
            description='Fundamental concepts in abstract algebra',
            pillar_level_id='PL04',
            axis_values={
                'pillar_function': {'values': [0.85], 'weights': [1.0]},
                'level_hierarchy': {'values': [1.0], 'time_deltas': [1.0]}
            }
        )
    }
    
    for node in nodes.values():
        db.add(node)
    
    return nodes

def create_initial_edges(db: Session, nodes: dict) -> None:
    """Create initial knowledge edges"""
    edges = [
        KnowledgeEdge(
            id=uuid4(),
            from_node_id=nodes['algebra_basics'].id,
            to_node_id=nodes['quantum_basics'].id,
            relation_type='prerequisite',
            confidence=0.9,
            axis_values={
                'unified_system_function': {'values': [0.7], 'weights': [1.0]}
            }
        )
    ]
    
    for edge in edges:
        db.add(edge)

def seed_database() -> None:
    """Seed the database with initial data"""
    db = SessionLocal()
    try:
        # Create data in correct order (respecting foreign keys)
        pillars = create_initial_pillar_levels(db)
        algorithms = create_initial_algorithms(db)
        personas = create_initial_personas(db)
        nodes = create_initial_nodes(db, pillars)
        create_initial_edges(db, nodes)
        
        db.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database() 