"""
API endpoints for UKG 13 Mathematical Axes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.axes import AxisCalculator, UKGAxes, AxisValue
from app.models.knowledge_node import KnowledgeNode

router = APIRouter()


class AxisComputationRequest(BaseModel):
    """Request model for axis computation"""
    node_id: Optional[str] = None
    axis_data: Dict[str, Any]
    specific_axes: Optional[List[str]] = None  # Compute only specific axes
    
    class Config:
        json_schema_extra = {
            "example": {
                "axis_data": {
                    "pillar_function": {
                        "weights": [0.8, 0.6, 0.9],
                        "values": [0.7, 0.8, 0.5]
                    },
                    "level_hierarchy": {
                        "values": [1.0, 2.0, 1.5],
                        "time_deltas": [0.5, 1.0, 0.8]
                    }
                },
                "specific_axes": ["pillar_function", "level_hierarchy"]
            }
        }


class AxisComputationResponse(BaseModel):
    """Response model for axis computation"""
    node_id: Optional[str]
    computed_axes: Dict[str, Dict[str, Any]]
    total_axes_computed: int
    computation_timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "123e4567-e89b-12d3-a456-426614174000",
                "computed_axes": {
                    "pillar_function": {
                        "value": 1.85,
                        "formula": "Σ wi · pi(x)",
                        "components": {
                            "weights": [0.8, 0.6, 0.9],
                            "pillar_values": [0.7, 0.8, 0.5]
                        },
                        "confidence": 1.0
                    }
                },
                "total_axes_computed": 1,
                "computation_timestamp": "2024-01-15T10:30:00Z"
            }
        }


class AxisListResponse(BaseModel):
    """Response model for listing all available axes"""
    axes: List[Dict[str, str]]
    total_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "axes": [
                    {
                        "name": "pillar_function",
                        "formula": "Σ wi · pi(x)",
                        "description": "Weighted sum of pillar attributes"
                    }
                ],
                "total_count": 13
            }
        }


@router.get("/", response_model=AxisListResponse)
async def list_axes():
    """
    List all 13 UKG mathematical axes with their formulas and descriptions
    """
    axes_info = [
        {
            "name": "pillar_function",
            "formula": "Σ wi · pi(x)",
            "description": "Weighted sum of pillar attributes"
        },
        {
            "name": "level_hierarchy",
            "formula": "∫ li, dt",
            "description": "Integral over level index li with time deltas"
        },
        {
            "name": "branch_navigator",
            "formula": "Π bi(x) · ri(x)",
            "description": "Product of branch and route components"
        },
        {
            "name": "node_mapping",
            "formula": "max(Σ ni(x)·vi(x))",
            "description": "Maximum sum of node*value pairs"
        },
        {
            "name": "honeycomb_crosswalk",
            "formula": "Π ci(x) · wi(x)",
            "description": "Product of crosswalk and weight per axis"
        },
        {
            "name": "spiderweb_provisions",
            "formula": "Σ si(x) · ri(x)",
            "description": "Weighted sum of provision and route"
        },
        {
            "name": "octopus_sector_mappings",
            "formula": "∫ δs/δt, dt",
            "description": "Integral of sector deltas over time"
        },
        {
            "name": "role_id_layer",
            "formula": "min(Σ ai(x)·ri(x))",
            "description": "Minimum sum of attribute*route for roles"
        },
        {
            "name": "sector_expert_function",
            "formula": "Π si(x) · ci(x)",
            "description": "Product of sector/provision and compliance"
        },
        {
            "name": "temporal_axis",
            "formula": "∫ δt, dt",
            "description": "Accumulation over time intervals"
        },
        {
            "name": "unified_system_function",
            "formula": "Σ ui(x)·wi(x)",
            "description": "System-wide weighted sum"
        },
        {
            "name": "location_mapping",
            "formula": "geoi(x)·scalei(x)",
            "description": "Geospatial position scaling"
        },
        {
            "name": "time_evolution_function",
            "formula": "Σ epochi·Δki(x)",
            "description": "Epoch-wise knowledge delta sum"
        }
    ]
    
    return AxisListResponse(
        axes=axes_info,
        total_count=len(axes_info)
    )


@router.post("/compute", response_model=AxisComputationResponse)
async def compute_axes(
    request: AxisComputationRequest,
    db: Session = Depends(get_db)
):
    """
    Compute UKG mathematical axes for given data
    
    Can compute axes for:
    - Existing knowledge node (provide node_id)
    - Custom axis data (provide axis_data)
    - Specific subset of axes (provide specific_axes list)
    """
    from datetime import datetime
    
    calculator = AxisCalculator()
    
    # If node_id provided, get node data from database
    if request.node_id:
        node = db.query(KnowledgeNode).filter(KnowledgeNode.id == request.node_id).first()
        if not node:
            raise HTTPException(status_code=404, detail="Knowledge node not found")
        
        # Merge node axis values with request data
        node_axis_data = node.axis_values or {}
        combined_data = {**node_axis_data, **request.axis_data}
    else:
        combined_data = request.axis_data
    
    # Compute axes
    try:
        computed_results = {}
        axes_to_compute = request.specific_axes or calculator.get_axis_names()
        
        for axis_name in axes_to_compute:
            if axis_name in combined_data:
                axis_data = combined_data[axis_name]
                result = None
                
                # Call appropriate axis method based on axis name
                if axis_name == "pillar_function":
                    result = calculator.axes.pillar_function(
                        axis_data.get('weights', [1.0]),
                        axis_data.get('values', [0.0])
                    )
                elif axis_name == "level_hierarchy":
                    result = calculator.axes.level_hierarchy(
                        axis_data.get('values', [1.0]),
                        axis_data.get('time_deltas', [1.0])
                    )
                elif axis_name == "unified_system_function":
                    result = calculator.axes.unified_system_function(
                        axis_data.get('values', [1.0]),
                        axis_data.get('weights', [1.0])
                    )
                # Add more axis-specific parameter handling as needed
                
                if result:
                    computed_results[axis_name] = {
                        "value": result.value,
                        "formula": result.components.get("formula", ""),
                        "components": result.components,
                        "confidence": result.confidence,
                        "computed_at": result.computed_at.isoformat()
                    }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error computing axes: {str(e)}")
    
    return AxisComputationResponse(
        node_id=request.node_id,
        computed_axes=computed_results,
        total_axes_computed=len(computed_results),
        computation_timestamp=datetime.utcnow().isoformat()
    )


@router.get("/node/{node_id}/axes", response_model=AxisComputationResponse)
async def get_node_axes(
    node_id: str,
    specific_axes: Optional[str] = None,  # Comma-separated list
    db: Session = Depends(get_db)
):
    """
    Get computed axes for a specific knowledge node
    
    Args:
        node_id: UUID of the knowledge node
        specific_axes: Optional comma-separated list of specific axes to compute
    """
    node = db.query(KnowledgeNode).filter(KnowledgeNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Knowledge node not found")
    
    axes_to_compute = None
    if specific_axes:
        axes_to_compute = [axis.strip() for axis in specific_axes.split(",")]
    
    request = AxisComputationRequest(
        node_id=node_id,
        axis_data=node.axis_values or {},
        specific_axes=axes_to_compute
    )
    
    return await compute_axes(request, db)


@router.post("/batch-compute")
async def batch_compute_axes(
    node_ids: List[str],
    specific_axes: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """
    Compute axes for multiple knowledge nodes in batch
    """
    results = []
    
    for node_id in node_ids:
        try:
            request = AxisComputationRequest(
                node_id=node_id,
                axis_data={},
                specific_axes=specific_axes
            )
            result = await compute_axes(request, db)
            results.append(result)
        except Exception as e:
            results.append({
                "node_id": node_id,
                "error": str(e),
                "computed_axes": {},
                "total_axes_computed": 0
            })
    
    return {
        "batch_results": results,
        "total_nodes_processed": len(node_ids),
        "successful_computations": len([r for r in results if "error" not in r])
    } 