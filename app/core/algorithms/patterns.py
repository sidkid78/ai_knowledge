"""
Core patterns for composable algorithms in the UKG system.
"""
from typing import Dict, Any, List, TypeVar, Generic, Protocol, Union, Optional
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod

# Type variables for generic node/edge types
T = TypeVar('T')  # Generic type for nodes/edges
R = TypeVar('R')  # Generic type for results

class AxisSchema(BaseModel):
    """Schema for axis values and parameters"""
    values: List[float] = Field(..., description="Axis values")
    weights: Optional[List[float]] = Field(None, description="Optional weights")
    time_deltas: Optional[List[float]] = Field(None, description="Time deltas for temporal axes")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional axis parameters")

    class Config:
        extra = "allow"  # Allow additional fields for extensibility

@dataclass
class AlgorithmContext:
    """Context for algorithm execution"""
    timestamp: datetime
    trace_id: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]

class AlgorithmInput(BaseModel):
    """Generic input for algorithms"""
    axis_values: Dict[str, AxisSchema]
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

class AlgorithmOutput(BaseModel):
    """Generic output for algorithms"""
    value: float
    confidence: float
    metadata: Dict[str, Any]
    warnings: List[str] = Field(default_factory=list)
    timestamp: datetime

    class Config:
        arbitrary_types_allowed = True

class GraphPattern(Protocol[T]):
    """Protocol for graph operations"""
    def get_neighbors(self, node: T) -> List[T]:
        ...
    def get_edges(self, node: T) -> List[Any]:
        ...

class AlgorithmPattern(Generic[T, R], ABC):
    """Base pattern for algorithms"""
    
    def __init__(self, required_axes: List[str], optional_axes: List[str] = None):
        self.required_axes = required_axes
        self.optional_axes = optional_axes or []
        
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        """Validate input data against required axes"""
        for axis in self.required_axes:
            if axis not in input_data.axis_values:
                raise ValueError(f"Missing required axis: {axis}")
        return True
    
    @abstractmethod
    def process_single(self, node: T, input_data: AlgorithmInput) -> R:
        """Process a single node"""
        pass
    
    def process_collection(self, nodes: List[T], input_data: AlgorithmInput) -> List[R]:
        """Process a collection of nodes"""
        results = []
        for node in nodes:
            try:
                result = self.process_single(node, input_data)
                results.append(result)
            except Exception as e:
                # Log error but continue processing
                print(f"Error processing node {node}: {str(e)}")
        return results

class CollectionPattern(AlgorithmPattern[T, R]):
    """Pattern for algorithms that operate on collections"""
    
    def __init__(self, 
                 required_axes: List[str],
                 optional_axes: List[str] = None,
                 aggregation_method: str = "average"):
        super().__init__(required_axes, optional_axes)
        self.aggregation_method = aggregation_method
    
    def aggregate_results(self, results: List[R]) -> R:
        """Aggregate results from collection processing"""
        if not results:
            raise ValueError("No results to aggregate")
            
        if self.aggregation_method == "average":
            # Implement averaging logic
            pass
        elif self.aggregation_method == "max":
            # Implement max logic
            pass
        # Add more aggregation methods
        
        return results[0]  # Placeholder

class GraphTraversalPattern(AlgorithmPattern[T, R]):
    """Pattern for algorithms that traverse the graph"""
    
    def __init__(self,
                 required_axes: List[str],
                 optional_axes: List[str] = None,
                 max_depth: int = 3,
                 traversal_method: str = "bfs"):
        super().__init__(required_axes, optional_axes)
        self.max_depth = max_depth
        self.traversal_method = traversal_method
        
    def traverse(self, 
                start_node: T,
                graph: GraphPattern[T],
                input_data: AlgorithmInput) -> List[R]:
        """Traverse graph and process nodes"""
        visited = set()
        results = []
        
        def bfs(node: T, depth: int):
            if depth > self.max_depth or node in visited:
                return
            visited.add(node)
            
            try:
                result = self.process_single(node, input_data)
                results.append(result)
            except Exception as e:
                print(f"Error processing node {node}: {str(e)}")
                
            for neighbor in graph.get_neighbors(node):
                if neighbor not in visited:
                    bfs(neighbor, depth + 1)
        
        bfs(start_node, 0)
        return results

class TemporalPattern(AlgorithmPattern[T, R]):
    """Pattern for algorithms that handle temporal aspects"""
    
    def __init__(self,
                 required_axes: List[str],
                 optional_axes: List[str] = None,
                 time_window: Optional[float] = None):
        super().__init__(required_axes, optional_axes)
        self.time_window = time_window
    
    def filter_by_time(self, 
                      nodes: List[T],
                      reference_time: datetime) -> List[T]:
        """Filter nodes by time window"""
        if not self.time_window:
            return nodes
            
        return [
            node for node in nodes
            if abs((getattr(node, 'timestamp', reference_time) - reference_time)
                  .total_seconds()) <= self.time_window
        ] 