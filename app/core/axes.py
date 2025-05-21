"""
Core mathematical axes system for the UKG.
Each axis represents a fundamental dimension of knowledge analysis.
"""
from typing import Dict, Any, List, Optional, Protocol, runtime_checkable
from dataclasses import dataclass
from enum import Enum
import math

@runtime_checkable
class AxisFunction(Protocol):
    """Protocol for axis computation functions"""
    def __call__(self, values: List[float], weights: Optional[List[float]] = None, **kwargs) -> float:
        ...

@dataclass
class AxisMetadata:
    """Metadata for an axis"""
    name: str
    description: str
    value_range: tuple[float, float]
    required_params: List[str]
    optional_params: List[str]

class AxisCategory(Enum):
    """Categories of axes"""
    STRUCTURAL = "structural"
    FUNCTIONAL = "functional"
    TEMPORAL = "temporal"
    SEMANTIC = "semantic"

# Core axis computation functions
def compute_weighted_average(values: List[float], weights: Optional[List[float]] = None) -> float:
    """Compute weighted average of values"""
    if not weights:
        weights = [1.0] * len(values)
    return sum(v * w for v, w in zip(values, weights)) / sum(weights)

def compute_temporal_decay(values: List[float], time_deltas: List[float], decay_rate: float = 0.1) -> float:
    """Compute time-decayed value"""
    return sum(v * math.exp(-decay_rate * t) for v, t in zip(values, time_deltas))

# The 13 Mathematical Axes
AXES: Dict[str, tuple[AxisFunction, AxisMetadata]] = {
    "pillar_function": (
        compute_weighted_average,
        AxisMetadata(
            name="Pillar Function",
            description="Measures alignment with pillar-level objectives",
            value_range=(0.0, 1.0),
            required_params=["values"],
            optional_params=["weights"]
        )
    ),
    "level_hierarchy": (
        compute_weighted_average,
        AxisMetadata(
            name="Level Hierarchy",
            description="Quantifies position and influence in knowledge hierarchy",
            value_range=(0.0, 1.0),
            required_params=["values"],
            optional_params=["weights"]
        )
    ),
    "unified_system_function": (
        compute_weighted_average,
        AxisMetadata(
            name="Unified System Function",
            description="Measures contribution to overall system objectives",
            value_range=(0.0, 1.0),
            required_params=["values"],
            optional_params=["weights"]
        )
    ),
    "temporal_relevance": (
        compute_temporal_decay,
        AxisMetadata(
            name="Temporal Relevance",
            description="Time-based relevance and decay of knowledge",
            value_range=(0.0, 1.0),
            required_params=["values", "time_deltas"],
            optional_params=["decay_rate"]
        )
    ),
    "semantic_density": (
        compute_weighted_average,
        AxisMetadata(
            name="Semantic Density",
            description="Density of meaningful connections and relationships",
            value_range=(0.0, 1.0),
            required_params=["values"],
            optional_params=["weights"]
        )
    ),
    "complexity_measure": (
        compute_weighted_average,
        AxisMetadata(
            name="Complexity Measure",
            description="Measures inherent complexity and sophistication",
            value_range=(0.0, 5.0),
            required_params=["values"],
            optional_params=["weights"]
        )
    ),
    "uncertainty_quantification": (
        compute_weighted_average,
        AxisMetadata(
            name="Uncertainty Quantification",
            description="Quantifies uncertainty and confidence levels",
            value_range=(0.0, 1.0),
            required_params=["values"],
            optional_params=["weights"]
        )
    ),
    "role_id_layer": (
        compute_weighted_average,
        AxisMetadata(
            name="Role Identification Layer",
            description="Identifies and quantifies functional roles",
            value_range=(0.0, 1.0),
            required_params=["values"],
            optional_params=["weights"]
        )
    ),
    "sector_expert_function": (
        compute_weighted_average,
        AxisMetadata(
            name="Sector Expert Function",
            description="Domain expertise and specialization measure",
            value_range=(0.0, 1.0),
            required_params=["values"],
            optional_params=["weights"]
        )
    ),
    "compliance_vector": (
        compute_weighted_average,
        AxisMetadata(
            name="Compliance Vector",
            description="Regulatory and compliance alignment",
            value_range=(0.0, 1.0),
            required_params=["values"],
            optional_params=["weights"]
        )
    ),
    "risk_tensor": (
        compute_weighted_average,
        AxisMetadata(
            name="Risk Tensor",
            description="Multi-dimensional risk assessment",
            value_range=(0.0, 1.0),
            required_params=["values"],
            optional_params=["weights"]
        )
    ),
    "innovation_potential": (
        compute_weighted_average,
        AxisMetadata(
            name="Innovation Potential",
            description="Potential for generating new insights",
            value_range=(0.0, 1.0),
            required_params=["values"],
            optional_params=["weights"]
        )
    ),
    "cross_domain_synergy": (
        compute_weighted_average,
        AxisMetadata(
            name="Cross-Domain Synergy",
            description="Measures synergistic effects across domains",
            value_range=(0.0, 1.0),
            required_params=["values"],
            optional_params=["weights"]
        )
    ),
}

def get_axis_metadata(axis_name: str) -> AxisMetadata:
    """Get metadata for an axis"""
    return AXES[axis_name][1]

def compute_axis_value(axis_name: str, **kwargs) -> float:
    """Compute value for an axis"""
    axis_func = AXES[axis_name][0]
    return axis_func(**kwargs)

def validate_axis_params(axis_name: str, params: Dict[str, Any]) -> bool:
    """Validate parameters for an axis"""
    metadata = get_axis_metadata(axis_name)
    
    # Check required params
    for param in metadata.required_params:
        if param not in params:
            raise ValueError(f"Missing required parameter: {param}")
            
    # Check value ranges
    if "values" in params:
        for value in params["values"]:
            if not metadata.value_range[0] <= value <= metadata.value_range[1]:
                raise ValueError(f"Value {value} outside valid range {metadata.value_range}")
                
    return True