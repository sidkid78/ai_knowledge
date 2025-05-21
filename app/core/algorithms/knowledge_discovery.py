"""
AI Knowledge Discovery algorithm implementation using composable patterns.
"""
from typing import Dict, Any, List
from datetime import datetime
from .patterns import (
    AlgorithmPattern,
    CollectionPattern,
    AlgorithmInput,
    AlgorithmOutput,
    AxisSchema
)
from app.models.knowledge_node import KnowledgeNode
from app.core.axes import compute_axis_value, validate_axis_params

class KnowledgeDiscoveryPattern(CollectionPattern[KnowledgeNode, AlgorithmOutput]):
    """Pattern for AI knowledge discovery"""
    
    def __init__(self):
        super().__init__(
            required_axes=["pillar_function", "level_hierarchy"],
            optional_axes=["unified_system_function"],
            aggregation_method="average"
        )
    
    def process_single(self, node: KnowledgeNode, input_data: AlgorithmInput) -> AlgorithmOutput:
        """Process a single node for knowledge discovery"""
        warnings = []
        discoveries = []
        axis_contributions = {}
        
        # Process required axes
        for axis_name in self.required_axes:
            axis_schema = input_data.axis_values.get(axis_name)
            if not axis_schema:
                warnings.append(f"Missing required axis: {axis_name}")
                continue
                
            try:
                # Validate and compute axis value
                validate_axis_params(axis_name, axis_schema.dict())
                
                # Only pass relevant parameters to compute function
                compute_params = {
                    "values": axis_schema.values
                }
                if axis_schema.weights:
                    compute_params["weights"] = axis_schema.weights
                
                value = compute_axis_value(axis_name, **compute_params)
                
                # Apply weight if specified in algorithm parameters
                weight = 1.0
                for param in input_data.parameters.get("axis_parameters", []):
                    if param["axis"] == axis_name:
                        weight = param.get("weight", 1.0)
                        break
                
                contribution = value * weight
                axis_contributions[axis_name] = contribution
                
                # Record significant discoveries
                if contribution > 0.8:
                    discoveries.append(f"HIGH_SIGNIFICANCE_{axis_name.upper()}")
                elif contribution > 0.6:
                    discoveries.append(f"MEDIUM_SIGNIFICANCE_{axis_name.upper()}")
                
            except Exception as e:
                warnings.append(f"Error processing axis {axis_name}: {str(e)}")
        
        # Process optional axes
        for axis_name in self.optional_axes:
            axis_schema = input_data.axis_values.get(axis_name)
            if axis_schema:
                try:
                    validate_axis_params(axis_name, axis_schema.dict())
                    
                    # Only pass relevant parameters
                    compute_params = {
                        "values": axis_schema.values
                    }
                    if axis_schema.weights:
                        compute_params["weights"] = axis_schema.weights
                    
                    value = compute_axis_value(axis_name, **compute_params)
                    
                    # Apply weight if specified
                    weight = 1.0
                    for param in input_data.parameters.get("axis_parameters", []):
                        if param["axis"] == axis_name:
                            weight = param.get("weight", 1.0)
                            break
                            
                    axis_contributions[axis_name] = value * weight
                except Exception as e:
                    warnings.append(f"Error processing optional axis {axis_name}: {str(e)}")
        
        # Calculate overall confidence
        if axis_contributions:
            confidence = sum(axis_contributions.values()) / len(axis_contributions)
        else:
            confidence = 0.0
            warnings.append("No valid axes processed")
        
        return AlgorithmOutput(
            value=confidence,
            confidence=confidence,
            metadata={
                "node_id": str(node.id),
                "discoveries": discoveries,
                "axis_contributions": axis_contributions,
                "parameters": input_data.parameters
            },
            warnings=warnings,
            timestamp=datetime.utcnow()
        )

def ai_knowledge_discovery(node: KnowledgeNode, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy wrapper for compatibility with existing code.
    """
    print("\nDebug - Original axis values:")
    for axis, values in node.axis_values.items():
        print(f"- {axis}: {values}")
    
    # Convert parameters to new input format
    axis_values = {}
    for axis, values in node.axis_values.items():
        schema_values = {
            "values": values.get("values", []),
            "weights": values.get("weights", [1.0] * len(values.get("values", []))),
            "time_deltas": values.get("time_deltas", []),
            "parameters": {k: v for k, v in values.items() 
                         if k not in ["values", "weights", "time_deltas"]}
        }
        axis_values[axis] = AxisSchema(**schema_values)
        print(f"\nDebug - Converted {axis}:")
        print(f"- Schema values: {schema_values}")
        print(f"- Final schema: {axis_values[axis]}")
    
    input_data = AlgorithmInput(
        axis_values=axis_values,
        parameters=params,
        context={"timestamp": datetime.utcnow()}
    )
    
    print("\nDebug - Input data:")
    print(f"- Parameters: {params}")
    print(f"- Axis values: {input_data.axis_values}")
    
    # Create and execute pattern
    pattern = KnowledgeDiscoveryPattern()
    result = pattern.process_single(node, input_data)
    
    print("\nDebug - Result:")
    print(f"- Value: {result.value}")
    print(f"- Confidence: {result.confidence}")
    print(f"- Metadata: {result.metadata}")
    print(f"- Warnings: {result.warnings}")
    
    # Convert to legacy format
    return {
        "confidence": result.confidence,
        "discoveries": result.metadata["discoveries"],
        "axis_contributions": result.metadata["axis_contributions"]
    } 