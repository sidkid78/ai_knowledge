"""
Demonstration of the Universal Knowledge Graph (UKG) system capabilities.
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.knowledge_node import KnowledgeNode
from app.models.algorithm import Algorithm
from app.models.persona import PersonaAgent
from app.models.pillar_level import PillarLevel
from app.core.algorithms import ai_knowledge_discovery, assess_risk

def demonstrate_knowledge_discovery(db: Session):
    """Demonstrate AI knowledge discovery capabilities"""
    print("\n=== AI Knowledge Discovery Demo ===")
    
    # Get our quantum computing node
    quantum_node = db.query(KnowledgeNode).filter(
        KnowledgeNode.label == 'Quantum Computing Fundamentals'
    ).first()
    
    if not quantum_node:
        print("Error: Quantum Computing node not found!")
        return
        
    print(f"\nAnalyzing node: {quantum_node.label}")
    print(f"Description: {quantum_node.description}")
    print("\nAxis Values:")
    for axis, values in quantum_node.axis_values.items():
        print(f"- {axis}: {values}")
    
    # Get and run the AI discovery algorithm
    ai_algo = db.query(Algorithm).filter(
        Algorithm.id == 'ai_knowledge_discovery'
    ).first()
    
    if not ai_algo:
        print("Error: AI Discovery algorithm not found!")
        return
        
    print(f"\nRunning algorithm: {ai_algo.name}")
    
    results = ai_knowledge_discovery(quantum_node, {"axis_parameters": ai_algo.axis_parameters})
    
    print("\nResults:")
    print(f"Confidence: {results['confidence']:.2f}")
    print("Axis Contributions:")
    for axis, contribution in results['axis_contributions'].items():
        print(f"- {axis}: {contribution:.2f}")
    
    if results['discoveries']:
        print("\nDiscoveries:")
        for discovery in results['discoveries']:
            print(f"- {discovery}")

def demonstrate_risk_assessment(db: Session):
    """Demonstrate risk assessment capabilities"""
    print("\n=== Risk Assessment Demo ===")
    
    # Get our quantum computing node
    quantum_node = db.query(KnowledgeNode).filter(
        KnowledgeNode.label == 'Quantum Computing Fundamentals'
    ).first()
    
    if not quantum_node:
        print("Error: Quantum Computing node not found!")
        return
    
    # Get and run the risk assessment algorithm
    risk_algo = db.query(Algorithm).filter(
        Algorithm.id == 'risk_assessment'
    ).first()
    
    if not risk_algo:
        print("Error: Risk Assessment algorithm not found!")
        return
        
    print(f"\nAssessing risks for: {quantum_node.label}")
    
    results = assess_risk(quantum_node, {"axis_parameters": risk_algo.axis_parameters})
    
    print("\nResults:")
    print(f"Risk Level: {results['risk_level']:.2f}")
    print(f"Risk Factors: {', '.join(results['risk_factors'])}")
    print("\nAxis Risks:")
    for axis, risk in results['axis_risks'].items():
        print(f"- {axis}: {risk:.2f}")

def demonstrate_persona_capabilities(db: Session):
    """Demonstrate persona agent capabilities"""
    print("\n=== Persona Agent Demo ===")
    
    # Get our quantum computing specialist
    persona = db.query(PersonaAgent).filter(PersonaAgent.name == "Quantum Computing Specialist").first()
    
    if not persona:
        print("Error: Quantum Computing Specialist not found!")
        return
    
    print(f"\nPersona: {persona.name}")
    print(f"State: {persona.state}")
    print("\nDomain Coverage:")
    
    # Get domain names
    domains = db.query(PillarLevel).filter(
        PillarLevel.id.in_(persona.domain_coverage)
    ).all()
    
    for domain in domains:
        print(f"- {domain.name} ({domain.id})")
    
    print("\nAvailable Algorithms:")
    algorithms = db.query(Algorithm).filter(
        Algorithm.id.in_(persona.algorithms_available)
    ).all()
    
    for algo in algorithms:
        print(f"- {algo.name} (v{algo.version})")

def run_demo():
    """Run all demonstrations"""
    db = SessionLocal()
    try:
        demonstrate_knowledge_discovery(db)
        demonstrate_risk_assessment(db)
        demonstrate_persona_capabilities(db)
    finally:
        db.close()

if __name__ == "__main__":
    run_demo() 