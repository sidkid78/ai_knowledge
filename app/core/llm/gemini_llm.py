"""
Gemini AI integration for AKF3 Universal Knowledge Graph
Uses the unified Google GenAI SDK for advanced AI reasoning capabilities
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

from google import genai
from google.genai import types

from .base import BaseLLM, LLMResponse


@dataclass
class GeminiConfig:
    """Configuration for Gemini AI using unified SDK"""
    api_key: Optional[str] = None
    model_name: str = "gemini-2.0-flash-001"
    temperature: float = 0.7
    max_output_tokens: int = 8192
    top_p: float = 0.8
    top_k: int = 40
    use_vertex_ai: bool = False
    project_id: Optional[str] = None
    location: str = "us-central1"


class GeminiLLM(BaseLLM):
    """
    Gemini AI implementation using unified Google GenAI SDK
    Provides UKG reasoning and analysis capabilities
    """
    
    def __init__(self, config: Optional[GeminiConfig] = None):
        if config is None:
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            use_vertex_ai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true"
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            
            config = GeminiConfig(
                api_key=api_key,
                use_vertex_ai=use_vertex_ai,
                project_id=project_id
            )
        
        self.config = config
        
        # Initialize the client based on configuration
        if config.use_vertex_ai:
            if not config.project_id:
                raise ValueError("Project ID required for Vertex AI")
            self.client = genai.Client(
                vertexai=True,
                project=config.project_id,
                location=config.location
            )
        else:
            if not config.api_key:
                raise ValueError("API key required for Gemini Developer API")
            self.client = genai.Client(api_key=config.api_key)
        
        # Generation configuration
        self.generation_config = types.GenerateContentConfig(
            temperature=config.temperature,
            max_output_tokens=config.max_output_tokens,
            top_p=config.top_p,
            top_k=config.top_k,
        )
    
    async def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stop_sequences: Optional[List[str]] = None
    ) -> LLMResponse:
        """Generate response from Gemini LLM"""
        try:
            # Create custom config for this request
            request_config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=self.config.top_p,
                top_k=self.config.top_k,
                stop_sequences=stop_sequences,
            )
            
            # Enhance prompt with context if provided
            enhanced_prompt = self._enhance_prompt_with_context(prompt, context)
            
            # Generate content
            response = await self.client.aio.models.generate_content(
                model=self.config.model_name,
                contents=enhanced_prompt,
                config=request_config
            )
            
            # Calculate confidence based on response quality
            confidence = self._calculate_confidence(response)
            
            return LLMResponse(
                content=response.text,
                confidence=confidence,
                metadata={
                    "model": self.config.model_name,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
            )
            
        except Exception as e:
            return LLMResponse(
                content=f"Error generating response: {str(e)}",
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
            # Convert functions to Gemini tool format
            tools = []
            for func in functions:
                tool = types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name=func["name"],
                            description=func.get("description", ""),
                            parameters=func.get("parameters", {})
                        )
                    ]
                )
                tools.append(tool)
            
            # Create config for function calling
            request_config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                tools=tools,
            )
            
            # Enhance prompt with context
            enhanced_prompt = self._enhance_prompt_with_context(prompt, context)
            
            # Generate content with function calling
            response = await self.client.aio.models.generate_content(
                model=self.config.model_name,
                contents=enhanced_prompt,
                config=request_config
            )
            
            # Process function calls if present
            content = response.text
            function_calls = []
            
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'function_call'):
                            function_calls.append({
                                "name": part.function_call.name,
                                "arguments": dict(part.function_call.args)
                            })
            
            confidence = self._calculate_confidence(response)
            
            return LLMResponse(
                content=content,
                confidence=confidence,
                metadata={
                    "model": self.config.model_name,
                    "temperature": temperature,
                    "function_calls": function_calls,
                }
            )
            
        except Exception as e:
            return LLMResponse(
                content=f"Error generating response with functions: {str(e)}",
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    def _calculate_confidence(self, response) -> float:
        """Calculate confidence score based on response characteristics"""
        try:
            if not response or not response.text:
                return 0.0
            
            # Basic confidence calculation based on response length and structure
            text_length = len(response.text)
            if text_length < 10:
                return 0.3
            elif text_length < 50:
                return 0.6
            elif text_length < 200:
                return 0.8
            else:
                return 0.9
                
        except Exception:
            return 0.5
    
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate AI response using Gemini unified SDK"""
        try:
            # Enhance prompt with UKG context if provided
            enhanced_prompt = self._enhance_prompt_with_context(prompt, context)
            
            # Use async client for non-blocking operation
            response = await self.client.aio.models.generate_content(
                model=self.config.model_name,
                contents=enhanced_prompt,
                config=self.generation_config
            )
            
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini generation failed: {str(e)}")
    
    async def analyze_knowledge_node(
        self, 
        node_data: Dict[str, Any],
        pillar_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a knowledge node using Gemini AI
        Provides insights, recommendations, and knowledge gaps
        """
        prompt = f"""
        As an expert in the Universal Knowledge Graph (UKG), analyze this knowledge node:
        
        Node Data:
        {json.dumps(node_data, indent=2)}
        
        Pillar Context:
        {json.dumps(pillar_context or {}, indent=2)}
        
        Please provide a comprehensive analysis including:
        1. Knowledge Domain Classification
        2. Conceptual Relationships
        3. Missing Information Gaps
        4. Recommended Connections
        5. Axis Value Insights
        6. Learning Opportunities
        
        Format your response as JSON with these sections.
        """
        
        response = await self.generate_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"analysis": response, "format": "text"}
    
    async def suggest_knowledge_connections(
        self,
        source_node: Dict[str, Any],
        candidate_nodes: List[Dict[str, Any]],
        max_suggestions: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Suggest potential knowledge connections using AI reasoning
        """
        prompt = f"""
        As a UKG expert, suggest the best knowledge connections for this source node:
        
        Source Node:
        {json.dumps(source_node, indent=2)}
        
        Candidate Nodes:
        {json.dumps(candidate_nodes[:10], indent=2)}  # Limit for context
        
        Analyze conceptual relationships, domain overlap, and knowledge flow.
        Return the top {max_suggestions} connections as JSON array with:
        - target_node_id: string
        - relationship_type: string
        - confidence: float (0-1)
        - reasoning: string
        - suggested_weight: float (0-1)
        """
        
        response = await self.generate_response(prompt)
        try:
            suggestions = json.loads(response)
            return suggestions[:max_suggestions] if isinstance(suggestions, list) else []
        except json.JSONDecodeError:
            return []
    
    async def optimize_axis_values(
        self,
        node_data: Dict[str, Any],
        current_axes: Dict[str, float],
        pillar_level: str
    ) -> Dict[str, float]:
        """
        Use AI to optimize axis values for a knowledge node
        """
        prompt = f"""
        As a UKG mathematical expert, optimize the axis values for this knowledge node:
        
        Node: {json.dumps(node_data, indent=2)}
        Current Axes: {json.dumps(current_axes, indent=2)}
        Pillar Level: {pillar_level}
        
        The 13 UKG axes are:
        1. Pillar Function: Σ wi · pi(x)
        2. Level Hierarchy: ∫ li, dt
        3. Branch Navigator: Π bi(x) · ri(x)
        4. Node Mapping: max(Σ ni(x)·vi(x))
        5. Honeycomb Crosswalk: Π ci(x) · wi(x)
        6. Spiderweb Provisions: Σ si(x) · ri(x)
        7. Octopus Sector Mappings: ∫ δs/δt, dt
        8. Role ID Layer: min(Σ ai(x)·ri(x))
        9. Sector Expert Function: Π si(x) · ci(x)
        10. Temporal Axis: ∫ δt, dt
        11. Unified System Function: Σ ui(x)·wi(x)
        12. Location Mapping: geoi(x)·scalei(x)
        13. Time Evolution Function: Σ epochi·Δki(x)
        
        Return optimized axis values as JSON object with axis names as keys.
        Provide mathematical reasoning for each optimization.
        """
        
        response = await self.generate_response(prompt)
        try:
            result = json.loads(response)
            return result.get("optimized_axes", current_axes)
        except json.JSONDecodeError:
            return current_axes
    
    async def generate_learning_insights(
        self,
        agent_trace: List[Dict[str, Any]],
        domain_context: List[str]
    ) -> Dict[str, Any]:
        """
        Generate learning insights for persona agents
        """
        prompt = f"""
        As an AI learning expert, analyze this agent's learning trace:
        
        Learning Trace:
        {json.dumps(agent_trace, indent=2)}
        
        Domain Context: {domain_context}
        
        Provide insights on:
        1. Learning patterns and progress
        2. Knowledge acquisition efficiency
        3. Domain coverage gaps
        4. Recommended learning paths
        5. Performance optimization suggestions
        
        Return analysis as JSON with structured insights.
        """
        
        response = await self.generate_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"insights": response, "format": "text"}
    
    async def reason_about_knowledge_gaps(
        self,
        pillar_coverage: Dict[str, float],
        missing_connections: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze knowledge gaps across the 87 UKG pillars
        """
        prompt = f"""
        As a UKG strategist, analyze these knowledge gaps:
        
        Pillar Coverage (87 pillars):
        {json.dumps(pillar_coverage, indent=2)}
        
        Missing Connections:
        {missing_connections}
        
        Provide strategic analysis:
        1. Critical gap identification
        2. Priority areas for development
        3. Cross-pillar impact assessment
        4. Resource allocation recommendations
        5. Risk assessment for knowledge blind spots
        
        Return structured JSON analysis.
        """
        
        response = await self.generate_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"gap_analysis": response, "format": "text"}
    
    async def generate_multimodal_content(
        self,
        text_prompt: str,
        image_data: Optional[bytes] = None,
        image_mime_type: str = "image/jpeg"
    ) -> str:
        """
        Generate content using multimodal capabilities (text + images)
        """
        try:
            contents = [text_prompt]
            
            if image_data:
                image_part = types.Part.from_bytes(
                    data=image_data,
                    mime_type=image_mime_type
                )
                contents.append(image_part)
            
            response = await self.client.aio.models.generate_content(
                model=self.config.model_name,
                contents=contents,
                config=self.generation_config
            )
            
            return response.text
        except Exception as e:
            raise RuntimeError(f"Multimodal generation failed: {str(e)}")
    
    async def create_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-004"
    ) -> List[List[float]]:
        """
        Generate embeddings for text inputs
        """
        try:
            response = await self.client.aio.models.embed_content(
                model=model,
                contents=texts
            )
            
            return [embedding.values for embedding in response.embeddings]
        except Exception as e:
            raise RuntimeError(f"Embedding generation failed: {str(e)}")
    
    def _enhance_prompt_with_context(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Enhance prompt with UKG context information"""
        if not context:
            return prompt
        
        context_str = "\n".join([
            f"Context - {key}: {value}" 
            for key, value in context.items()
        ])
        
        return f"{context_str}\n\nQuery: {prompt}"


def create_gemini_llm(
    api_key: Optional[str] = None,
    use_vertex_ai: bool = False,
    project_id: Optional[str] = None
) -> GeminiLLM:
    """
    Factory function to create GeminiLLM instance
    """
    config = GeminiConfig(
        api_key=api_key,
        use_vertex_ai=use_vertex_ai,
        project_id=project_id
    )
    return GeminiLLM(config) 