"""FastAPI server with SSE support for MCP protocol."""
import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pathlib import Path

from .config import settings
from .tools.mcp_tools import MermaidMCPTools
from .utils.logging import logger


app = FastAPI(
    title="Mermaid MCP Server",
    description="MCP server for generating Mermaid diagrams using AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize tools
tools = MermaidMCPTools()


# MCP Tool Definitions
MCP_TOOLS = [
    {
        "name": "generate_diagram_from_prompt",
        "description": "Generate a Mermaid diagram from a natural language prompt. Automatically detects the best diagram type or accepts a specific type.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Natural language description of the diagram to generate"
                },
                "diagram_type": {
                    "type": "string",
                    "enum": ["flowchart", "sequenceDiagram", "classDiagram", "stateDiagram", "erDiagram", "gantt", "pie", "journey", "mindmap", "timeline", "quadrantChart"],
                    "description": "Optional: Specific diagram type to generate"
                },
                "theme": {
                    "type": "string",
                    "enum": ["default", "forest", "dark", "neutral", "base"],
                    "description": "Optional: Theme for the diagram"
                },
                "auto_fix": {
                    "type": "boolean",
                    "description": "Automatically fix invalid Mermaid syntax",
                    "default": True
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "generate_diagram_from_type",
        "description": "Generate a specific type of Mermaid diagram with a description of the content.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "diagram_type": {
                    "type": "string",
                    "enum": ["flowchart", "sequenceDiagram", "classDiagram", "stateDiagram", "erDiagram", "gantt", "pie", "journey", "mindmap", "timeline", "quadrantChart"],
                    "description": "Type of diagram to generate"
                },
                "description": {
                    "type": "string",
                    "description": "Description of what should be in the diagram"
                },
                "theme": {
                    "type": "string",
                    "enum": ["default", "forest", "dark", "neutral", "base"],
                    "description": "Optional: Theme for the diagram"
                },
                "auto_fix": {
                    "type": "boolean",
                    "description": "Automatically fix invalid Mermaid syntax",
                    "default": True
                }
            },
            "required": ["diagram_type", "description"]
        }
    },
    {
        "name": "validate_mermaid",
        "description": "Validate Mermaid diagram code for syntax errors.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mermaid_code": {
                    "type": "string",
                    "description": "Mermaid diagram code to validate"
                }
            },
            "required": ["mermaid_code"]
        }
    },
    {
        "name": "fix_mermaid",
        "description": "Automatically fix invalid Mermaid diagram code.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mermaid_code": {
                    "type": "string",
                    "description": "Invalid Mermaid code to fix"
                },
                "error_message": {
                    "type": "string",
                    "description": "Optional: Error message from validation"
                }
            },
            "required": ["mermaid_code"]
        }
    },
    {
        "name": "render_diagram",
        "description": "Render a Mermaid diagram to an image file (PNG, SVG, or PDF).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mermaid_code": {
                    "type": "string",
                    "description": "Mermaid diagram code to render"
                },
                "format": {
                    "type": "string",
                    "enum": ["png", "svg", "pdf"],
                    "description": "Output image format",
                    "default": "png"
                },
                "theme": {
                    "type": "string",
                    "enum": ["default", "forest", "dark", "neutral", "base"],
                    "description": "Diagram theme"
                },
                "background": {
                    "type": "string",
                    "description": "Background color (e.g., 'white', '#ffffff', 'transparent')",
                    "default": "white"
                },
                "width": {
                    "type": "integer",
                    "description": "Output width in pixels",
                    "default": 1920
                },
                "height": {
                    "type": "integer",
                    "description": "Output height in pixels",
                    "default": 1080
                },
                "return_base64": {
                    "type": "boolean",
                    "description": "Return base64 encoded image instead of file path",
                    "default": False
                }
            },
            "required": ["mermaid_code"]
        }
    },
    {
        "name": "get_download_link",
        "description": "Get a download URL for a rendered diagram file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the diagram file"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "get_edit_link",
        "description": "Get Mermaid Live Editor URL to edit and preview a diagram.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mermaid_code": {
                    "type": "string",
                    "description": "Mermaid diagram code"
                }
            },
            "required": ["mermaid_code"]
        }
    }
]


