# core/persona_agent.py
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import copy
import datetime

# Import algorithm registry and axes
from .algorithms import ALGORITHMS
from .axes import AXES

class Persona:
    def __init__(
        self, 
        id: UUID, 
        name: str,
        domain_coverage: List[str],    # List of pillar IDs, e.g., ["PL04"]
        algorithms_available: List[str],
        learning_trace: Optional[List[Dict[str, Any]]] = None
    ):
        self.id = id
        self.name = name
        self.domain_coverage = domain_coverage
        self.algorithms_available = algorithms_available
        self.learning_trace = learning_trace or []

    def process_query(
        self, 
        node: Dict[str, Any],           # As from KnowledgeNode schema
        algorithm_id: str,
        pillar_levels_map: Dict[str, Any],
        recursion_depth: int = 0, 
        max_recursion: int = 3,
        visited_agents: Optional[List[UUID]] = None,
        verbose: bool = False,
        background_agents = None     # List[Persona], for chaining
    ) -> Dict[str, Any]:
        """
        Main recursive learning routine for an agent.
        """
        if visited_agents is None:
            visited_agents = []

        result = {
            "agent_id": str(self.id),
            "agent_name": self.name,
            "pillar_levels": self.domain_coverage,
            "algorithm_id": algorithm_id,
            "node_id": str(node['id']),
            "start_time": datetime.datetime.utcnow().isoformat(),
            "result": None,
            "recursion_depth": recursion_depth,
            "actions": [],
            "validation": None,
            "subcalls": []
        }

        # Step 1: Can I apply the requested algorithm?
        if algorithm_id not in self.algorithms_available:
            result['actions'].append("Algorithm not in persona capability: " + algorithm_id)
            return result

        # Step 2: Retrieve axes needed for this algorithm
        axes_input = copy.deepcopy(node.get("axis_values", {}))
        # If specialized, could filter axes here for this persona & pillar domain

        # Step 3: Attempt to compute result
        try:
            # Algorithm receives (query, axis_values, weights)
            # (For simplicity, pass node as query – adapt as per algorithm)
            algo = ALGORITHMS[algorithm_id]
            output = algo(query=node, axis_values=axes_input, weights={}) # add weights as needed

            # Store result
            result['result'] = output
            result['actions'].append(f"Computed algorithm {algorithm_id} directly.")
        except Exception as e:
            result['result'] = None
            result['actions'].append(f"Computation failed: {e}")

        # Step 4: Check for confidence or gaps (simulate "recursive reasoning")
        gap_detected, gap_info = self._detect_gap(node, output, axes_input)
        if gap_detected and recursion_depth < max_recursion:
            result['actions'].append("Gap/uncertainty detected – recursive learning engaged.")
            # Option 1: Recursion – re-analyze with alternative algorithm or different context (simulate reflection)
            next_algorithm = self._choose_alternate_algorithm(algorithm_id)
            if next_algorithm:
                sub_result = self.process_query(
                    node=node,
                    algorithm_id=next_algorithm,
                    pillar_levels_map=pillar_levels_map,
                    recursion_depth=recursion_depth+1,
                    max_recursion=max_recursion,
                    visited_agents=visited_agents + [self.id],
                    verbose=verbose,
                    background_agents=background_agents
                )
                result['subcalls'].append(sub_result)
            # Option 2: If available, chain to a peer agent covering the gap's pillar
            elif background_agents is not None and gap_info.get("missing_pillar"):
                for agent in background_agents:
                    if agent.id != self.id and gap_info["missing_pillar"] in agent.domain_coverage:
                        result['actions'].append(f"Chaining to expert agent {agent.name} for pillar {gap_info['missing_pillar']}")
                        sub_result = agent.process_query(
                            node,
                            algorithm_id,
                            pillar_levels_map,
                            recursion_depth=recursion_depth+1,
                            max_recursion=max_recursion,
                            visited_agents=visited_agents + [self.id],
                            verbose=verbose,
                            background_agents=background_agents
                        )
                        result['subcalls'].append(sub_result)
                        break
        else:
            result['actions'].append("No recursion necessary, result sufficient.")

        # Step 5: Autonomous validation/research if needed
        if gap_detected:
            result['validation'] = self._autonomous_research(node, gap_info, verbose=verbose)
        
        # Step 6: Log trace
        self._record_trace(result)
        return result

    def _detect_gap(self, node, output, axes_input) -> Tuple[bool, Dict[str, Any]]:
        # Basic: Detect if output is None, or if axis values are missing/zero/low
        # Extend with whatever domain heuristics you have
        gap = False
        info = {}
        if output is None:
            gap = True
            info['reason'] = "Algorithm output is None"
        elif isinstance(output, (int, float)) and output < 0.1:
            gap = True
            info['reason'] = "Result likely insignificant"
        # Example: check for axes with missing or low value
        missing_axes = [k for k, v in axes_input.items() if not v or min(v.get('values', [1.0])) < 0.05]
        if missing_axes:
            gap = True
            info['missing_axes'] = missing_axes
        # Example: missing pillar expertise
        if 'pillar_level_id' in node and node['pillar_level_id'] not in self.domain_coverage:
            info['missing_pillar'] = node['pillar_level_id']
        return gap, info

    def _choose_alternate_algorithm(self, current_algorithm:str) -> Optional[str]:
        # Simple fallback: pick any other algorithm in capabilities
        return next((a for a in self.algorithms_available if a != current_algorithm), None)

    def _autonomous_research(self, node, gap_info, verbose=False) -> Dict[str, Any]:
        # Placeholder: In a production build, this could query a database, external services, etc.
        # Here, simulate some basic gap-filling heuristics.
        validation_report = {"status": None, "actions": []}
        if 'missing_axes' in gap_info:
            for axis in gap_info['missing_axes']:
                # Try to "impute" missing values (dummy example)
                node['axis_values'][axis] = {"values": [0.5], "weights": [1.0]}
                validation_report['actions'].append(
                    f"Imputed axis {axis} with default value."
                )
            validation_report["status"] = "Axis values imputed"
        elif 'missing_pillar' in gap_info:
            validation_report['status'] = "Unable to fill gap – missing pillar expertise"
        else:
            validation_report['status'] = "No significant gap found"
        return validation_report

    def _record_trace(self, result: Dict[str, Any]) -> None:
        # Add result dict, truncated to last N traces for memory/performance
        self.learning_trace.append(result)
        if len(self.learning_trace) > 1000:
            self.learning_trace = self.learning_trace[-1000:]

# Utility: Build (or hydrate from DB) agents for all major domains/pillars
def load_persona_agents(persona_rows, algorithm_options, pillar_map) -> List[Persona]:
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