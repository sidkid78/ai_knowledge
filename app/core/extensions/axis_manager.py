"""
Utilities for extending and managing axes.
"""
from typing import Dict, Any, List, Callable, Optional
from app.core.axes import (
    AxisFunction,
    AxisMetadata,
    AxisCategory,
    AXES,
    validate_axis_params
)

def register_axis(
    name: str,
    function: AxisFunction,
    metadata: AxisMetadata,
    category: AxisCategory,
    overwrite: bool = False
) -> None:
    """
    Register a new axis in the system.
    
    Args:
        name: Name of the axis (e.g., 'semantic_density')
        function: Computation function for the axis
        metadata: Metadata describing the axis
        category: Category of the axis
        overwrite: Whether to overwrite if axis already exists
    """
    if name in AXES and not overwrite:
        raise ValueError(f"Axis {name} already exists")
    
    # Validate function signature
    try:
        # Test with minimal valid input
        test_values = [0.5]
        test_weights = [1.0]
        function(values=test_values, weights=test_weights)
    except Exception as e:
        raise ValueError(f"Invalid axis function: {str(e)}")
    
    # Validate metadata
    if not metadata.value_range[0] <= metadata.value_range[1]:
        raise ValueError("Invalid value range")
    
    # Add to registry
    AXES[name] = (function, metadata)

def create_composite_axis(
    name: str,
    component_axes: List[str],
    weights: Optional[List[float]] = None,
    metadata: Optional[AxisMetadata] = None,
    category: AxisCategory = AxisCategory.FUNCTIONAL
) -> None:
    """
    Create a new axis that combines multiple existing axes.
    
    Args:
        name: Name of the new composite axis
        component_axes: List of existing axes to combine
        weights: Optional weights for each component
        metadata: Optional metadata (will be generated if not provided)
        category: Category for the new axis
    """
    if not weights:
        weights = [1.0] * len(component_axes)
    
    if len(weights) != len(component_axes):
        raise ValueError("Number of weights must match number of components")
    
    # Validate all components exist
    for axis in component_axes:
        if axis not in AXES:
            raise ValueError(f"Component axis {axis} not found")
    
    def composite_function(values: List[float], **kwargs) -> float:
        """Compute weighted combination of component axes"""
        if len(values) != len(component_axes):
            raise ValueError("Number of values must match number of components")
            
        total = 0.0
        for i, (axis, weight) in enumerate(zip(component_axes, weights)):
            axis_func = AXES[axis][0]
            total += weight * axis_func([values[i]], **kwargs)
        
        return total / sum(weights)
    
    # Generate metadata if not provided
    if not metadata:
        descriptions = [AXES[axis][1].description for axis in component_axes]
        metadata = AxisMetadata(
            name=name,
            description=f"Composite axis combining: {', '.join(component_axes)}",
            value_range=(0.0, 1.0),
            required_params=["values"],
            optional_params=["weights"]
        )
    
    register_axis(name, composite_function, metadata, category)

def create_temporal_axis(
    name: str,
    base_axis: str,
    decay_rate: float = 0.1,
    metadata: Optional[AxisMetadata] = None
) -> None:
    """
    Create a new temporal variant of an existing axis.
    
    Args:
        name: Name of the new temporal axis
        base_axis: Existing axis to add temporal decay to
        decay_rate: Rate of temporal decay
        metadata: Optional metadata (will be generated if not provided)
    """
    if base_axis not in AXES:
        raise ValueError(f"Base axis {base_axis} not found")
    
    base_func = AXES[base_axis][0]
    
    def temporal_function(
        values: List[float],
        time_deltas: List[float],
        **kwargs
    ) -> float:
        """Compute time-decayed axis value"""
        if len(values) != len(time_deltas):
            raise ValueError("Number of values must match number of time deltas")
            
        # Apply temporal decay
        decayed_values = [
            v * math.exp(-decay_rate * t)
            for v, t in zip(values, time_deltas)
        ]
        
        # Compute base function with decayed values
        return base_func(decayed_values, **kwargs)
    
    # Generate metadata if not provided
    if not metadata:
        base_metadata = AXES[base_axis][1]
        metadata = AxisMetadata(
            name=name,
            description=f"Temporal variant of {base_axis} with decay rate {decay_rate}",
            value_range=base_metadata.value_range,
            required_params=["values", "time_deltas"],
            optional_params=base_metadata.optional_params
        )
    
    register_axis(name, temporal_function, metadata, AxisCategory.TEMPORAL)

def suggest_axis_combinations() -> List[Dict[str, Any]]:
    """
    Suggest potentially useful axis combinations.
    """
    suggestions = []
    
    # Group axes by category
    categories = {}
    for name, (_, metadata) in AXES.items():
        cat = getattr(metadata, 'category', AxisCategory.FUNCTIONAL)
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(name)
    
    # Suggest combinations within categories
    for category, axes in categories.items():
        if len(axes) >= 2:
            suggestions.append({
                "name": f"composite_{category.value}",
                "components": axes,
                "weights": [1.0] * len(axes),
                "reasoning": f"Combine all {category.value} axes for comprehensive analysis"
            })
    
    # Suggest cross-category combinations
    if AxisCategory.STRUCTURAL in categories and AxisCategory.FUNCTIONAL in categories:
        suggestions.append({
            "name": "structure_function_composite",
            "components": [
                categories[AxisCategory.STRUCTURAL][0],
                categories[AxisCategory.FUNCTIONAL][0]
            ],
            "weights": [0.7, 0.3],
            "reasoning": "Combine structural and functional aspects"
        })
    
    return suggestions 