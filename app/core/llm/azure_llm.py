"""
Azure OpenAI implementation.
"""
from typing import Dict, Any, Optional, List
import openai
from openai import AsyncAzureOpenAI

from app.core.llm.base import BaseLLM, LLMResponse
from app.core.config import settings

class AzureLLM(BaseLLM):
    """Azure OpenAI implementation"""
    
    def __init__(
        self,
        deployment_name: str = settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        api_version: str = settings.AZURE_OPENAI_API_VERSION
    ):
        self.client = AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=api_version,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        self.deployment_name = deployment_name
    
    async def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.3,
        max_tokens: int = 1000,
        stop_sequences: Optional[List[str]] = None
    ) -> LLMResponse:
        """Generate response from Azure OpenAI"""
        try:
            # Prepare messages
            messages = []
            
            # Add context if provided
            if context:
                messages.append({
                    "role": "system",
                    "content": str(context.get("system", ""))
                })
                
                # Add any previous messages
                for msg in context.get("messages", []):
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": str(msg.get("content", ""))
                    })
            
            # Add current prompt
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Make API call
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop_sequences,
                stream=False
            )
            
            # Extract response
            content = response.choices[0].message.content
            
            # Calculate confidence based on response metadata
            confidence = 1.0 - (temperature * 0.5)  # Simple heuristic
            
            return LLMResponse(
                content=content,
                confidence=confidence,
                metadata={
                    "model": self.model_name,
                    "usage": response.usage.dict() if response.usage else {},
                    "finish_reason": response.choices[0].finish_reason
                }
            )
            
        except Exception as e:
            # Log error and return low confidence response
            print(f"Azure OpenAI error: {str(e)}")
            return LLMResponse(
                content="Error generating response",
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    async def generate_with_functions(
        self,
        prompt: str,
        functions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> LLMResponse:
        """Generate response with function calling capability"""
        try:
            # Prepare messages
            messages = []
            
            # Add context if provided
            if context:
                messages.append({
                    "role": "system",
                    "content": str(context.get("system", ""))
                })
                
                # Add any previous messages
                for msg in context.get("messages", []):
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": str(msg.get("content", ""))
                    })
            
            # Add current prompt
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Make API call with functions
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                functions=functions,
                function_call="auto",
                stream=False
            )
            
            # Extract response
            message = response.choices[0].message
            
            # Check if function was called
            if message.function_call:
                return LLMResponse(
                    content=message.function_call.arguments,
                    confidence=0.9,  # High confidence for function calls
                    metadata={
                        "function_name": message.function_call.name,
                        "model": self.model_name,
                        "usage": response.usage.dict() if response.usage else {},
                        "finish_reason": response.choices[0].finish_reason,
                        "is_function_call": True
                    }
                )
            else:
                return LLMResponse(
                    content=message.content,
                    confidence=1.0 - (temperature * 0.5),
                    metadata={
                        "model": self.model_name,
                        "usage": response.usage.dict() if response.usage else {},
                        "finish_reason": response.choices[0].finish_reason,
                        "is_function_call": False
                    }
                )
            
        except Exception as e:
            # Log error and return low confidence response
            print(f"Azure OpenAI error: {str(e)}")
            return LLMResponse(
                content="Error generating response",
                confidence=0.0,
                metadata={
                    "error": str(e),
                    "is_function_call": False
                }
            ) 