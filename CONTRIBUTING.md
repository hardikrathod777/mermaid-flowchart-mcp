# Contributing to Mermaid MCP Server

Thank you for your interest in contributing! We welcome contributions from the community and are excited to help you get started.

## 🤝 Ways to Contribute

There are many ways to contribute to the project:

| Type | Description |
|------|-------------|
| 🐛 **Bug Reports** | Report bugs you find in the codebase |
| 💡 **Feature Requests** | Suggest new features or improvements |
| 📖 **Documentation** | Improve docs, README, or add examples |
| 💻 **Code Contributions** | Fix bugs, add features, refactor code |
| 🧪 **Testing** | Write tests or improve test coverage |
| 🎨 **Examples** | Create example diagrams or use cases |

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 16+ (for Playwright)
- Anthropic API key (for development)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/hardikrathod777/mermaid-flowchart-mcp
cd mermaid-mcp-server

# Create and activate virtual environment
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Copy environment template
cp .env.example .env

# Add your API key to .env
# ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### Running the Server

```bash
# Development with auto-reload
python main.py --reload

# Run tests
pytest

# Lint code
ruff check .
```

## 🔧 Development Guidelines

### Code Style

- Follow **PEP 8** for Python code
- Use **type hints** where possible
- Keep functions small and focused (max 50 lines)
- Write docstrings for all public functions

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Functions | `snake_case` | `generate_diagram` |
| Classes | `PascalCase` | `DiagramService` |
| Constants | `UPPER_SNAKE` | `MAX_RETRIES` |
| Private methods | `_leading_underscore` | `_validate_input` |

### Commit Messages

Use conventional commits:

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

**Example:**
```
feat(validation): add syntax checker for flowchart diagrams

- Implemented Mermaid syntax validation
- Added error reporting with line numbers
- Fixed validation timeout issues

Closes #42
```

### Pull Request Process

#### 1. Fork and Branch

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/hardikrathod777/mermaid-flowchart-mcp.git
cd mermaid-mcp-server

# Create a new branch
git checkout -b feature/my-awesome-feature
# or
git checkout -b fix/issue-description
```

#### 2. Make Changes

- Write clear, descriptive code
- Add tests for new functionality
- Update documentation if needed
- Keep commits atomic and focused

#### 3. Submit PR

```bash
# Push your branch
git push origin feature/my-awesome-feature
```

Then open a Pull Request with:

1. **Clear title** describing the change
2. **Detailed description** explaining:
   - What the change does
   - Why it's needed
   - How to test it
3. **Screenshots** for UI changes
4. **Linked issues** (e.g., "Fixes #123")

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commits are atomic
- [ ] PR description is complete

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_services.py -v
```

### Writing Tests

```python
# tests/test_services.py
import pytest
from mermaid_mcp.services.validation_service import ValidationService

class TestValidationService:
    """Tests for ValidationService."""
    
    def test_valid_mermaid_syntax(self):
        """Test that valid syntax passes validation."""
        service = ValidationService()
        result = service.validate("graph TD; A-->B;")
        assert result.is_valid is True
    
    def test_invalid_syntax_returns_error(self):
        """Test that invalid syntax returns error details."""
        service = ValidationService()
        result = service.validate("invalid syntax")
        assert result.is_valid is False
        assert result.errors is not None
```

## 📝 Documentation

### Docstring Format

Use Google-style docstrings:

```python
def generate_diagram(prompt: str, diagram_type: str = "flowchart") -> Diagram:
    """Generate a Mermaid diagram from a text prompt.

    Args:
        prompt: Natural language description of the diagram.
        diagram_type: Type of diagram to generate.
            Defaults to "flowchart".

    Returns:
        Diagram: The generated diagram object.

    Raises:
        ValidationError: If the generated diagram is invalid.
        RateLimitError: If API rate limit is exceeded.

    Example:
        >>> diagram = generate_diagram("User login flow", "sequence")
        >>> print(dagram.code)
        sequenceDiagram
            User->>System: Login
    """
```

## 🏗️ Architecture

```
mermaid-mcp-server/
├── src/mermaid_mcp/
│   ├── config.py          # Configuration & settings
│   ├── server.py          # MCP server implementation
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   │   ├── llm_service.py      # AI integration
│   │   ├── render_service.py   # Diagram rendering
│   │   └── validation_service.py
│   ├── tools/             # MCP tools
│   └── utils/             # Utilities
├── main.py                # Entry point
├── tests/                 # Test suite
└── diagrams/              # Output directory
```

## 📜 License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

⭐ Star us on GitHub if this project helped you!