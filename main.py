"""Main entry point for Mermaid MCP Server."""
import sys
import argparse
import uvicorn
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mermaid_mcp.config import settings
from mermaid_mcp.utils.logging import logger

def main():
    """Run the MCP server."""
    parser = argparse.ArgumentParser(
        description="Mermaid MCP Server - AI-powered diagram generation"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=settings.host,
        help=f"Host to bind to (default: {settings.host})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help=f"Port to bind to (default: {settings.port})"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Log level (default: info)"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting Mermaid MCP Server on {args.host}:{args.port}")
    logger.info(f"Diagrams will be saved to: {settings.diagrams_dir.absolute()}")
    logger.info(f"Using model: {settings.llm_model}")
    
    # Check API key     
    if not settings.openai_api_key:
        logger.error("OPENAI_API_KEY not set!")
        logger.error("Please set it in .env file or environment variable")
        sys.exit(1)
    
    # Run server
    uvicorn.run(
        "mermaid_mcp.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main()
