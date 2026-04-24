"""LLM service for generating Mermaid diagrams using OpenAI."""
from openai import OpenAI
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from ..config import settings
from ..models.schemas import DiagramType
from ..utils.logging import logger
from ..utils.mermaid import clean_mermaid_code, extract_mermaid_from_markdown


class LLMService:
    """Service for LLM-based diagram generation."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature
    
    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_diagram_from_prompt(
        self,
        prompt: str,
        diagram_type: Optional[DiagramType] = None
    ) -> str:
        """
        Generate Mermaid diagram from natural language prompt.
        
        Args:
            prompt: Natural language description
            diagram_type: Optional specific diagram type
            
        Returns:
            Mermaid diagram code
        """
        logger.info(f"Generating diagram from prompt: {prompt[:100]}...")
        
        system_prompt = self._build_system_prompt(diagram_type)
        user_message = self._build_user_message(prompt, diagram_type)
        
        try:
            message = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            
            response_text = message.choices[0].message.content or ""
            mermaid_code = clean_mermaid_code(response_text)
            
            logger.info("Successfully generated Mermaid diagram")
            return mermaid_code
            
        except Exception as e:
            logger.error(f"Failed to generate diagram: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def fix_mermaid_code(
        self,
        mermaid_code: str,
        error_message: Optional[str] = None
    ) -> str:
        """
        Fix invalid Mermaid code using LLM.
        
        Args:
            mermaid_code: Invalid Mermaid code
            error_message: Optional error message from validation
            
        Returns:
            Fixed Mermaid code
        """
        logger.info("Attempting to fix invalid Mermaid code")
        
        system_prompt = """You are a Mermaid diagram syntax expert.
                            Your task is to fix invalid Mermaid diagram code.

                            Rules:
                            1. Return ONLY the corrected Mermaid code
                            2. Fix syntax errors while preserving intent
                            3. Use valid Mermaid syntax only
                            4. Keep the diagram structure as close to original as possible
                            5. Do not add explanations or markdown formatting"""
        
        user_message = f"""Fix this invalid Mermaid code:

        ```mermaid
        {mermaid_code}
        ```"""
        
        if error_message:
            user_message += f"\n\nError message: {error_message}"
        
        user_message += "\n\nReturn only the corrected Mermaid code."
        
        try:
            message = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.3,  # Lower temperature for fixing
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            
            response_text = message.choices[0].message.content or ""
            fixed_code = clean_mermaid_code(response_text)
            
            logger.info("Successfully fixed Mermaid code")
            return fixed_code
            
        except Exception as e:
            logger.error(f"Failed to fix Mermaid code: {e}")
            raise
    
    def _build_system_prompt(self, diagram_type: Optional[DiagramType] = None) -> str:
        """Build system prompt for diagram generation."""
        base_prompt = """You are an expert at creating Mermaid diagrams.

                        Your task is to generate syntactically correct Mermaid diagram code based on user descriptions.

                        Core Rules:
                        1. Return ONLY valid Mermaid code - no explanations, no markdown formatting
                        2. Use proper Mermaid syntax for the chosen diagram type
                        3. Keep diagrams clear and well-organized
                        4. Use meaningful node IDs and labels
                        5. Avoid deprecated or unsupported Mermaid features
                        6. Do not use special characters that break Mermaid syntax

                        Diagram Types Available:
                        - flowchart: For processes, workflows, decision trees
                        - sequenceDiagram: For API interactions, message flows, protocols
                        - classDiagram: For OOP structures, class relationships
                        - stateDiagram: For state machines, lifecycles, transitions
                        - erDiagram: For database schemas, entity relationships
                        - gantt: For project timelines, schedules
                        - pie: For percentages and distributions
                        - journey: For user/customer journey maps
                        - mindmap: For hierarchical concepts
                        - gitGraph: For git branching strategies
                        - timeline: For chronological events
                        - quadrantChart: For 2x2 matrices"""

        if diagram_type:
            base_prompt += f"\n\nGenerate a {diagram_type.value} diagram."
        
        return base_prompt
    
    def _build_user_message(
        self,
        prompt: str,
        diagram_type: Optional[DiagramType] = None
    ) -> str:
        """Build user message for diagram generation."""
        message = f"Create a Mermaid diagram for: {prompt}\n\n"
        
        if diagram_type:
            message += f"Diagram type: {diagram_type.value}\n"
        
        message += "Return only the Mermaid code, no explanations."
        
        return message
