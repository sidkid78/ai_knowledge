"""
Background task manager for ongoing research and validation.
"""
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import asyncio
import logging
from uuid import UUID, uuid4
from enum import Enum
from fastapi import BackgroundTasks

from app.core.orchestrator import Orchestrator
from app.db.session import SessionLocal
from app.models.knowledge_node import KnowledgeNode
from app.models.knowledge_edge import KnowledgeEdge

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Background task status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskType(Enum):
    """Background task types"""
    RESEARCH = "research"
    VALIDATION = "validation"
    ENRICHMENT = "enrichment"
    ENSEMBLE = "ensemble"

class BackgroundTask:
    """Background task container"""
    def __init__(
        self,
        task_type: TaskType,
        node_id: str,
        parameters: Dict[str, Any],
        priority: int = 1
    ):
        self.id = uuid4()
        self.type = task_type
        self.node_id = node_id
        self.parameters = parameters
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None

class BackgroundManager:
    """
    Manages background tasks for research, validation, and enrichment.
    
    Features:
    - Task queuing and prioritization
    - Concurrent task execution
    - Result persistence
    - Error handling and retry logic
    """
    
    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator
        self.tasks: Dict[UUID, BackgroundTask] = {}
        self.running_tasks: Set[UUID] = set()
        self.max_concurrent = 5
        self._task_lock = asyncio.Lock()
        self._enrichment_threshold = 3  # Number of gaps before triggering enrichment

    async def schedule_task(
        self,
        task_type: TaskType,
        node_id: str,
        parameters: Dict[str, Any],
        priority: int = 1,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> UUID:
        """Schedule a new background task"""
        task = BackgroundTask(task_type, node_id, parameters, priority)
        self.tasks[task.id] = task
        
        if background_tasks:
            background_tasks.add_task(self._process_task, task.id)
        else:
            asyncio.create_task(self._process_task(task.id))
        
        return task.id

    async def _process_task(self, task_id: UUID) -> None:
        """Process a background task"""
        task = self.tasks[task_id]
        
        try:
            async with self._task_lock:
                if len(self.running_tasks) >= self.max_concurrent:
                    return  # Will be retried later
                self.running_tasks.add(task_id)
            
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            
            # Process based on task type
            if task.type == TaskType.RESEARCH:
                await self._perform_research(task)
            elif task.type == TaskType.VALIDATION:
                await self._perform_validation(task)
            elif task.type == TaskType.ENRICHMENT:
                await self._perform_enrichment(task)
            elif task.type == TaskType.ENSEMBLE:
                await self._perform_ensemble_reasoning(task)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            
        finally:
            self.running_tasks.remove(task_id)

    async def _perform_research(self, task: BackgroundTask) -> None:
        """Perform autonomous research on a node"""
        db = SessionLocal()
        try:
            # Get node
            node = db.query(KnowledgeNode).filter(KnowledgeNode.id == task.node_id).first()
            if not node:
                raise ValueError(f"Node {task.node_id} not found")
            
            # Get relevant agents
            research_agents = [
                agent for agent in self.orchestrator.agents
                if "research" in agent.research_sources.get("capabilities", [])
            ]
            
            # Perform research with each agent
            results = []
            for agent in research_agents:
                result = agent.process_query(
                    node=node.to_dict(),
                    algorithm_id=task.parameters.get("algorithm_id", "ai_knowledge_discovery"),
                    pillar_levels_map=self.orchestrator.pillar_map,
                    context={"mode": "research"}
                )
                results.append(result)
            
            # Aggregate research findings
            task.result = {
                "findings": results,
                "suggested_updates": self._aggregate_research_findings(results)
            }
            
            # If significant findings, trigger enrichment
            if len(task.result["suggested_updates"]) >= self._enrichment_threshold:
                await self.schedule_task(
                    TaskType.ENRICHMENT,
                    task.node_id,
                    {"suggestions": task.result["suggested_updates"]}
                )
            
        finally:
            db.close()

    async def _perform_validation(self, task: BackgroundTask) -> None:
        """Perform validation on a node"""
        db = SessionLocal()
        try:
            # Get node
            node = db.query(KnowledgeNode).filter(KnowledgeNode.id == task.node_id).first()
            if not node:
                raise ValueError(f"Node {task.node_id} not found")
            
            # Get validation agents
            validation_agents = [
                agent for agent in self.orchestrator.agents
                if "validation" in agent.research_sources.get("capabilities", [])
            ]
            
            # Perform validation
            validations = []
            for agent in validation_agents:
                result = agent.process_query(
                    node=node.to_dict(),
                    algorithm_id=task.parameters.get("algorithm_id", "validation"),
                    pillar_levels_map=self.orchestrator.pillar_map,
                    context={"mode": "validation"}
                )
                validations.append(result)
            
            # Aggregate validation results
            task.result = {
                "validations": validations,
                "consensus": self._calculate_validation_consensus(validations)
            }
            
        finally:
            db.close()

    async def _perform_enrichment(self, task: BackgroundTask) -> None:
        """Perform graph enrichment based on findings"""
        db = SessionLocal()
        try:
            # Get node
            node = db.query(KnowledgeNode).filter(KnowledgeNode.id == task.node_id).first()
            if not node:
                raise ValueError(f"Node {task.node_id} not found")
            
            suggestions = task.parameters.get("suggestions", [])
            applied_updates = []
            
            for suggestion in suggestions:
                try:
                    if suggestion["type"] == "new_node":
                        # Create new node
                        new_node = KnowledgeNode(**suggestion["data"])
                        db.add(new_node)
                        db.flush()
                        
                        # Create edge to original node
                        edge = KnowledgeEdge(
                            from_node_id=node.id,
                            to_node_id=new_node.id,
                            relation_type=suggestion["relation_type"],
                            confidence=suggestion["confidence"]
                        )
                        db.add(edge)
                        applied_updates.append({
                            "type": "new_node_and_edge",
                            "node_id": str(new_node.id),
                            "edge_id": str(edge.id)
                        })
                        
                    elif suggestion["type"] == "update_axis":
                        # Update axis values
                        axis_updates = suggestion["updates"]
                        node.axis_values.update(axis_updates)
                        applied_updates.append({
                            "type": "axis_update",
                            "axes": list(axis_updates.keys())
                        })
                
                except Exception as e:
                    logger.error(f"Error applying suggestion: {str(e)}")
            
            db.commit()
            task.result = {"applied_updates": applied_updates}
            
        finally:
            db.close()

    async def _perform_ensemble_reasoning(self, task: BackgroundTask) -> None:
        """Perform ensemble reasoning across multiple agents"""
        db = SessionLocal()
        try:
            # Get node
            node = db.query(KnowledgeNode).filter(KnowledgeNode.id == task.node_id).first()
            if not node:
                raise ValueError(f"Node {task.node_id} not found")
            
            # Get all relevant agents
            algorithm_id = task.parameters.get("algorithm_id", "ai_knowledge_discovery")
            relevant_agents = [
                agent for agent in self.orchestrator.agents
                if algorithm_id in agent.algorithms_available
                and node.pillar_level_id in agent.domain_coverage
            ]
            
            # Process with all agents
            results = []
            for agent in relevant_agents:
                result = agent.process_query(
                    node=node.to_dict(),
                    algorithm_id=algorithm_id,
                    pillar_levels_map=self.orchestrator.pillar_map,
                    context={"mode": "ensemble"}
                )
                results.append(result)
            
            # Calculate ensemble results
            task.result = {
                "individual_results": results,
                "ensemble_metrics": self._calculate_ensemble_metrics(results),
                "consensus_result": self._calculate_ensemble_consensus(results)
            }
            
            # If significant disagreement, trigger validation
            if task.result["ensemble_metrics"]["disagreement_level"] > 0.3:
                await self.schedule_task(
                    TaskType.VALIDATION,
                    task.node_id,
                    {"algorithm_id": algorithm_id}
                )
            
        finally:
            db.close()

    def _aggregate_research_findings(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Aggregate research findings from multiple agents"""
        # Implementation would combine and deduplicate findings
        return []

    def _calculate_validation_consensus(
        self,
        validations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate consensus from multiple validations"""
        # Implementation would determine overall validation status
        return {}

    def _calculate_ensemble_metrics(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate metrics for ensemble results"""
        if not results:
            return {
                "agreement_score": 0.0,
                "disagreement_level": 0.0,
                "confidence_stats": {
                    "mean": 0.0,
                    "std": 0.0
                }
            }
        
        # Calculate confidence statistics
        confidences = [r.get("confidence", 0.0) for r in results]
        mean_confidence = sum(confidences) / len(confidences)
        variance = sum((c - mean_confidence) ** 2 for c in confidences) / len(confidences)
        std_confidence = variance ** 0.5
        
        # Calculate agreement score (inverse of normalized std dev)
        agreement_score = 1.0 - (std_confidence / mean_confidence if mean_confidence > 0 else 1.0)
        
        return {
            "agreement_score": agreement_score,
            "disagreement_level": 1.0 - agreement_score,
            "confidence_stats": {
                "mean": mean_confidence,
                "std": std_confidence
            }
        }

    def _calculate_ensemble_consensus(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate consensus result from ensemble"""
        if not results:
            return {}
        
        # Combine results based on confidence
        total_confidence = sum(r.get("confidence", 0.0) for r in results)
        if total_confidence == 0:
            return results[0]  # Return first result if no confidence scores
        
        # Weight results by confidence
        consensus = {}
        for result in results:
            weight = result.get("confidence", 0.0) / total_confidence
            for key, value in result.items():
                if key not in consensus:
                    consensus[key] = 0.0
                consensus[key] += value * weight
        
        return consensus 