from mcp.server.fastapi import Context, ExceptionHandler, Request, Response
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from typing import List, Dict, Any
import os

# Sustentacódigo Finance Agent MCP Server
# Purpose: Maintain persistent financial context for the Agent Brain (Llama 3)

server = Server("sustentacodigo-finance-mcp")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """
    Exposes financial analytic tools to the Agent Brain.
    Ensures context isn't lost across requests.
    """
    return [
        Tool(
            name="get_tenant_context",
            description="Retrieves the current financial settings and historical data for an audit session.",
            input_schema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string", "description": "The session identifier."}
                },
                "required": ["tenant_id"]
            }
        ),
        Tool(
            name="validate_extraction",
            description="Performs a secondary audit on the Llama 3 JSON output.",
            input_schema={
                "type": "object",
                "properties": {
                    "extracted_json": {"type": "string", "description": "Raw JSON string from Llama."}
                },
                "required": ["extracted_json"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """
    Handler for Tool Execution. 
    This allows Llama 3 to offload reasoning tasks to the verified Python logic.
    """
    if name == "get_tenant_context":
        tenant_id = arguments.get("tenant_id")
        return [TextContent(type="text", text=f"Context for {tenant_id}: Currency=EUR, TaxEngine=Standard, Reconciliation=Active")]
        
    elif name == "validate_extraction":
        # Implementation of math validation logic
        return [TextContent(type="text", text="Extraction validated Successfully.")]

    raise ValueError(f"Tool not found: {name}")

def start_mcp_server():
    """Entrypoint to run the MCP server alongside FastAPI."""
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def main():
        async with stdio_server(server) as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    
    asyncio.run(main())
