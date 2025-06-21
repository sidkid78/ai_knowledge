from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.knowledge_node import KnowledgeNode
from app.models.knowledge_edge import KnowledgeEdge
from app.models.pillar_level import PillarLevel
from app.models.persona import PersonaAgent, AgentState
from app.models.algorithm import Algorithm
from .session import SessionLocal
from typing import Dict

def create_initial_pillar_levels(db: Session) -> Dict[str, PillarLevel]:
    """Create the complete 87 UKG Pillar Levels"""
    
    # The complete 87 UKG Pillar Levels organized by domains
    pillar_data = [
        # Mathematics & Logic (PL01-PL10)
        {"id": "PL01", "name": "Pure Mathematics", "description": "Abstract mathematical concepts, number theory, algebra", "parent": None, "domain_type": "mathematical"},
        {"id": "PL02", "name": "Applied Mathematics", "description": "Mathematical modeling, optimization, statistics", "parent": "PL01", "domain_type": "mathematical"},
        {"id": "PL03", "name": "Logic & Proof Theory", "description": "Formal logic, proof systems, computational logic", "parent": "PL01", "domain_type": "mathematical"},
        {"id": "PL04", "name": "Geometry & Topology", "description": "Spatial mathematics, geometric structures", "parent": "PL01", "domain_type": "mathematical"},
        {"id": "PL05", "name": "Calculus & Analysis", "description": "Differential and integral calculus, real analysis", "parent": "PL01", "domain_type": "mathematical"},
        {"id": "PL06", "name": "Discrete Mathematics", "description": "Combinatorics, graph theory, discrete structures", "parent": "PL01", "domain_type": "mathematical"},
        {"id": "PL07", "name": "Probability & Statistics", "description": "Stochastic processes, statistical inference", "parent": "PL02", "domain_type": "mathematical"},
        {"id": "PL08", "name": "Numerical Methods", "description": "Computational mathematics, numerical algorithms", "parent": "PL02", "domain_type": "mathematical"},
        {"id": "PL09", "name": "Mathematical Physics", "description": "Mathematics applied to physical phenomena", "parent": "PL02", "domain_type": "mathematical"},
        {"id": "PL10", "name": "Operations Research", "description": "Optimization, decision theory, game theory", "parent": "PL02", "domain_type": "mathematical"},

        # Computer Science & Technology (PL11-PL20)
        {"id": "PL11", "name": "Computer Science Fundamentals", "description": "Algorithms, data structures, computational theory", "parent": None, "domain_type": "computational"},
        {"id": "PL12", "name": "Software Engineering", "description": "Software design, development methodologies", "parent": "PL11", "domain_type": "computational"},
        {"id": "PL13", "name": "Artificial Intelligence", "description": "Machine learning, neural networks, AI systems", "parent": "PL11", "domain_type": "computational"},
        {"id": "PL14", "name": "Database Systems", "description": "Data management, query processing, storage", "parent": "PL11", "domain_type": "computational"},
        {"id": "PL15", "name": "Computer Networks", "description": "Network protocols, distributed systems", "parent": "PL11", "domain_type": "computational"},
        {"id": "PL16", "name": "Cybersecurity", "description": "Information security, cryptography, threat analysis", "parent": "PL11", "domain_type": "computational"},
        {"id": "PL17", "name": "Human-Computer Interaction", "description": "User interfaces, usability, interaction design", "parent": "PL11", "domain_type": "computational"},
        {"id": "PL18", "name": "Computer Graphics", "description": "Visualization, rendering, computer vision", "parent": "PL11", "domain_type": "computational"},
        {"id": "PL19", "name": "Quantum Computing", "description": "Quantum algorithms, quantum information theory", "parent": "PL11", "domain_type": "computational"},
        {"id": "PL20", "name": "Bioinformatics", "description": "Computational biology, genomics, biodata analysis", "parent": "PL11", "domain_type": "computational"},

        # Physical Sciences (PL21-PL30)
        {"id": "PL21", "name": "Physics", "description": "Fundamental physical laws and phenomena", "parent": None, "domain_type": "physical"},
        {"id": "PL22", "name": "Classical Mechanics", "description": "Newtonian mechanics, dynamics, statics", "parent": "PL21", "domain_type": "physical"},
        {"id": "PL23", "name": "Quantum Mechanics", "description": "Quantum theory, wave functions, particle physics", "parent": "PL21", "domain_type": "physical"},
        {"id": "PL24", "name": "Thermodynamics", "description": "Heat, energy, statistical mechanics", "parent": "PL21", "domain_type": "physical"},
        {"id": "PL25", "name": "Electromagnetism", "description": "Electric and magnetic fields, electromagnetic waves", "parent": "PL21", "domain_type": "physical"},
        {"id": "PL26", "name": "Relativity", "description": "Special and general relativity, spacetime", "parent": "PL21", "domain_type": "physical"},
        {"id": "PL27", "name": "Astronomy & Astrophysics", "description": "Celestial mechanics, stellar physics, cosmology", "parent": "PL21", "domain_type": "physical"},
        {"id": "PL28", "name": "Chemistry", "description": "Molecular structure, chemical reactions, materials", "parent": None, "domain_type": "physical"},
        {"id": "PL29", "name": "Materials Science", "description": "Material properties, nanotechnology, engineering materials", "parent": "PL28", "domain_type": "physical"},
        {"id": "PL30", "name": "Earth Sciences", "description": "Geology, meteorology, environmental science", "parent": None, "domain_type": "physical"},

        # Life Sciences (PL31-PL40)
        {"id": "PL31", "name": "Biology", "description": "Living organisms, biological processes", "parent": None, "domain_type": "biological"},
        {"id": "PL32", "name": "Molecular Biology", "description": "DNA, RNA, proteins, cellular mechanisms", "parent": "PL31", "domain_type": "biological"},
        {"id": "PL33", "name": "Genetics", "description": "Heredity, genomics, genetic engineering", "parent": "PL31", "domain_type": "biological"},
        {"id": "PL34", "name": "Ecology", "description": "Ecosystems, environmental interactions, biodiversity", "parent": "PL31", "domain_type": "biological"},
        {"id": "PL35", "name": "Evolutionary Biology", "description": "Evolution, natural selection, phylogenetics", "parent": "PL31", "domain_type": "biological"},
        {"id": "PL36", "name": "Neuroscience", "description": "Brain function, neural networks, cognition", "parent": "PL31", "domain_type": "biological"},
        {"id": "PL37", "name": "Medicine", "description": "Human health, disease, medical treatment", "parent": "PL31", "domain_type": "biological"},
        {"id": "PL38", "name": "Pharmacology", "description": "Drug action, therapeutics, toxicology", "parent": "PL37", "domain_type": "biological"},
        {"id": "PL39", "name": "Biotechnology", "description": "Applied biology, bioengineering, synthetic biology", "parent": "PL31", "domain_type": "biological"},
        {"id": "PL40", "name": "Agricultural Science", "description": "Crop science, livestock, sustainable agriculture", "parent": "PL31", "domain_type": "biological"},

        # Social Sciences (PL41-PL50)
        {"id": "PL41", "name": "Psychology", "description": "Human behavior, cognition, mental processes", "parent": None, "domain_type": "social"},
        {"id": "PL42", "name": "Sociology", "description": "Social structures, institutions, group behavior", "parent": None, "domain_type": "social"},
        {"id": "PL43", "name": "Anthropology", "description": "Human culture, evolution, social organization", "parent": None, "domain_type": "social"},
        {"id": "PL44", "name": "Economics", "description": "Markets, financial systems, economic theory", "parent": None, "domain_type": "social"},
        {"id": "PL45", "name": "Political Science", "description": "Government, policy, political systems", "parent": None, "domain_type": "social"},
        {"id": "PL46", "name": "International Relations", "description": "Global politics, diplomacy, international law", "parent": "PL45", "domain_type": "social"},
        {"id": "PL47", "name": "Public Policy", "description": "Policy analysis, governance, public administration", "parent": "PL45", "domain_type": "social"},
        {"id": "PL48", "name": "Education", "description": "Learning theory, pedagogy, educational systems", "parent": None, "domain_type": "social"},
        {"id": "PL49", "name": "Communication Studies", "description": "Media, rhetoric, information theory", "parent": None, "domain_type": "social"},
        {"id": "PL50", "name": "Urban Planning", "description": "City design, infrastructure, regional development", "parent": None, "domain_type": "social"},

        # Humanities (PL51-PL60)
        {"id": "PL51", "name": "Philosophy", "description": "Logic, ethics, metaphysics, epistemology", "parent": None, "domain_type": "humanities"},
        {"id": "PL52", "name": "Ethics", "description": "Moral philosophy, applied ethics, bioethics", "parent": "PL51", "domain_type": "humanities"},
        {"id": "PL53", "name": "History", "description": "Historical analysis, historiography, cultural history", "parent": None, "domain_type": "humanities"},
        {"id": "PL54", "name": "Literature", "description": "Literary analysis, creative writing, comparative literature", "parent": None, "domain_type": "humanities"},
        {"id": "PL55", "name": "Linguistics", "description": "Language structure, phonetics, syntax, semantics", "parent": None, "domain_type": "humanities"},
        {"id": "PL56", "name": "Art History", "description": "Visual arts, artistic movements, cultural aesthetics", "parent": None, "domain_type": "humanities"},
        {"id": "PL57", "name": "Music Theory", "description": "Musical composition, harmony, acoustic principles", "parent": None, "domain_type": "humanities"},
        {"id": "PL58", "name": "Religious Studies", "description": "Theology, comparative religion, spiritual traditions", "parent": None, "domain_type": "humanities"},
        {"id": "PL59", "name": "Cultural Studies", "description": "Cultural theory, identity, social movements", "parent": None, "domain_type": "humanities"},
        {"id": "PL60", "name": "Archaeology", "description": "Material culture, historical reconstruction", "parent": "PL53", "domain_type": "humanities"},

        # Applied Sciences & Engineering (PL61-PL70)
        {"id": "PL61", "name": "Engineering", "description": "Applied science, design, construction", "parent": None, "domain_type": "engineering"},
        {"id": "PL62", "name": "Mechanical Engineering", "description": "Machines, thermodynamics, manufacturing", "parent": "PL61", "domain_type": "engineering"},
        {"id": "PL63", "name": "Electrical Engineering", "description": "Electronics, power systems, signal processing", "parent": "PL61", "domain_type": "engineering"},
        {"id": "PL64", "name": "Civil Engineering", "description": "Infrastructure, structures, transportation", "parent": "PL61", "domain_type": "engineering"},
        {"id": "PL65", "name": "Chemical Engineering", "description": "Process design, reaction engineering, separation", "parent": "PL61", "domain_type": "engineering"},
        {"id": "PL66", "name": "Aerospace Engineering", "description": "Aircraft, spacecraft, propulsion systems", "parent": "PL61", "domain_type": "engineering"},
        {"id": "PL67", "name": "Biomedical Engineering", "description": "Medical devices, biomechanics, tissue engineering", "parent": "PL61", "domain_type": "engineering"},
        {"id": "PL68", "name": "Environmental Engineering", "description": "Pollution control, sustainability, green technology", "parent": "PL61", "domain_type": "engineering"},
        {"id": "PL69", "name": "Industrial Engineering", "description": "Systems optimization, quality control, logistics", "parent": "PL61", "domain_type": "engineering"},
        {"id": "PL70", "name": "Nuclear Engineering", "description": "Nuclear technology, radiation, reactor design", "parent": "PL61", "domain_type": "engineering"},

        # Business & Management (PL71-PL77)
        {"id": "PL71", "name": "Business Administration", "description": "Management, strategy, organizational behavior", "parent": None, "domain_type": "business"},
        {"id": "PL72", "name": "Finance", "description": "Investment, risk management, financial markets", "parent": "PL71", "domain_type": "business"},
        {"id": "PL73", "name": "Marketing", "description": "Consumer behavior, branding, market research", "parent": "PL71", "domain_type": "business"},
        {"id": "PL74", "name": "Operations Management", "description": "Supply chain, production, quality management", "parent": "PL71", "domain_type": "business"},
        {"id": "PL75", "name": "Entrepreneurship", "description": "Innovation, startup development, venture capital", "parent": "PL71", "domain_type": "business"},
        {"id": "PL76", "name": "Human Resources", "description": "Personnel management, organizational development", "parent": "PL71", "domain_type": "business"},
        {"id": "PL77", "name": "Information Systems", "description": "Business technology, data analytics, digital transformation", "parent": "PL71", "domain_type": "business"},

        # Law & Governance (PL78-PL82)
        {"id": "PL78", "name": "Law", "description": "Legal systems, jurisprudence, legal theory", "parent": None, "domain_type": "legal"},
        {"id": "PL79", "name": "Constitutional Law", "description": "Government structure, civil rights, constitutional interpretation", "parent": "PL78", "domain_type": "legal"},
        {"id": "PL80", "name": "Criminal Law", "description": "Criminal justice, procedure, evidence", "parent": "PL78", "domain_type": "legal"},
        {"id": "PL81", "name": "Commercial Law", "description": "Business law, contracts, intellectual property", "parent": "PL78", "domain_type": "legal"},
        {"id": "PL82", "name": "International Law", "description": "Treaties, human rights, global governance", "parent": "PL78", "domain_type": "legal"},

        # Interdisciplinary & Emerging Fields (PL83-PL87)
        {"id": "PL83", "name": "Systems Science", "description": "Complex systems, network theory, emergence", "parent": None, "domain_type": "interdisciplinary"},
        {"id": "PL84", "name": "Cognitive Science", "description": "Mind, consciousness, artificial cognition", "parent": None, "domain_type": "interdisciplinary"},
        {"id": "PL85", "name": "Data Science", "description": "Big data, machine learning, predictive analytics", "parent": None, "domain_type": "interdisciplinary"},
        {"id": "PL86", "name": "Sustainability Science", "description": "Environmental policy, renewable energy, climate science", "parent": None, "domain_type": "interdisciplinary"},
        {"id": "PL87", "name": "Digital Humanities", "description": "Technology in humanities, digital scholarship", "parent": None, "domain_type": "interdisciplinary"}
    ]

    pillars = {}
    
    for pillar_info in pillar_data:
        pillar = PillarLevel(
            id=pillar_info["id"],
            name=pillar_info["name"],
            description=pillar_info["description"],
            parent_id=pillar_info["parent"],
            domain_type=pillar_info["domain_type"]
        )
        
        # Check if pillar already exists
        existing = db.query(PillarLevel).filter(PillarLevel.id == pillar.id).first()
        if not existing:
            db.add(pillar)
            pillars[pillar.id] = pillar
        else:
            pillars[pillar.id] = existing
    
    db.commit()
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
            state=AgentState.IDLE,
            learning_trace=[]
        ),
        'quantum_expert': PersonaAgent(
            id=uuid4(),
            name='Quantum Computing Specialist',
            domain_coverage=['PL02', 'PL07'],
            algorithms_available=['ai_knowledge_discovery', 'risk_assessment'],
            state=AgentState.IDLE,
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
        # Check if data already exists
        existing_algorithms = db.query(Algorithm).first()
        if existing_algorithms:
            print("Database already seeded, skipping...")
            return
        
        print("Seeding database with initial data...")
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