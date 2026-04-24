"""Mermaid diagram validation service."""
import re
from typing import List, Tuple
from ..models.schemas import ValidationResponse
from ..utils.logging import logger
from ..utils.mermaid import detect_diagram_type


class ValidationService:
    """Service for validating Mermaid diagram syntax."""
    
    def __init__(self):
        """Initialize validation service."""
        pass
    
    async def validate(self, mermaid_code: str) -> ValidationResponse:
        """
        Validate Mermaid diagram code.
        
        Args:
            mermaid_code: Mermaid diagram code to validate
            
        Returns:
            ValidationResponse with validation results
        """
        logger.info("Validating Mermaid code")
        
        errors = []
        warnings = []
        
        # Basic structure validation
        if not mermaid_code or not mermaid_code.strip():
            errors.append("Empty diagram code")
            return ValidationResponse(
                is_valid=False,
                errors=errors,
                warnings=warnings
            )
        
        # Detect diagram type
        diagram_type = detect_diagram_type(mermaid_code)
        
        # Type-specific validation
        if diagram_type == "flowchart":
            errors.extend(self._validate_flowchart(mermaid_code))
        elif diagram_type == "sequenceDiagram":
            errors.extend(self._validate_sequence(mermaid_code))
        elif diagram_type == "classDiagram":
            errors.extend(self._validate_class(mermaid_code))
        elif diagram_type == "stateDiagram":
            errors.extend(self._validate_state(mermaid_code))
        elif diagram_type == "erDiagram":
            errors.extend(self._validate_er(mermaid_code))
        elif diagram_type == "gantt":
            errors.extend(self._validate_gantt(mermaid_code))
        elif diagram_type == "pie":
            errors.extend(self._validate_pie(mermaid_code))
        
        # Common syntax checks
        common_errors = self._validate_common_syntax(mermaid_code)
        errors.extend(common_errors)
        
        # Check for warnings
        warnings.extend(self._check_warnings(mermaid_code))
        
        is_valid = len(errors) == 0
        
        logger.info(f"Validation complete: {'Valid' if is_valid else 'Invalid'}")
        if errors:
            logger.warning(f"Validation errors: {errors}")
        
        return ValidationResponse(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            diagram_type=diagram_type
        )
    
    def _validate_flowchart(self, code: str) -> List[str]:
        """Validate flowchart specific syntax."""
        errors = []
        
        # Check for graph declaration
        if not (code.strip().startswith('flowchart') or code.strip().startswith('graph')):
            errors.append("Flowchart must start with 'flowchart' or 'graph' keyword")
        
        # Check for proper direction
        first_line = code.strip().split('\n')[0]
        if 'flowchart' in first_line or 'graph' in first_line:
            if not any(direction in first_line for direction in ['TD', 'TB', 'BT', 'RL', 'LR']):
                # Warning, not error - default is TD
                pass
        
        return errors
    
    def _validate_sequence(self, code: str) -> List[str]:
        """Validate sequence diagram specific syntax."""
        errors = []
        
        if not code.strip().startswith('sequenceDiagram'):
            errors.append("Sequence diagram must start with 'sequenceDiagram' keyword")
        
        # Check for participant declarations (optional but recommended)
        lines = code.split('\n')
        has_interactions = any('->>' in line or '->>' in line for line in lines)
        
        if not has_interactions:
            errors.append("Sequence diagram should have at least one interaction (->>, ->, etc.)")
        
        return errors
    
    def _validate_class(self, code: str) -> List[str]:
        """Validate class diagram specific syntax."""
        errors = []
        
        if not code.strip().startswith('classDiagram'):
            errors.append("Class diagram must start with 'classDiagram' keyword")
        
        return errors
    
    def _validate_state(self, code: str) -> List[str]:
        """Validate state diagram specific syntax."""
        errors = []
        
        if not code.strip().startswith('stateDiagram'):
            errors.append("State diagram must start with 'stateDiagram' or 'stateDiagram-v2' keyword")
        
        return errors
    
    def _validate_er(self, code: str) -> List[str]:
        """Validate ER diagram specific syntax."""
        errors = []
        
        if not code.strip().startswith('erDiagram'):
            errors.append("ER diagram must start with 'erDiagram' keyword")
        
        return errors
    
    def _validate_gantt(self, code: str) -> List[str]:
        """Validate Gantt chart specific syntax."""
        errors = []
        
        if not code.strip().startswith('gantt'):
            errors.append("Gantt chart must start with 'gantt' keyword")
        
        # Check for required elements
        if 'title' not in code.lower():
            # Warning only - title is recommended but not required
            pass
        
        return errors
    
    def _validate_pie(self, code: str) -> List[str]:
        """Validate pie chart specific syntax."""
        errors = []
        
        if not code.strip().startswith('pie'):
            errors.append("Pie chart must start with 'pie' keyword")
        
        return errors
    
    def _validate_common_syntax(self, code: str) -> List[str]:
        """Validate common syntax issues."""
        errors = []
        
        # Check for unmatched brackets
        brackets = {'[': ']', '(': ')', '{': '}', '<': '>'}
        stack = []
        
        for char in code:
            if char in brackets.keys():
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    errors.append(f"Unmatched closing bracket: {char}")
                else:
                    opening = stack.pop()
                    if brackets[opening] != char:
                        errors.append(f"Mismatched brackets: {opening} and {char}")
        
        if stack:
            errors.append(f"Unclosed brackets: {', '.join(stack)}")
        
        # Check for invalid characters in node IDs
        # Node IDs should be alphanumeric with underscores
        node_id_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\['
        for match in re.finditer(node_id_pattern, code):
            node_id = match.group(1)
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', node_id):
                errors.append(f"Invalid node ID: {node_id}")
        
        return errors
    
    def _check_warnings(self, code: str) -> List[str]:
        """Check for non-critical issues."""
        warnings = []
        
        # Check for very long lines
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 200:
                warnings.append(f"Line {i} is very long ({len(line)} chars), consider breaking it up")
        
        # Check for excessive nesting in flowcharts
        if 'subgraph' in code.lower():
            subgraph_count = code.lower().count('subgraph')
            if subgraph_count > 5:
                warnings.append(f"High number of subgraphs ({subgraph_count}), may be hard to read")
        
        return warnings