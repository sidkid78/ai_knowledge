"""
Risk Assessment algorithm implementation using composable patterns.
"""
from typing import Dict, Any, List
from datetime import datetime
from .patterns import (
    AlgorithmPattern,
    GraphTraversalPattern,
    AlgorithmInput,
    AlgorithmOutput,
    AxisSchema
)
from app.models.knowledge_node import KnowledgeNode
from app.models.knowledge_edge import KnowledgeEdge
from app.core.axes import compute_axis_value, validate_axis_params

class RiskAssessmentPattern(GraphTraversalPattern[KnowledgeNode, AlgorithmOutput]):
    """Pattern for risk assessment across connected nodes"""
    
    def __init__(self):
        super().__init__(
            required_axes=["unified_system_function", "risk_tensor"],
            optional_axes=["compliance_vector"],
            max_depth=2,
            traversal_method="bfs"
        )
    
    def process_single(self, node: KnowledgeNode, input_data: AlgorithmInput) -> AlgorithmOutput:
        """Process a single node for risk assessment"""
        warnings = []
        risk_factors = []
        axis_risks = {}
        
        # Process required axes
        for axis_name in self.required_axes:
            axis_schema = input_data.axis_values.get(axis_name)
            if not axis_schema:
                warnings.append(f"Missing required axis: {axis_name}")
                continue
                
            try:
                # Validate and compute axis value
                validate_axis_params(axis_name, axis_schema.dict())
                
                # Only pass relevant parameters
                compute_params = {
                    "values": axis_schema.values
                }
                if axis_schema.weights:
                    compute_params["weights"] = axis_schema.weights
                
                value = compute_axis_value(axis_name, **compute_params)
                
                # For risk assessment, we consider higher values as higher risk
                risk_level = value
                
                # Apply weight if specified in algorithm parameters
                weight = 1.0
                for param in input_data.parameters.get("axis_parameters", []):
                    if param["axis"] == axis_name:
                        weight = param.get("weight", 1.0)
                        break
                
                risk_level *= weight
                axis_risks[axis_name] = risk_level
                
                # Categorize risk
                if risk_level > 0.7:
                    risk_factors.append(f"HIGH_RISK_{axis_name.upper()}")
                elif risk_level > 0.4:
                    risk_factors.append(f"MEDIUM_RISK_{axis_name.upper()}")
                
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
                            
                    risk_level = value * weight
                    axis_risks[axis_name] = risk_level
                    
                    # Categorize optional risks
                    if risk_level > 0.7:
                        risk_factors.append(f"HIGH_RISK_{axis_name.upper()}")
                    elif risk_level > 0.4:
                        risk_factors.append(f"MEDIUM_RISK_{axis_name.upper()}")
                        
                except Exception as e:
                    warnings.append(f"Error processing optional axis {axis_name}: {str(e)}")
        
        # Calculate overall risk level
        if axis_risks:
            overall_risk = sum(axis_risks.values()) / len(axis_risks)
        else:
            overall_risk = 0.0
            warnings.append("No valid axes processed")
        
        # Calculate confidence based on number of successful axis computations
        total_axes = len(self.required_axes) + len(self.optional_axes)
        processed_axes = len(axis_risks)
        confidence = processed_axes / total_axes if total_axes > 0 else 0.0
        
        return AlgorithmOutput(
            value=overall_risk,
            confidence=confidence,
            metadata={
                "node_id": str(node.id),
                "risk_factors": risk_factors,
                "axis_risks": axis_risks,
                "parameters": input_data.parameters
            },
            warnings=warnings,
            timestamp=datetime.utcnow()
        )

def assess_risk(node: KnowledgeNode, params: Dict[str, Any]) -> Dict[str, Any]:
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
    pattern = RiskAssessmentPattern()
    result = pattern.process_single(node, input_data)
    
    print("\nDebug - Result:")
    print(f"- Value: {result.value}")
    print(f"- Confidence: {result.confidence}")
    print(f"- Metadata: {result.metadata}")
    print(f"- Warnings: {result.warnings}")
    
    # Convert to legacy format
    return {
        "risk_level": result.value,
        "risk_factors": result.metadata["risk_factors"],
        "axis_risks": result.metadata["axis_risks"]
    } 