def _jsonrpc_result(response_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
    """Build a JSON-RPC success response."""
    return {"jsonrpc": "2.0", "id": response_id, "result": result}


def _jsonrpc_error(
    response_id: Any,
    code: int,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Build a JSON-RPC error response."""
    error: Dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": response_id, "error": error}


async def _dispatch_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Route tool call to the correct implementation."""
    if tool_name == "generate_diagram_from_prompt":
        return await tools.generate_diagram_from_prompt(**arguments)
    if tool_name == "generate_diagram_from_type":
        return await tools.generate_diagram_from_type(**arguments)
    if tool_name == "validate_mermaid":
        return await tools.validate_mermaid(**arguments)
    if tool_name == "fix_mermaid":
        return await tools.fix_mermaid(**arguments)
    if tool_name == "render_diagram":
        return await tools.render_diagram(**arguments)
    if tool_name == "get_download_link":
        return await tools.get_download_link(**arguments)
    if tool_name == "get_edit_link":
        return await tools.get_edit_link(**arguments)

    raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Mermaid MCP Server",
        "version": "1.0.0",
        "description": "MCP server for generating Mermaid diagrams with AI",
        "endpoints": {
            "sse": "/sse",
            "download": "/download/{filename}",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mermaid-mcp-server"}


@app.get("/sse")
async def sse_endpoint(request: Request):
    """
    SSE endpoint for MCP protocol.
    Handles tool discovery and execution via Server-Sent Events.
    """
    logger.info("SSE connection established")

    async def event_generator():
        """Keep SSE connection alive without sending non-MCP payloads."""
        try:
            while True:
                if await request.is_disconnected():
                    logger.info("SSE client disconnected")
                    break

                await asyncio.sleep(1)
                # Keep this function as an async generator without emitting
                # non-MCP payloads that strict clients may try to parse.
                if False:
                    yield {"event": "noop", "data": "{}"}

        except Exception as e:
            logger.error(f"SSE error: {e}")

    return EventSourceResponse(event_generator(), ping=15)


@app.post("/sse")
async def sse_jsonrpc_endpoint(request: Request):
    """
    Streamable HTTP JSON-RPC endpoint.
    Supports initialize, tools/list, tools/call, and ping.
    """
    response_id = None
    try:
        body = await request.json()
        response_id = body.get("id")
        method = body.get("method")
        params = body.get("params", {})

        if body.get("jsonrpc") != "2.0" or not isinstance(method, str):
            return JSONResponse(
                _jsonrpc_error(response_id, -32600, "Invalid Request"),
                status_code=400
            )

        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "mermaid-mcp-server", "version": "1.0.0"},
            }
            return JSONResponse(_jsonrpc_result(response_id, result))

        if method == "notifications/initialized":
            return Response(status_code=202)

        if method == "ping":
            return JSONResponse(_jsonrpc_result(response_id, {}))

        if method == "tools/list":
            return JSONResponse(_jsonrpc_result(response_id, {"tools": MCP_TOOLS}))

        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            if not isinstance(tool_name, str):
                return JSONResponse(
                    _jsonrpc_error(response_id, -32602, "Invalid params: missing tool name"),
                    status_code=400
                )

            result = await _dispatch_tool(tool_name, arguments)
            tool_result = {
                "content": [{"type": "text", "text": json.dumps(result)}],
                "structuredContent": result,
                "isError": False,
            }
            return JSONResponse(_jsonrpc_result(response_id, tool_result))

        return JSONResponse(
            _jsonrpc_error(response_id, -32601, f"Method not found: {method}"),
            status_code=404
        )

    except HTTPException as e:
        logger.error(f"Tool execution error: {e.detail}")
        return JSONResponse(
            _jsonrpc_result(
                response_id,
                {
                    "content": [{"type": "text", "text": str(e.detail)}],
                    "isError": True,
                }
            )
        )
    except Exception as e:
        logger.error(f"JSON-RPC error: {e}")
        return JSONResponse(
            _jsonrpc_error(response_id, -32000, "Server error", {"detail": str(e)}),
            status_code=500
        )


@app.post("/execute")
async def execute_tool(request: Request):
    """
    Execute an MCP tool.
    
    Request body:
    {
        "tool": "tool_name",
        "arguments": {...}
    }
    """
    try:
        body = await request.json()
        tool_name = body.get("tool")
        arguments = body.get("arguments", {})
        
        logger.info(f"Executing tool: {tool_name}")
        
        result = await _dispatch_tool(tool_name, arguments)
        
        return {
            "success": True,
            "tool": tool_name,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download a rendered diagram file."""
    file_path = settings.diagrams_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )


@app.get("/tools")
async def list_tools():
    """List all available MCP tools."""
    return {
        "tools": MCP_TOOLS,
        "count": len(MCP_TOOLS)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info"
    )
