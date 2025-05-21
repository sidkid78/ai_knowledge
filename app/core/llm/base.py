"""
Base LLM interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class LLMResponse:
    """LLM response structure"""
    def __init__(
        self,
        content: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.confidence = confidence
        self.metadata = metadata or {}

class BaseLLM(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stop_sequences: Optional[List[str]] = None
    ) -> LLMResponse:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    async def generate_with_functions(
        self,
        prompt: str,
        functions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> LLMResponse:
        """Generate response with function calling capability"""
        pass 