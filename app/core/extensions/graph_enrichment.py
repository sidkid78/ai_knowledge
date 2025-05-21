"""
Utilities for recursive learning and graph enrichment.
"""
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.knowledge_node import KnowledgeNode
from app.models.knowledge_edge import KnowledgeEdge
from app.models.pillar_level import PillarLevel
from app.models.persona import PersonaAgent
from app.core.algorithms.patterns import (
    AlgorithmInput,
    AlgorithmOutput,
    GraphPattern
)

class KnowledgeGraph(GraphPattern[KnowledgeNode]):
    """Implementation of graph operations for knowledge nodes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_neighbors(self, node: KnowledgeNode) -> List[KnowledgeNode]:
        """Get connected nodes"""
        # Get outgoing edges
        outgoing = (
            self.db.query(KnowledgeEdge)
            .filter(KnowledgeEdge.from_node_id == node.id)
            .all()
        )
        
        # Get incoming edges
        incoming = (
            self.db.query(KnowledgeEdge)
            .filter(KnowledgeEdge.to_node_id == node.id)
            .all()
        )
        
        # Get connected nodes
        neighbor_ids = set()
        for edge in outgoing:
            neighbor_ids.add(edge.to_node_id)
        for edge in incoming:
            neighbor_ids.add(edge.from_node_id)
            
        return (
            self.db.query(KnowledgeNode)
            .filter(KnowledgeNode.id.in_(neighbor_ids))
            .all()
        )
    
    def get_edges(self, node: KnowledgeNode) -> List[KnowledgeEdge]:
        """Get all edges connected to node"""
        return (
            self.db.query(KnowledgeEdge)
            .filter(
                (KnowledgeEdge.from_node_id == node.id) |
                (KnowledgeEdge.to_node_id == node.id)
            )
            .all()
        )

class GraphEnrichment:
    """
    Identifies potential improvements to the knowledge graph through
    recursive learning and analysis.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.graph = KnowledgeGraph(db)
    
    def find_missing_connections(
        self,
        confidence_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find potential missing edges between nodes.
        """
        suggestions = []
        nodes = self.db.query(KnowledgeNode).all()
        
        for node1 in nodes:
            for node2 in nodes:
                if node1.id == node2.id:
                    continue
                    
                # Check if edge already exists
                existing = (
                    self.db.query(KnowledgeEdge)
                    .filter(
                        (
                            (KnowledgeEdge.from_node_id == node1.id) &
                            (KnowledgeEdge.to_node_id == node2.id)
                        ) |
                        (
                            (KnowledgeEdge.from_node_id == node2.id) &
                            (KnowledgeEdge.to_node_id == node1.id)
                        )
                    )
                    .first()
                )
                
                if existing:
                    continue
                
                # Calculate similarity
                similarity = self._calculate_node_similarity(node1, node2)
                
                if similarity > confidence_threshold:
                    suggestions.append({
                        "from_node": node1.id,
                        "to_node": node2.id,
                        "confidence": similarity,
                        "suggested_relation": self._suggest_relation_type(node1, node2)
                    })
        
        return sorted(suggestions, key=lambda x: x["confidence"], reverse=True)
    
    def suggest_node_improvements(
        self,
        node: KnowledgeNode
    ) -> Dict[str, Any]:
        """
        Suggest improvements for a node.
        """
        suggestions = {
            "missing_axes": [],
            "low_confidence_axes": [],
            "potential_relations": []
        }
        
        # Check for missing axes
        all_axes = set(AXES.keys())
        node_axes = set(node.axis_values.keys())
        missing = all_axes - node_axes
        
        for axis in missing:
            metadata = AXES[axis][1]
            suggestions["missing_axes"].append({
                "axis": axis,
                "importance": "high" if axis in ["pillar_function", "level_hierarchy"] else "medium",
                "reason": f"Missing {metadata.description}"
            })
        
        # Check for low confidence axes
        for axis, values in node.axis_values.items():
            if "values" in values and values["values"]:
                avg_value = sum(values["values"]) / len(values["values"])
                if avg_value < 0.5:
                    suggestions["low_confidence_axes"].append({
                        "axis": axis,
                        "current_value": avg_value,
                        "reason": f"Low confidence in {axis} axis"
                    })
        
        # Suggest potential relations
        neighbors = self.graph.get_neighbors(node)
        for neighbor in neighbors:
            edge = (
                self.db.query(KnowledgeEdge)
                .filter(
                    (
                        (KnowledgeEdge.from_node_id == node.id) &
                        (KnowledgeEdge.to_node_id == neighbor.id)
                    ) |
                    (
                        (KnowledgeEdge.from_node_id == neighbor.id) &
                        (KnowledgeEdge.to_node_id == node.id)
                    )
                )
                .first()
            )
            
            if edge and edge.confidence < 0.7:
                suggestions["potential_relations"].append({
                    "node_id": neighbor.id,
                    "current_relation": edge.relation_type,
                    "current_confidence": edge.confidence,
                    "suggested_improvements": [
                        "Add more axis values",
                        "Refine relation type",
                        "Add supporting evidence"
                    ]
                })
        
        return suggestions
    
    def suggest_domain_expansion(
        self,
        pillar_id: str
    ) -> List[Dict[str, Any]]:
        """
        Suggest ways to expand a domain.
        """
        suggestions = []
        pillar = self.db.query(PillarLevel).filter(PillarLevel.id == pillar_id).first()
        
        if not pillar:
            raise ValueError(f"Pillar level {pillar_id} not found")
        
        # Get all nodes in this domain
        domain_nodes = (
            self.db.query(KnowledgeNode)
            .filter(KnowledgeNode.pillar_level_id == pillar_id)
            .all()
        )
        
        # Analyze domain coverage
        total_axes = len(AXES)
        covered_axes = set()
        for node in domain_nodes:
            covered_axes.update(node.axis_values.keys())
        
        coverage = len(covered_axes) / total_axes
        if coverage < 0.8:
            suggestions.append({
                "type": "axis_coverage",
                "current_coverage": coverage,
                "missing_axes": list(set(AXES.keys()) - covered_axes),
                "importance": "high"
            })
        
        # Check for knowledge gaps
        if len(domain_nodes) < 3:
            suggestions.append({
                "type": "knowledge_density",
                "current_nodes": len(domain_nodes),
                "suggested_minimum": 3,
                "importance": "medium"
            })
        
        # Check for expert coverage
        experts = (
            self.db.query(PersonaAgent)
            .filter(PersonaAgent.domain_coverage.contains([pillar_id]))
            .all()
        )
        
        if not experts:
            suggestions.append({
                "type": "expert_coverage",
                "current_experts": 0,
                "suggested_minimum": 1,
                "importance": "high"
            })
        
        return suggestions
    
    def _calculate_node_similarity(
        self,
        node1: KnowledgeNode,
        node2: KnowledgeNode
    ) -> float:
        """Calculate similarity between two nodes"""
        # Start with pillar level similarity
        if node1.pillar_level_id == node2.pillar_level_id:
            base_similarity = 0.3
        else:
            pillar1 = self.db.query(PillarLevel).get(node1.pillar_level_id)
            pillar2 = self.db.query(PillarLevel).get(node2.pillar_level_id)
            if pillar1 and pillar2 and pillar1.parent_id == pillar2.parent_id:
                base_similarity = 0.2
            else:
                base_similarity = 0.1
        
        # Add axis similarity
        common_axes = set(node1.axis_values.keys()) & set(node2.axis_values.keys())
        if not common_axes:
            return base_similarity
        
        axis_similarity = 0.0
        for axis in common_axes:
            values1 = node1.axis_values[axis].get("values", [])
            values2 = node2.axis_values[axis].get("values", [])
            if values1 and values2:
                avg1 = sum(values1) / len(values1)
                avg2 = sum(values2) / len(values2)
                axis_similarity += 1.0 - abs(avg1 - avg2)
        
        axis_similarity /= len(common_axes)
        return (base_similarity + axis_similarity) / 2
    
    def _suggest_relation_type(
        self,
        node1: KnowledgeNode,
        node2: KnowledgeNode
    ) -> str:
        """Suggest relationship type between nodes"""
        pillar1 = self.db.query(PillarLevel).get(node1.pillar_level_id)
        pillar2 = self.db.query(PillarLevel).get(node2.pillar_level_id)
        
        if pillar1 and pillar2:
            if pillar1.depth < pillar2.depth:
                return "specializes"
            elif pillar1.depth > pillar2.depth:
                return "generalizes"
            else:
                return "related"
        
        return "related" 