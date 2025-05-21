"""
Base classes and utilities for composable algorithms.
"""
from typing import Dict, Any, List, Protocol, runtime_checkable
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod

@runtime_checkable
class AlgorithmComponent(Protocol):
    """Protocol for algorithm components"""
    def process(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        ...

@dataclass
class AlgorithmResult:
    """Result of an algorithm execution"""
    algorithm_id: str
    status: str
    result_value: float
    confidence: float
    execution_time: float
    metadata: Dict[str, Any]
    timestamp: datetime
    warnings: List[str]

class ComposableAlgorithm(ABC):
    """Base class for composable algorithms"""
    
    def __init__(self, algorithm_id: str, components: List[AlgorithmComponent]):
        self.algorithm_id = algorithm_id
        self.components = components
        
    @abstractmethod
    def preprocess(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess input data"""
        pass
        
    @abstractmethod
    def postprocess(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Postprocess component results"""
        pass
    
    def execute(self, data: Dict[str, Any]) -> AlgorithmResult:
        """Execute the algorithm pipeline"""
        start_time = datetime.utcnow()
        warnings = []
        
        try:
            # Preprocess
            processed_data = self.preprocess(data)
            
            # Execute components
            context = {}
            component_results = []
            
            for component in self.components:
                try:
                    result = component.process(processed_data, context)
                    component_results.append(result)
                    context.update(result)
                except Exception as e:
                    warnings.append(f"Component error: {str(e)}")
            
            # Postprocess
            final_result = self.postprocess(component_results)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AlgorithmResult(
                algorithm_id=self.algorithm_id,
                status="success",
                result_value=final_result.get("value", 0.0),
                confidence=final_result.get("confidence", 0.0),
                execution_time=execution_time,
                metadata=final_result.get("metadata", {}),
                timestamp=datetime.utcnow(),
                warnings=warnings
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return AlgorithmResult(
                algorithm_id=self.algorithm_id,
                status="error",
                result_value=0.0,
                confidence=0.0,
                execution_time=execution_time,
                metadata={},
                timestamp=datetime.utcnow(),
                warnings=[f"Algorithm error: {str(e)}"] + warnings
            )

class AlgorithmPipeline:
    """Pipeline for executing multiple algorithms"""
    
    def __init__(self, algorithms: List[ComposableAlgorithm]):
        self.algorithms = algorithms
    
    def execute(self, data: Dict[str, Any]) -> List[AlgorithmResult]:
        """Execute all algorithms in the pipeline"""
        results = []
        context = {}
        
        for algorithm in self.algorithms:
            result = algorithm.execute(data)
            results.append(result)
            if result.status == "success":
                context[algorithm.algorithm_id] = result
                
        return results 