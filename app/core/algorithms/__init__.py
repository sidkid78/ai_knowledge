"""
Composable algorithms for the UKG system.
"""
from .knowledge_discovery import ai_knowledge_discovery
from .risk_assessment import assess_risk

ALGORITHMS = {
    'ai_knowledge_discovery': ai_knowledge_discovery,
    'assess_risk': assess_risk
}

__all__ = ['ALGORITHMS', 'ai_knowledge_discovery', 'assess_risk'] 