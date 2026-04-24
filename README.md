# 🎨 Mermaid MCP Server

**AI-Powered Mermaid Diagram Generation via Model Context Protocol (MCP)**

A production-ready MCP server that generates, validates, fixes, and renders Mermaid diagrams using Claude AI. Perfect for creating flowcharts, sequence diagrams, class diagrams, and more from natural language descriptions.

## 🌟 Features

- ✨ **Natural Language to Diagrams**: Describe what you want, get a diagram
- 🤖 **AI-Powered**: Uses Claude Sonnet 4 for intelligent diagram generation
- 🔧 **Auto-Fix**: Automatically corrects invalid Mermaid syntax
- 🎨 **Multiple Formats**: Export to PNG, SVG, or PDF
- 🔍 **Validation**: Built-in syntax validation and error reporting
- 🔗 **Live Editor Links**: Get instant Mermaid Live Editor URLs
- 📊 **11+ Diagram Types**: Flowcharts, sequences, classes, states, and more
- 🚀 **SSE Transport**: Real-time streaming via Server-Sent Events
- 🎯 **Smart Type Detection**: Automatically chooses the best diagram type

## 📋 Supported Diagram Types

| Type | Use Case | Example Prompt |
|------|----------|----------------|
| `flowchart` | Processes, workflows, decision trees | "Create a login flow" |
| `sequenceDiagram` | API interactions, message flows | "API authentication flow" |
| `classDiagram` | OOP structures, class relationships | "User management system classes" |
| `stateDiagram` | State machines, lifecycles | "Order status lifecycle" |
| `erDiagram` | Database schemas | "E-commerce database schema" |
| `gantt` | Project timelines, schedules | "Website launch timeline" |
| `pie` | Percentages, distributions | "Market share breakdown" |
| `journey` | User/customer journeys | "Customer onboarding journey" |
| `mindmap` | Hierarchical concepts | "Product feature brainstorm" |
| `gitGraph` | Git branching strategies | "Feature branch workflow" |
| `timeline` | Chronological events | "Company milestones" |
| `quadrantChart` | 2x2 matrices | "Priority matrix" |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API key
- Node.js 16+ (for Playwright browser automation)

### Installation

```bash
# Clone the repository
cd mermaid-mcp-server

# Create virtual environment
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Copy environment template
cp .env.example .env

# Edit .env and add your Anthropic API key
nano .env  # or use your preferred editor
```

### Configuration

Edit `.env` file:

```env
OPENAI_API_KEY=sk-ant-xxxxxxxxxxxxx
HOST=0.0.0.0
PORT=3000
LLM_MODEL=gpt-4.1-mini
```

### Run the Server

```bash
# Development mode with auto-reload
python main.py --reload

# Production mode
python main.py --host 0.0.0.0 --port 3000

# With custom settings
python main.py --host localhost --port 8000 --log-level debug
```

Server will start at: `http://localhost:3000`

## 🔧 MCP Tools

### 1. `generate_diagram_from_prompt`

Generate diagram from natural language description.

**Input:**
```json
{
  "prompt": "Create a user authentication flow with login, registration, and password reset",
  "diagram_type": "flowchart",  // optional
  "theme": "dark",  // optional
  "auto_fix": true  // optional
}
```

**Output:**
```json
{
  "mermaid_code": "flowchart TD\n  Start[User] --> Login...",
  "diagram_type": "flowchart",
  "metadata": {
    "node_count": 12,
    "edge_count": 15,
    "estimated_complexity": "medium"
  },
  "mermaid_live_url": "https://mermaid.live/edit#base64:...",
  "mermaid_ink_url": "https://mermaid.ink/img/...",
  "is_valid": true
}
```

### 2. `generate_diagram_from_type`

Generate specific diagram type with description.

**Input:**
```json
{
  "diagram_type": "sequenceDiagram",
  "description": "Show OAuth 2.0 authorization flow between client, auth server, and resource server"
}
```

### 3. `validate_mermaid`

Validate Mermaid syntax.

**Input:**
```json
{
  "mermaid_code": "flowchart TD\n  A --> B"
}
```

**Output:**
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [],
  "diagram_type": "flowchart"
}
```

### 4. `fix_mermaid`

Auto-fix invalid Mermaid code.

**Input:**
```json
{
  "mermaid_code": "flowchart TD\n  A -> B",  // invalid syntax
  "error_message": "Invalid arrow syntax"
}
```

**Output:**
```json
{
  "success": true,
  "fixed_code": "flowchart TD\n  A --> B",
  "original_errors": ["Invalid arrow syntax"],
  "changes_made": ["Fixed all syntax errors"]
}
```

### 5. `render_diagram`

Render diagram to image.

**Input:**
```json
{
  "mermaid_code": "flowchart TD\n  A --> B",
  "format": "png",
  "theme": "dark",
  "background": "transparent",
  "width": 1920,
  "height": 1080,
  "return_base64": false
}
```

**Output:**
```json
{
  "success": true,
  "file_path": "/path/to/diagram_20250330_123456_abc123.png",
  "download_url": "/download/diagram_20250330_123456_abc123.png",
  "format": "png"
}
```

### 6. `get_download_link`

Get download URL for rendered file.

**Input:**
```json
{
  "file_path": "/path/to/diagram.png"
}
```

### 7. `get_edit_link`

Get Mermaid Live Editor URL.

**Input:**
```json
{
  "mermaid_code": "flowchart TD\n  A --> B"
}
```

**Output:**
```json
{
  "mermaid_live_url": "https://mermaid.live/edit#base64:Zmxvd2NoYXJ0IFREICBBIC0tPiBC",
  "mermaid_ink_url": "https://mermaid.ink/img/Zmxvd2NoYXJ0IFREICBBIC0tPiBC"
}
```

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:3000/health
```

