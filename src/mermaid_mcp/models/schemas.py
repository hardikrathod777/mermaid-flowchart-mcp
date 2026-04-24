"""Data models for Mermaid MCP Server."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, Dict, Any
from enum import Enum


class DiagramType(str, Enum):
    """Supported Mermaid diagram types."""
    FLOWCHART = "flowchart"
    SEQUENCE = "sequenceDiagram"
    CLASS = "classDiagram"
    STATE = "stateDiagram"
    ER = "erDiagram"
    GANTT = "gantt"
    PIE = "pie"
    JOURNEY = "journey"
    GITGRAPH = "gitGraph"
    MINDMAP = "mindmap"
    TIMELINE = "timeline"
    QUADRANT = "quadrantChart"


class RenderFormat(str, Enum):
    """Supported output formats."""
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"


class Theme(str, Enum):
    """Mermaid themes."""
    DEFAULT = "default"
    FOREST = "forest"
    DARK = "dark"
    NEUTRAL = "neutral"
    BASE = "base"


class GenerateDiagramRequest(BaseModel):
    """Request to generate diagram from natural language."""
    prompt: str = Field(..., description="Natural language description of the diagram")
    diagram_type: Optional[DiagramType] = Field(None, description="Preferred diagram type (auto-detected if not specified)")
    theme: Optional[Theme] = Field(Theme.DEFAULT, description="Diagram theme")
    auto_fix: bool = Field(True, description="Automatically fix invalid syntax")
    

class GenerateDiagramFromTypeRequest(BaseModel):
    """Request to generate specific diagram type."""
    diagram_type: DiagramType = Field(..., description="Type of diagram to generate")
    description: str = Field(..., description="Description of diagram content")
    theme: Optional[Theme] = Field(Theme.DEFAULT, description="Diagram theme")
    auto_fix: bool = Field(True, description="Automatically fix invalid syntax")


class ValidateMermaidRequest(BaseModel):
    """Request to validate Mermaid code."""
    mermaid_code: str = Field(..., description="Mermaid diagram code to validate")


class FixMermaidRequest(BaseModel):
    """Request to fix invalid Mermaid code."""
    mermaid_code: str = Field(..., description="Invalid Mermaid code to fix")
    error_message: Optional[str] = Field(None, description="Error message from validation")


class RenderDiagramRequest(BaseModel):
    """Request to render Mermaid diagram."""
    mermaid_code: str = Field(..., description="Mermaid diagram code")
    format: RenderFormat = Field(RenderFormat.PNG, description="Output format")
    theme: Optional[Theme] = Field(Theme.DEFAULT, description="Diagram theme")
    background: Optional[str] = Field("white", description="Background color")
    width: Optional[int] = Field(1920, description="Output width")
    height: Optional[int] = Field(1080, description="Output height")
    return_base64: bool = Field(False, description="Return base64 encoded image instead of file path")


class DiagramMetadata(BaseModel):
    """Metadata about generated diagram."""
    diagram_type: str
    node_count: int = 0
    edge_count: int = 0
    has_subgraphs: bool = False
    estimated_complexity: Literal["simple", "medium", "complex"] = "simple"


class DiagramResponse(BaseModel):
    """Response containing generated diagram."""
    mermaid_code: str
    diagram_type: str
    metadata: DiagramMetadata
    mermaid_live_url: str
    mermaid_ink_url: Optional[str] = None
    is_valid: bool = True
    validation_errors: Optional[list[str]] = None


class ValidationResponse(BaseModel):
    """Response from Mermaid validation."""
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    diagram_type: Optional[str] = None


class RenderResponse(BaseModel):
    """Response from diagram rendering."""
    success: bool
    file_path: Optional[str] = None
    base64_image: Optional[str] = None
    format: str
    download_url: Optional[str] = None
    error: Optional[str] = None


class FixResponse(BaseModel):
    """Response from fixing Mermaid code."""
    success: bool
    fixed_code: Optional[str] = None
    original_errors: list[str] = Field(default_factory=list)
    changes_made: list[str] = Field(default_factory=list)
    error: Optional[str] = None