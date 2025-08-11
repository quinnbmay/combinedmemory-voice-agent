#!/usr/bin/env python3
"""
Fully compliant MCP server for ElevenLabs integration
Implements Model Context Protocol specification
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from mem0 import MemoryClient
import uuid
from pydantic import BaseModel

app = FastAPI(title="Mem0 MCP Server")

# Initialize Mem0
mem0_client = MemoryClient(
    api_key=os.environ.get('MEM0_API_KEY', 'm0-IQGqsMWB42QhWG77RuzpSdNcyEppgRHeBhz0KcNu')
)

USER_ID = 'quinn_may'

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: str
    params: Optional[Dict[str, Any]] = None

@app.post("/")
async def mcp_handler(request: MCPRequest):
    """Main MCP handler - processes all MCP requests"""
    
    request_id = request.id or str(uuid.uuid4())
    method = request.method
    params = request.params or {}
    
    # Handle different MCP methods
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "0.1.0",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "mem0-server",
                    "version": "1.0.0"
                }
            }
        }
    
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "store_memory",
                        "description": "Store important information from conversations",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "The information to remember"
                                }
                            },
                            "required": ["content"]
                        }
                    },
                    {
                        "name": "search_memories",
                        "description": "Search stored memories",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                ]
            }
        }
    
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "store_memory":
            content = arguments.get("content")
            if not content:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "content parameter is required"
                    }
                }
            
            # Store in Mem0
            now = datetime.now()
            metadata = {
                "category": "elevenlabs_mcp",
                "timestamp": now.isoformat(),
                "source": "mcp_server"
            }
            
            result = mem0_client.add(
                messages=[{"role": "user", "content": content}],
                user_id=USER_ID,
                metadata=metadata
            )
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Memory stored successfully"
                        }
                    ]
                }
            }
        
        elif tool_name == "search_memories":
            query = arguments.get("query")
            if not query:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "query parameter is required"
                    }
                }
            
            # Search Mem0
            results = mem0_client.search(
                query=query,
                user_id=USER_ID,
                limit=5
            )
            
            memories = "\n".join([
                f"• {r.get('memory', '')}"
                for r in results.get('results', [])
            ])
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": memories or "No memories found"
                        }
                    ]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
    
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

@app.get("/")
async def sse_handler(request: Request):
    """SSE handler for MCP over SSE transport"""
    
    async def event_stream():
        # Send initial connection
        yield f"event: open\n"
        yield f"data: {json.dumps({'type': 'open'})}\n\n"
        
        # Keep alive
        while True:
            if await request.is_disconnected():
                break
            await asyncio.sleep(30)
            yield f": ping\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.options("/")
async def options_handler():
    """Handle CORS preflight"""
    return Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600"
        }
    )

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)