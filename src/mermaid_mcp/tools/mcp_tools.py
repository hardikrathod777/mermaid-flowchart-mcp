"""MCP tools for Mermaid diagram generation."""
from typing import Optional, Dict, Any
from ..services.llm_service import LLMService
from ..services.validation_service import ValidationService
from ..services.render_service import RenderService
from ..models.schemas import (
    GenerateDiagramRequest,
    GenerateDiagramFromTypeRequest,
    ValidateMermaidRequest,
    FixMermaidRequest,
    RenderDiagramRequest,
    DiagramResponse,
    ValidationResponse,
    FixResponse,
    RenderResponse,
    RenderFormat,
    Theme
)
from ..utils.mermaid import (
    analyze_diagram,
    create_mermaid_live_url,
    create_mermaid_ink_url,
    infer_diagram_type_from_prompt
)
from ..utils.logging import logger


class MermaidMCPTools:
    """MCP tools for Mermaid diagram operations."""
    
    def __init__(self):
        """Initialize MCP tools."""
        self.llm_service = LLMService()
        self.validation_service = ValidationService()
        self.render_service = RenderService()
    
    async def generate_diagram_from_prompt(
        self,
        prompt: str,
        diagram_type: Optional[str] = None,
        theme: Optional[str] = None,
        auto_fix: bool = True
    ) -> Dict[str, Any]:
        """
        Generate Mermaid diagram from natural language prompt.
        
        Args:
            prompt: Natural language description
            diagram_type: Optional diagram type
            theme: Optional theme
            auto_fix: Auto-fix invalid syntax
            
        Returns:
            Dictionary with diagram data
        """
        logger.info(f"Tool: generate_diagram_from_prompt - prompt: {prompt[:50]}...")
        
        try:
            # Infer diagram type if not provided
            if not diagram_type:
                inferred_type = infer_diagram_type_from_prompt(prompt)
                logger.info(f"Inferred diagram type: {inferred_type.value}")
            else:
                from ..models.schemas import DiagramType
                inferred_type = DiagramType(diagram_type)
            
            # Generate diagram
            mermaid_code = await self.llm_service.generate_diagram_from_prompt(
                prompt=prompt,
                diagram_type=inferred_type
            )
            
            # Validate
            validation = await self.validation_service.validate(mermaid_code)
            
            # Auto-fix if invalid and auto_fix enabled
            if not validation.is_valid and auto_fix:
                logger.info("Diagram invalid, attempting auto-fix")
                try:
                    mermaid_code = await self.llm_service.fix_mermaid_code(
                        mermaid_code=mermaid_code,
                        error_message=", ".join(validation.errors)
                    )
                    # Re-validate
                    validation = await self.validation_service.validate(mermaid_code)
                except Exception as fix_error:
                    logger.warning(f"Auto-fix failed: {fix_error}")
            
            # Analyze diagram
            metadata = analyze_diagram(mermaid_code)
            
            # Create links
            live_url = create_mermaid_live_url(mermaid_code)
            ink_url = create_mermaid_ink_url(mermaid_code)
            
            response = DiagramResponse(
                mermaid_code=mermaid_code,
                diagram_type=metadata.diagram_type,
                metadata=metadata,
                mermaid_live_url=live_url,
                mermaid_ink_url=ink_url,
                is_valid=validation.is_valid,
                validation_errors=validation.errors if not validation.is_valid else None
            )
            
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Failed to generate diagram: {e}")
            raise
    
    async def generate_diagram_from_type(
        self,
        diagram_type: str,
        description: str,
        theme: Optional[str] = None,
        auto_fix: bool = True
    ) -> Dict[str, Any]:
        """
        Generate specific diagram type.
        
        Args:
            diagram_type: Type of diagram
            description: Description of content
            theme: Optional theme
            auto_fix: Auto-fix invalid syntax
            
        Returns:
            Dictionary with diagram data
        """
        logger.info(f"Tool: generate_diagram_from_type - type: {diagram_type}")
        
        try:
            from ..models.schemas import DiagramType
            dt = DiagramType(diagram_type)
            
            # Generate with specific type
            mermaid_code = await self.llm_service.generate_diagram_from_prompt(
                prompt=description,
                diagram_type=dt
            )
            
            # Validate
            validation = await self.validation_service.validate(mermaid_code)
            
            # Auto-fix if needed
            if not validation.is_valid and auto_fix:
                logger.info("Diagram invalid, attempting auto-fix")
                try:
                    mermaid_code = await self.llm_service.fix_mermaid_code(
                        mermaid_code=mermaid_code,
                        error_message=", ".join(validation.errors)
                    )
                    validation = await self.validation_service.validate(mermaid_code)
                except Exception as fix_error:
                    logger.warning(f"Auto-fix failed: {fix_error}")
            
            # Analyze and create response
            metadata = analyze_diagram(mermaid_code)
            live_url = create_mermaid_live_url(mermaid_code)
            ink_url = create_mermaid_ink_url(mermaid_code)
            
            response = DiagramResponse(
                mermaid_code=mermaid_code,
                diagram_type=diagram_type,
                metadata=metadata,
                mermaid_live_url=live_url,
                mermaid_ink_url=ink_url,
                is_valid=validation.is_valid,
                validation_errors=validation.errors if not validation.is_valid else None
            )
            
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Failed to generate diagram: {e}")
            raise
    
    async def validate_mermaid(self, mermaid_code: str) -> Dict[str, Any]:
        """
        Validate Mermaid diagram code.
        
        Args:
            mermaid_code: Mermaid code to validate
            
        Returns:
            Dictionary with validation results
        """
        logger.info("Tool: validate_mermaid")
        
        try:
            validation = await self.validation_service.validate(mermaid_code)
            return validation.model_dump()
            
        except Exception as e:
            logger.error(f"Failed to validate diagram: {e}")
            raise
    
    async def fix_mermaid(
        self,
        mermaid_code: str,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fix invalid Mermaid code.
        
        Args:
            mermaid_code: Invalid Mermaid code
            error_message: Optional error message
            
        Returns:
            Dictionary with fixed code
        """
        logger.info("Tool: fix_mermaid")
        
        try:
            # Get original validation
            original_validation = await self.validation_service.validate(mermaid_code)
            original_errors = original_validation.errors
            
            # Fix the code
            fixed_code = await self.llm_service.fix_mermaid_code(
                mermaid_code=mermaid_code,
                error_message=error_message or ", ".join(original_errors)
            )
            
            # Validate fixed code
            fixed_validation = await self.validation_service.validate(fixed_code)
            
            # Determine changes
            changes = []
            if fixed_validation.is_valid:
                changes.append("Fixed all syntax errors")
            else:
                changes.append(f"Fixed some errors, {len(fixed_validation.errors)} remaining")
            
            response = FixResponse(
                success=fixed_validation.is_valid,
                fixed_code=fixed_code,
                original_errors=original_errors,
                changes_made=changes,
                error=None if fixed_validation.is_valid else ", ".join(fixed_validation.errors)
            )
            
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Failed to fix diagram: {e}")
            return FixResponse(
                success=False,
                error=str(e)
            ).model_dump()
    
    async def render_diagram(
        self,
        mermaid_code: str,
        format: str = "png",
        theme: Optional[str] = None,
        background: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        return_base64: bool = False
    ) -> Dict[str, Any]:
        """
        Render Mermaid diagram to image.
        
        Args:
            mermaid_code: Mermaid code to render
            format: Output format (png, svg, pdf)
            theme: Diagram theme
            background: Background color
            width: Output width
            height: Output height
            return_base64: Return base64 encoded image
            
        Returns:
            Dictionary with render results
        """
        logger.info(f"Tool: render_diagram - format: {format}")
        
        try:
            render_format = RenderFormat(format)
            render_theme = Theme(theme) if theme else Theme.DEFAULT
            
            response = await self.render_service.render(
                mermaid_code=mermaid_code,
                format=render_format,
                theme=render_theme,
                background=background or "white",
                width=width or 1920,
                height=height or 1080,
                return_base64=return_base64
            )
            
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Failed to render diagram: {e}")
            return RenderResponse(
                success=False,
                format=format,
                error=str(e)
            ).model_dump()
    
    async def get_download_link(self, file_path: str) -> Dict[str, Any]:
        """
        Get download URL for rendered diagram.
        
        Args:
            file_path: Path to diagram file
            
        Returns:
            Dictionary with download URL
        """
        logger.info(f"Tool: get_download_link - path: {file_path}")
        
        try:
            from pathlib import Path
            path = Path(file_path)
            filename = path.name
            
            return {
                "download_url": f"/download/{filename}",
                "file_path": str(path),
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"Failed to get download link: {e}")
            raise
    
    async def get_edit_link(self, mermaid_code: str) -> Dict[str, Any]:
        """
        Get Mermaid Live editor link.
        
        Args:
            mermaid_code: Mermaid code
            
        Returns:
            Dictionary with editor URL
        """
        logger.info("Tool: get_edit_link")
        
        try:
            live_url = create_mermaid_live_url(mermaid_code)
            ink_url = create_mermaid_ink_url(mermaid_code)
            
            return {
                "mermaid_live_url": live_url,
                "mermaid_ink_url": ink_url,
                "mermaid_code_length": len(mermaid_code)
            }
            
        except Exception as e:
            logger.error(f"Failed to get edit link: {e}")
            raise