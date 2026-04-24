"""Mermaid diagram utilities."""
import re
import base64
import json
import zlib
from typing import Optional, Tuple
from ..models.schemas import DiagramType, DiagramMetadata


def detect_diagram_type(mermaid_code: str) -> Optional[str]:
    """
    Detect the diagram type from Mermaid code.
    
    Args:
        mermaid_code: Mermaid diagram code
        
    Returns:
        Detected diagram type or None
    """
    code = mermaid_code.strip()
    
    # Check for explicit diagram type declarations
    if code.startswith("sequenceDiagram"):
        return "sequenceDiagram"
    elif code.startswith("classDiagram"):
        return "classDiagram"
    elif code.startswith("stateDiagram"):
        return "stateDiagram"
    elif code.startswith("erDiagram"):
        return "erDiagram"
    elif code.startswith("gantt"):
        return "gantt"
    elif code.startswith("pie"):
        return "pie"
    elif code.startswith("journey"):
        return "journey"
    elif code.startswith("gitGraph"):
        return "gitGraph"
    elif code.startswith("mindmap"):
        return "mindmap"
    elif code.startswith("timeline"):
        return "timeline"
    elif code.startswith("quadrantChart"):
        return "quadrantChart"
    elif code.startswith("flowchart") or code.startswith("graph"):
        return "flowchart"
    
    # Default to flowchart if no type detected
    return "flowchart"


def analyze_diagram(mermaid_code: str) -> DiagramMetadata:
    """
    Analyze Mermaid diagram and extract metadata.
    
    Args:
        mermaid_code: Mermaid diagram code
        
    Returns:
        DiagramMetadata with analysis results
    """
    diagram_type = detect_diagram_type(mermaid_code) or "unknown"
    
    # Count nodes (approximate - looks for node definitions)
    node_patterns = [
        r'\[.*?\]',  # [label]
        r'\(.*?\)',  # (label)
        r'\{.*?\}',  # {label}
        r'[A-Za-z0-9_]+\[',  # nodeId[
        r'[A-Za-z0-9_]+\(',  # nodeId(
    ]
    
    node_count = 0
    for pattern in node_patterns:
        node_count += len(re.findall(pattern, mermaid_code))
    
    # Count edges (arrows and connections)
    edge_patterns = [
        r'-->',
        r'---',
        r'-.->',
        r'==>',
        r'-..-',
        r'->>',
        r'<<->>',
    ]
    
    edge_count = 0
    for pattern in edge_patterns:
        edge_count += mermaid_code.count(pattern)
    
    # Check for subgraphs
    has_subgraphs = 'subgraph' in mermaid_code.lower()
    
    # Estimate complexity
    total_elements = node_count + edge_count
    if total_elements < 5:
        complexity = "simple"
    elif total_elements < 15:
        complexity = "medium"
    else:
        complexity = "complex"
    
    return DiagramMetadata(
        diagram_type=diagram_type,
        node_count=node_count,
        edge_count=edge_count,
        has_subgraphs=has_subgraphs,
        estimated_complexity=complexity
    )


def create_mermaid_live_url(mermaid_code: str) -> str:
    """
    Create a Mermaid Live Editor URL.
    
    Args:
        mermaid_code: Mermaid diagram code
        
    Returns:
        URL to edit diagram in Mermaid Live
    """
    # Mermaid Live expects a compressed state object in #pako format.
    state = {
        "code": mermaid_code,
        "mermaid": json.dumps({"theme": "default"}),
        "autoSync": True
    }
    payload = json.dumps(state, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(payload, 9)  # zlib-wrapped deflate
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
    return f"https://mermaid.live/edit#pako:{encoded}"


def create_mermaid_ink_url(mermaid_code: str) -> str:
    """
    Create a Mermaid Ink rendering URL.
    
    Args:
        mermaid_code: Mermaid diagram code
        
    Returns:
        URL to render diagram via Mermaid Ink
    """
    encoded = base64.b64encode(mermaid_code.encode('utf-8')).decode('ascii')
    return f"https://mermaid.ink/img/{encoded}"


def extract_mermaid_from_markdown(text: str) -> Optional[str]:
    """
    Extract Mermaid code from markdown code blocks.
    
    Args:
        text: Text that may contain Mermaid code
        
    Returns:
        Extracted Mermaid code or None
    """
    # Look for ```mermaid code blocks
    pattern = r'```mermaid\s*\n(.*?)\n```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Look for plain ``` code blocks
    pattern = r'```\s*\n(.*?)\n```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        code = match.group(1).strip()
        # Check if it looks like Mermaid
        if any(keyword in code for keyword in [
            'graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
            'stateDiagram', 'erDiagram', 'gantt', 'pie', 'journey'
        ]):
            return code
    
    # Return as-is if no code blocks found
    return text.strip()


def clean_mermaid_code(mermaid_code: str) -> str:
    """
    Clean and normalize Mermaid code.
    
    Args:
        mermaid_code: Raw Mermaid code
        
    Returns:
        Cleaned Mermaid code
    """
    # Extract from markdown if needed
    code = extract_mermaid_from_markdown(mermaid_code)
    if not code:
        code = mermaid_code
    
    # Remove extra whitespace
    lines = [line.rstrip() for line in code.split('\n')]
    code = '\n'.join(line for line in lines if line)
    
    return code.strip()


def infer_diagram_type_from_prompt(prompt: str) -> DiagramType:
    """
    Infer the best diagram type from a natural language prompt.
    
    Args:
        prompt: User's natural language description
        
    Returns:
        Inferred DiagramType
    """
    prompt_lower = prompt.lower()
    
    # Sequence diagram keywords
    if any(keyword in prompt_lower for keyword in [
        'sequence', 'interaction', 'api call', 'request', 'response',
        'communication', 'message flow', 'protocol'
    ]):
        return DiagramType.SEQUENCE
    
    # Class diagram keywords
    if any(keyword in prompt_lower for keyword in [
        'class', 'object', 'inheritance', 'oop', 'uml class',
        'relationship', 'attribute', 'method'
    ]):
        return DiagramType.CLASS
    
    # State diagram keywords
    if any(keyword in prompt_lower for keyword in [
        'state', 'transition', 'fsm', 'finite state', 'lifecycle',
        'status change'
    ]):
        return DiagramType.STATE
    
    # ER diagram keywords
    if any(keyword in prompt_lower for keyword in [
        'database', 'entity', 'relationship', 'er diagram', 'schema',
        'table', 'foreign key'
    ]):
        return DiagramType.ER
    
    # Gantt chart keywords
    if any(keyword in prompt_lower for keyword in [
        'gantt', 'timeline', 'schedule', 'project plan', 'milestone',
        'task timeline'
    ]):
        return DiagramType.GANTT
    
    # Pie chart keywords
    if any(keyword in prompt_lower for keyword in [
        'pie chart', 'percentage', 'distribution', 'proportion',
        'breakdown'
    ]):
        return DiagramType.PIE
    
    # User journey keywords
    if any(keyword in prompt_lower for keyword in [
        'user journey', 'customer journey', 'experience', 'touchpoint'
    ]):
        return DiagramType.JOURNEY
    
    # Mindmap keywords
    if any(keyword in prompt_lower for keyword in [
        'mindmap', 'mind map', 'brainstorm', 'hierarchy'
    ]):
        return DiagramType.MINDMAP
    
    # Default to flowchart for process/flow descriptions
    return DiagramType.FLOWCHART