### List Tools
```bash
curl http://localhost:3000/tools
```

### Execute Tool
```bash
curl -X POST http://localhost:3000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "generate_diagram_from_prompt",
    "arguments": {
      "prompt": "Create a simple login flow"
    }
  }'
```

### SSE Connection
```bash
curl -N http://localhost:3000/sse
```

### Download File
```bash
curl http://localhost:3000/download/diagram_20250330_123456.png --output diagram.png
```

## 🎯 Usage Examples

### Example 1: Generate Flowchart

```python
import requests

response = requests.post('http://localhost:3000/execute', json={
    "tool": "generate_diagram_from_prompt",
    "arguments": {
        "prompt": "Create a flowchart for processing a customer order with payment, inventory check, and shipping"
    }
})

result = response.json()
print(f"Diagram code:\n{result['result']['mermaid_code']}")
print(f"Live editor: {result['result']['mermaid_live_url']}")
```

### Example 2: Generate and Render

```python
# Step 1: Generate diagram
gen_response = requests.post('http://localhost:3000/execute', json={
    "tool": "generate_diagram_from_prompt",
    "arguments": {
        "prompt": "Database schema for a blog with users, posts, and comments"
    }
})

mermaid_code = gen_response.json()['result']['mermaid_code']

# Step 2: Render to PNG
render_response = requests.post('http://localhost:3000/execute', json={
    "tool": "render_diagram",
    "arguments": {
        "mermaid_code": mermaid_code,
        "format": "png",
        "theme": "dark"
    }
})

download_url = render_response.json()['result']['download_url']
print(f"Download: http://localhost:3000{download_url}")
```

### Example 3: Sequence Diagram

```python
response = requests.post('http://localhost:3000/execute', json={
    "tool": "generate_diagram_from_type",
    "arguments": {
        "diagram_type": "sequenceDiagram",
        "description": "User logs in, gets JWT token, makes authenticated API request"
    }
})

print(response.json()['result']['mermaid_code'])
```

### Example 4: Fix Invalid Code

```python
invalid_code = """
flowchart TD
  A -> B  # Wrong arrow syntax
  B -> C
"""

response = requests.post('http://localhost:3000/execute', json={
    "tool": "fix_mermaid",
    "arguments": {
        "mermaid_code": invalid_code
    }
})

print(f"Fixed code:\n{response.json()['result']['fixed_code']}")
```

## 🏗️ Architecture

```
mermaid-mcp-server/
├── src/mermaid_mcp/
│   ├── models/          # Pydantic data models
│   │   └── schemas.py
│   ├── services/        # Business logic
│   │   ├── llm_service.py      # Claude AI integration
│   │   ├── validation_service.py  # Mermaid validation
│   │   └── render_service.py   # Playwright rendering
│   ├── tools/           # MCP tools
│   │   └── mcp_tools.py
│   ├── utils/           # Utilities
│   │   ├── logging.py
│   │   └── mermaid.py
│   ├── config.py        # Configuration
│   └── server.py        # FastAPI SSE server
├── diagrams/            # Rendered diagrams (auto-created)
├── main.py              # Entry point
├── requirements.txt
└── README.md
```

### Design Principles

1. **Service Layer Pattern**: Clean separation of concerns
2. **Dependency Injection**: Services are loosely coupled
3. **Type Safety**: Full Pydantic validation
4. **Error Handling**: Comprehensive try-catch with logging
5. **Retry Logic**: Auto-retry for LLM failures
6. **Async/Await**: Non-blocking I/O operations

## 🔒 Security

- API keys stored in environment variables
- Input validation via Pydantic
- Rate limiting (configurable)
- CORS enabled for cross-origin requests
- No sensitive data in logs

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=src/mermaid_mcp tests/

# Specific test
pytest tests/test_llm_service.py -v
```

## 🐛 Troubleshooting

### "ANTHROPIC_API_KEY not set"
- Copy `.env.example` to `.env`
- Add your API key: `ANTHROPIC_API_KEY=sk-ant-xxx...`

### "Playwright not installed"
```bash
playwright install chromium
```

### "Port already in use"
```bash
python main.py --port 8000
```

### Diagram rendering fails
- Check Playwright browser installation
- Verify network access to CDN (cdn.jsdelivr.net)
- Check logs: `python main.py --log-level debug`

## 📊 Performance

- **Diagram Generation**: 2-5 seconds (Claude API)
- **Validation**: <100ms (regex-based)
- **Rendering**: 1-3 seconds (Playwright)
- **Auto-Fix**: 3-6 seconds (Claude API)

## 🛣️ Roadmap

- [ ] Diagram templates library
- [ ] Multi-diagram batch generation
- [ ] Diagram history/versioning
- [ ] WebSocket support
- [ ] Diagram collaboration features
- [ ] Custom theme editor
- [ ] Export to PowerPoint/Google Slides
- [ ] Git integration (commit diagrams)

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [Mermaid.js](https://mermaid.js.org/) - Diagram syntax
- [Anthropic Claude](https://www.anthropic.com/) - AI generation
- [Playwright](https://playwright.dev/) - Browser automation
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourorg/mermaid-mcp-server/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourorg/mermaid-mcp-server/discussions)
- 📧 **Email**: support@example.com

---

**Built with ❤️ using MCP, Claude AI, and Mermaid**