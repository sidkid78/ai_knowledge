# core/persona_agent.py
from typing import List, Dict, Any, Optional, Tuple, Set
from uuid import UUID
import copy
import datetime
from pathlib import Path
import json

# Import algorithm registry and axes
from .algorithms import ALGORITHMS
from .axes import AXES, validate_axis_params
from app.models.persona import AgentState
from app.core.llm.azure_llm import AzureLLM
from app.core.config import settings

class ValidationResult:
    """Result of autonomous validation"""
    def __init__(
        self,
        is_valid: bool,
        confidence: float,
        suggestions: List[Dict[str, Any]],
        sources: List[str]
    ):
        self.is_valid = is_valid
        self.confidence = confidence
        self.suggestions = suggestions
        self.sources = sources

class Persona:
    """
    Persona/Agent class that simulates domain-specific, recursively reasoning AI workers.
    
    Features:
    - Domain-specific algorithm application
    - Recursive self-invocation
    - Peer agent collaboration
    - Autonomous research/validation
    - Complete traceability
    """
    def __init__(
        self,
        id: UUID,
        name: str,
        domain_coverage: List[str],
        algorithms_available: List[str],
        learning_trace: List[Dict[str, Any]] = None
    ):
        self.id = id
        self.name = name
        self.domain_coverage = domain_coverage
        self.algorithms_available = algorithms_available
        self.learning_trace = learning_trace or []
        self.state = AgentState.IDLE
        self.validation_rules = {
            "required_axes": ["temporal_axis", "confidence_axis"],
            "value_ranges": {
                "temporal_axis": (0, 1),
                "confidence_axis": (0, 1)
            }
        }
        
        # Initialize LLM
        self.llm = AzureLLM()

    def _init_result(self, node: Dict[str, Any], algorithm_id: str, recursion_depth: int) -> Dict[str, Any]:
        """Initialize standardized result structure"""
        return {
            "agent_id": str(self.id),
            "agent_name": self.name,
            "pillar_levels": self.domain_coverage,
            "algorithm_id": algorithm_id,
            "node_id": str(node["id"]),
            "start_time": datetime.datetime.utcnow().isoformat(),
            "recursion_depth": recursion_depth,
            "actions": [],
            "result": None,
            "confidence": 0.0,
            "validation": {
                "status": None,
                "actions": []
            },
            "subcalls": [],
            "error": None
        }

    async def _validate_input(self, node: Dict[str, Any], algorithm_id: str, result: Dict[str, Any]) -> bool:
        """Validate input parameters and update trace"""
        # Check algorithm availability
        if algorithm_id not in self.algorithms_available:
            result["actions"].append(f"Algorithm not available: {algorithm_id}")
            result["validation"]["status"] = "Algorithm unavailable"
            return False
        
        # Check domain coverage
        if "pillar_level_id" in node and node["pillar_level_id"] not in self.domain_coverage:
            result["actions"].append("Domain expertise gap detected")
            result["validation"]["status"] = "Domain gap"
            return False
            
        # Use LLM to validate axis values
        validation_prompt = f"""
        Please validate the following node axis values against the requirements:
        
        Node: {json.dumps(node, indent=2)}
        Required axes: {self.validation_rules['required_axes']}
        Value ranges: {self.validation_rules['value_ranges']}
        
        Tasks:
        1. Check if all required axes are present
        2. Validate value ranges
        3. Suggest default values for missing axes
        4. Identify any potential issues
        
        Respond in JSON format with:
        {
            "is_valid": boolean,
            "missing_axes": [...],
            "invalid_ranges": {...},
            "suggested_defaults": {...},
            "issues": [...]
        }
        """
        
        validation_response = await self.llm.generate(
            prompt=validation_prompt,
            temperature=0.1  # Low temperature for consistent validation
        )
        
        try:
            validation_data = json.loads(validation_response.content)
            
            # Apply suggested defaults
            axis_values = node.get("axis_values", {})
            for axis, value in validation_data.get("suggested_defaults", {}).items():
                if axis not in axis_values:
                    axis_values[axis] = value
                    action_msg = f"Imputed axis {axis} with value {value}"
                    result["validation"]["actions"].append(action_msg)
            
            # Update validation status
            is_valid_llm = validation_data.get("is_valid", False)
            if is_valid_llm:
                result["validation"]["status"] = "Valid"
                return True
            else:
                result["validation"]["status"] = "Invalid"
                result["validation"]["actions"].extend(validation_data.get("issues", []))
                return False
                
        except json.JSONDecodeError:
            result["validation"]["status"] = "Validation error"
            result["validation"]["actions"].append("Failed to parse validation response")
            return False
        except Exception as val_err:
            result["validation"]["status"] = "Validation processing error"
            result["validation"]["actions"].append(f"Internal error during validation: {str(val_err)}")
            return False

    async def _apply_algorithm(
        self,
        node: Dict[str, Any],
        algorithm_id: str,
        context: Dict[str, Any]
    ) -> Tuple[Any, float]:
        """Apply algorithm and return result with confidence"""
        if algorithm_id not in ALGORITHMS:
            raise ValueError(f"Algorithm {algorithm_id} not found")
            
        algo = ALGORITHMS[algorithm_id]
        
        # Extract required components from node
        query = node.get("query", {})
        axis_values = node.get("axis_values", {})
        weights = node.get("weights", {})
        
        # Execute algorithm
        try:
            result = algo(query, axis_values, weights)
            confidence = result.get('confidence', 0.0)
            return result, confidence
        except Exception as e:
            raise ValueError(f"Algorithm execution failed: {str(e)}")

    async def process_query(
        self,
        node: Dict[str, Any],
        algorithm_id: str,
        pillar_levels_map: Dict[str, Any],
        recursion_depth: int = 0,
        max_recursion: int = 3,
        visited_agents: Optional[List[UUID]] = None,
        background_agents: Optional[List['Persona']] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main recursive learning routine for an agent.
        
        Features:
        - Recursive analysis with gap detection
        - Peer agent collaboration
        - Autonomous validation
        - Learning trace maintenance
        """
        if visited_agents is None:
            visited_agents = []
        if context is None:
            context = {}

        # Initialize result structure
        result = self._init_result(node, algorithm_id, recursion_depth)
        
        try:
            # Update agent state
            self.state = AgentState.PROCESSING
            
            # Validate input
            if not await self._validate_input(node, algorithm_id, result):
                result["actions"].append("Input validation failed")
                self.state = AgentState.ERROR
                self._update_learning_trace(result)
                return result

            # Try direct computation
            try:
                # Get the result tuple first
                algo_result_tuple = await self._apply_algorithm(node, algorithm_id, context)
                # Then unpack
                output, confidence = algo_result_tuple
                
                result["result"] = output
                result["confidence"] = confidence
                action_msg = f"Computed algorithm {algorithm_id} directly." # Isolate f-string
                result["actions"].append(action_msg)
            except Exception as e:
                # This catches errors from _apply_algorithm
                result["error"] = str(e)
                result["actions"].append(
                    f"Direct computation failed: {str(e)}"
                )

            # Use LLM to decide on recursive processing
            if result["confidence"] < 0.7 and recursion_depth < max_recursion:
                recursion_prompt = f"""
                Please analyze whether recursive processing is needed:
                
                Current result: {json.dumps(result, indent=2)}
                Available peer agents: {len(background_agents) if background_agents else 0}
                Current recursion depth: {recursion_depth}
                Max recursion: {max_recursion}
                
                Tasks:
                1. Assess if the confidence is too low
                2. Determine if peer agents might help
                3. Consider if self-recursion would be beneficial
                4. Suggest specific next steps
                
                Respond in JSON format with:
                {
                    "needs_recursion": boolean,
                    "try_peer_agents": boolean,
                    "try_self_recursion": boolean,
                    "reasoning": [...],
                    "suggested_steps": [...]
                }
                """
                
                recursion_response = await self.llm.generate(
                    prompt=recursion_prompt,
                    temperature=0.3  # Low temperature for consistent decisions
                )
                
                try:
                    recursion_data = json.loads(recursion_response.content)
                    
                    if recursion_data.get("needs_recursion", False):
                        result["actions"].append(
                            "Gap/uncertainty detected – recursive learning engaged."
                        )
                        
                        # Try peer agents first
                        if recursion_data.get("try_peer_agents", False) and background_agents:
                            for agent in background_agents:
                                if agent.id not in visited_agents and any(
                                    level in agent.domain_coverage 
                                    for level in pillar_levels_map.get(node["pillar_level_id"], [])
                                ):
                                    subcall = await agent.process_query(
                                        node=node,
                                        algorithm_id=algorithm_id,
                                        pillar_levels_map=pillar_levels_map,
                                        recursion_depth=recursion_depth + 1,
                                        max_recursion=max_recursion,
                                        visited_agents=visited_agents + [self.id],
                                        background_agents=background_agents,
                                        context=context
                                    )
                                    result["subcalls"].append(subcall)
                                    
                                    if subcall["confidence"] > result["confidence"]:
                                        result["result"] = subcall["result"]
                                        result["confidence"] = subcall["confidence"]
                                        result["actions"].append(
                                            f"Used peer agent {agent.name} result."
                                        )

                        # If still uncertain, try self-recursion
                        if recursion_data.get("try_self_recursion", False) and result["confidence"] < 0.7:
                            # Add more context from pillar levels
                            enriched_context = {
                                **context,
                                "pillar_levels": pillar_levels_map.get(node["pillar_level_id"], []),
                                "previous_results": [
                                    call["result"] for call in result["subcalls"]
                                ]
                            }
                            
                            subcall = await self.process_query(
                                node=node,
                                algorithm_id=algorithm_id,
                                pillar_levels_map=pillar_levels_map,
                                recursion_depth=recursion_depth + 1,
                                max_recursion=max_recursion,
                                visited_agents=visited_agents + [self.id],
                                background_agents=background_agents,
                                context=enriched_context
                            )
                            result["subcalls"].append(subcall)
                            
                            if subcall["confidence"] > result["confidence"]:
                                result["result"] = subcall["result"]
                                result["confidence"] = subcall["confidence"]
                                result["actions"].append("Used recursive refinement result.")
                                
                except json.JSONDecodeError:
                    result["actions"].append("Failed to parse recursion decision")

            # Update final state
            self.state = AgentState.IDLE
            
        except Exception as e:
            error_message = str(e)
            result["error"] = error_message
            result["actions"].append(f"Processing error: {error_message}")
            self.state = AgentState.ERROR
            
        # Update learning trace
        self._update_learning_trace(result)
        return result

    def _update_learning_trace(self, result: Dict[str, Any]) -> None:
        """Update agent learning trace"""
        trace_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "agent_id": result["agent_id"],
            "agent_name": result["agent_name"],
            "pillar_levels": result["pillar_levels"],
            "algorithm_id": result["algorithm_id"],
            "node_id": result["node_id"],
            "start_time": result["start_time"],
            "result": result["result"],
            "recursion_depth": result["recursion_depth"],
            "actions": result["actions"],
            "validation": result["validation"],
            "subcalls": result["subcalls"],
            "confidence": result["confidence"],
            "error": result["error"]
        }
        self.learning_trace.append(trace_entry)

# Utility: Build (or hydrate from DB) agents for all major domains/pillars
def load_persona_agents(persona_rows, algorithm_options, pillar_map) -> List[Persona]:
    """
    Create Persona agents from database rows or configuration.
    
    Args:
        persona_rows: List of ORM models or dicts from persona_agents table
        algorithm_options: Available algorithms for agents
        pillar_map: Mapping of pillar IDs to pillar information
        
    Returns:
        List of initialized Persona agents
    """
    # persona_rows as list of ORM models or dicts from persona_agents table
    # pillar_map: mapping id->pillar info
    agents = []
    for row in persona_rows:
        agent = Persona(
            id=row['id'],
            name=row['name'],
            domain_coverage=row['domain_coverage'],
            algorithms_available=row['algorithms_available'],
            learning_trace=row.get('learning_trace', [])
        )
        agents.append(agent)
    return agents

def save_agent_output_to_markdown(result: Dict[str, Any], output_dir: str = "agent_outputs") -> str:
    """
    Save agent processing results to a markdown file.
    
    Args:
        result: The processing result from a Persona agent
        output_dir: Directory to save the markdown file (default: 'agent_outputs')
        
    Returns:
        Path to the generated markdown file
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate filename using timestamp and agent info
    timestamp = datetime.datetime.fromisoformat(result['start_time']).strftime('%Y%m%d_%H%M%S')
    filename = f"agent_{result['agent_name']}_{timestamp}.md"
    file_path = output_path / filename
    
    # Format the markdown content
    content = [
        f"# Agent Processing Report: {result['agent_name']}",
        f"\n## Overview",
        f"- **Agent ID**: {result['agent_id']}",
        f"- **Node ID**: {result['node_id']}",
        f"- **Algorithm**: {result['algorithm_id']}",
        f"- **Start Time**: {result['start_time']}",
        f"- **Recursion Depth**: {result['recursion_depth']}",
        
        f"\n## Actions Taken",
        *[f"1. {action}" for action in result['actions']],
        
        f"\n## Processing Result",
        "```json",
        json.dumps(result['result'], indent=2) if result['result'] else "No result generated",
        "```",
    ]
    
    # Add validation section if present
    if result['validation']:
        content.extend([
            f"\n## Validation",
            f"**Status**: {result['validation']['status']}",
            "\n**Actions:**",
            *[f"- {action}" for action in result['validation']['actions']]
        ])
    
    # Add subcalls section if present
    if result['subcalls']:
        content.extend([
            f"\n## Subcalls",
            *[f"\n### Subcall to {subcall['agent_name']}" for subcall in result['subcalls']]
        ])
    
    # Write to file
    file_path.write_text('\n'.join(content), encoding='utf-8')
    return str(file_path)

# # 5. Extensibility Patterns
# New axes, pillar levels, or algorithms: Add to models/core, no change needed to endpoint wiring—APIs pick up expanded set automatically.
# Recursion depth or agent chaining: Exposed as parameters for POSTs to agent endpoints.
# Advanced: Batch operations, real-time event hooks (for async research/validation); straightforward to add using FastAPI BackgroundTasks or WebSockets.


