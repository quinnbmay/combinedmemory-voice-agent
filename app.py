#!/usr/bin/env python3
"""
CombinedMemory Voice Agent - Web Interface for Railway
ElevenLabs + Mem0 Integration with SSE Support
"""

import os
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from mem0 import MemoryClient
from dotenv import load_dotenv
import uvicorn
from typing import AsyncGenerator
import uuid

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="CombinedMemory Voice Agent")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global configuration
USER_ID = os.environ.get('USER_ID', 'quinn_may')
MEM0_API_KEY = os.environ.get('MEM0_API_KEY')
AGENT_ID = os.environ.get('AGENT_ID', 'mem')
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')
CLIENT = os.environ.get('MEM0_CLIENT', 'CombinedMemory.com')
PROJECT_TYPE = os.environ.get('MEM0_PROJECT_TYPE', 'voice_ai_assistant')
DEVICE = os.environ.get('MEM0_DEVICE', 'railway_deployment')

# Initialize Mem0 client
mem0_client = None
if MEM0_API_KEY:
    mem0_client = MemoryClient(api_key=MEM0_API_KEY)

# SSE Memory Queue for broadcasting
memory_queue = asyncio.Queue()
active_connections = []

async def broadcast_memory(memory_data):
    """Broadcast memory to all SSE connections"""
    for connection in active_connections[:]:
        try:
            await connection.put(memory_data)
        except:
            active_connections.remove(connection)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface with SSE test"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>CombinedMemory Voice Agent</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .status {
            background: #f0f4f8;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
        }
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge.success {
            background: #10b981;
            color: white;
        }
        .badge.info {
            background: #3b82f6;
            color: white;
        }
        .badge.warning {
            background: #fbbf24;
            color: #92400e;
        }
        .actions {
            margin-top: 30px;
        }
        .btn {
            display: block;
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        .btn-secondary {
            background: #e5e7eb;
            color: #333;
        }
        .btn-secondary:hover {
            background: #d1d5db;
        }
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        .btn-danger:hover {
            background: #dc2626;
        }
        .info-box {
            background: #fef3c7;
            border: 1px solid #fbbf24;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .info-box h3 {
            margin-top: 0;
            color: #92400e;
        }
        .code {
            background: #1f2937;
            color: #10b981;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            overflow-x: auto;
        }
        .sse-status {
            background: #f3f4f6;
            border: 2px solid #e5e7eb;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .sse-messages {
            max-height: 200px;
            overflow-y: auto;
            background: #1f2937;
            color: #10b981;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ CombinedMemory Voice Agent</h1>
        <p class="subtitle">Powered by ElevenLabs + Mem0 + SSE</p>
        
        <div class="status">
            <h3>System Status</h3>
            <div class="status-item">
                <span>Memory Backend</span>
                <span class="badge success">Connected</span>
            </div>
            <div class="status-item">
                <span>ElevenLabs Agent</span>
                <span class="badge success">Configured</span>
            </div>
            <div class="status-item">
                <span>SSE Endpoint</span>
                <span id="sse-status" class="badge warning">Disconnected</span>
            </div>
            <div class="status-item">
                <span>User ID</span>
                <span class="badge info">quinn_may</span>
            </div>
            <div class="status-item">
                <span>Agent ID</span>
                <span class="badge info">mem</span>
            </div>
        </div>

        <div class="info-box">
            <h3>📱 SSE Memory Stream</h3>
            <p>The SSE endpoint is now available at:</p>
            <div class="code">
                GET /sse - Stream memory updates<br>
                POST /sse - Push memory to stream
            </div>
        </div>

        <div class="sse-status">
            <h3>🔄 SSE Connection Test</h3>
            <button class="btn btn-primary" onclick="connectSSE()">Connect to SSE Stream</button>
            <button class="btn btn-secondary" onclick="testSSEPost()">Test POST to SSE</button>
            <button class="btn btn-danger" onclick="disconnectSSE()">Disconnect SSE</button>
            <div class="sse-messages" id="sse-messages">
                SSE messages will appear here...
            </div>
        </div>

        <div class="actions">
            <button class="btn btn-primary" onclick="testMemory()">Test Memory System</button>
            <button class="btn btn-secondary" onclick="viewStats()">View Statistics</button>
        </div>

        <div id="result" style="margin-top: 20px;"></div>
    </div>

    <script>
        let eventSource = null;

        function connectSSE() {
            if (eventSource) {
                eventSource.close();
            }
            
            const messagesDiv = document.getElementById('sse-messages');
            messagesDiv.innerHTML = 'Connecting to SSE stream...\n';
            
            eventSource = new EventSource('/sse');
            const statusBadge = document.getElementById('sse-status');
            
            eventSource.onopen = function(event) {
                statusBadge.className = 'badge success';
                statusBadge.textContent = 'Connected';
                messagesDiv.innerHTML += 'Connected to SSE stream!\n';
            };
            
            eventSource.onmessage = function(event) {
                const timestamp = new Date().toLocaleTimeString();
                messagesDiv.innerHTML += `[${timestamp}] ${event.data}\n`;
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            };
            
            eventSource.onerror = function(event) {
                statusBadge.className = 'badge warning';
                statusBadge.textContent = 'Error';
                messagesDiv.innerHTML += 'SSE connection error!\n';
            };
        }

        function disconnectSSE() {
            if (eventSource) {
                eventSource.close();
                eventSource = null;
                const statusBadge = document.getElementById('sse-status');
                statusBadge.className = 'badge warning';
                statusBadge.textContent = 'Disconnected';
                document.getElementById('sse-messages').innerHTML += 'Disconnected from SSE stream.\n';
            }
        }

        async function testSSEPost() {
            const messagesDiv = document.getElementById('sse-messages');
            messagesDiv.innerHTML += 'Testing POST to /sse...\n';
            
            try {
                const response = await fetch('/sse', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: 'Test memory from SSE POST endpoint',
                        timestamp: new Date().toISOString()
                    })
                });
                
                const data = await response.json();
                messagesDiv.innerHTML += `POST Response: ${JSON.stringify(data)}\n`;
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            } catch (error) {
                messagesDiv.innerHTML += `POST Error: ${error}\n`;
            }
        }

        async function testMemory() {
            const result = document.getElementById('result');
            result.innerHTML = '<p>Testing memory system...</p>';
            
            try {
                const response = await fetch('/api/test-memory');
                const data = await response.json();
                result.innerHTML = `
                    <div class="status">
                        <h3>✅ Memory Test Results</h3>
                        <pre class="code">${JSON.stringify(data, null, 2)}</pre>
                    </div>
                `;
            } catch (error) {
                result.innerHTML = `<p style="color: red;">Error: ${error}</p>`;
            }
        }

        async function viewStats() {
            const result = document.getElementById('result');
            result.innerHTML = '<p>Loading statistics...</p>';
            
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                result.innerHTML = `
                    <div class="status">
                        <h3>📊 System Statistics</h3>
                        <div class="status-item">
                            <span>Total Memories</span>
                            <span class="badge info">${data.memory_count || 0}</span>
                        </div>
                        <div class="status-item">
                            <span>Recent Activity</span>
                            <span class="badge success">${data.recent_activity || 'Active'}</span>
                        </div>
                    </div>
                `;
            } catch (error) {
                result.innerHTML = `<p style="color: red;">Error: ${error}</p>`;
            }
        }
    </script>
</body>
</html>
"""

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "service": "CombinedMemory Voice Agent", "sse_enabled": True}

# ========== NEW SSE ENDPOINTS ==========

async def event_generator() -> AsyncGenerator[str, None]:
    """Generate SSE events from memory queue"""
    queue = asyncio.Queue()
    active_connections.append(queue)
    
    try:
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connection', 'message': 'Connected to CombinedMemory SSE', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        while True:
            # Wait for new memory events
            memory_event = await queue.get()
            yield f"data: {json.dumps(memory_event)}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        if queue in active_connections:
            active_connections.remove(queue)

@app.get("/sse")
async def sse_stream(request: Request):
    """SSE endpoint for streaming memory updates"""
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
        }
    )

@app.post("/sse")
async def sse_post_memory(request: Request):
    """POST endpoint to push memories through SSE stream"""
    data = await request.json()
    message = data.get("message")
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Generate memory ID
    memory_id = str(uuid.uuid4())
    
    # Create memory event
    memory_event = {
        "id": memory_id,
        "type": "memory",
        "message": message,
        "user_id": USER_ID,
        "agent_id": AGENT_ID,
        "timestamp": datetime.now().isoformat(),
        "metadata": data.get("metadata", {})
    }
    
    # Add to mem0 if configured
    if mem0_client:
        try:
            # Add metadata for mem0
            now = datetime.now()
            metadata = {
                "category": "sse_stream",
                "day": now.strftime("%Y-%m-%d"),
                "month": now.strftime("%Y-%m"),
                "year": now.strftime("%Y"),
                "client": CLIENT,
                "project_type": PROJECT_TYPE,
                "device": DEVICE,
                "timestamp": now.isoformat(),
                "sse_memory_id": memory_id
            }
            
            # Store in mem0
            mem0_result = mem0_client.add(
                messages=[{"role": "user", "content": message}],
                user_id=USER_ID,
                metadata=metadata
            )
            
            memory_event["mem0_result"] = mem0_result
            memory_event["stored"] = True
        except Exception as e:
            memory_event["error"] = str(e)
            memory_event["stored"] = False
    else:
        memory_event["stored"] = False
        memory_event["error"] = "Mem0 client not configured"
    
    # Broadcast to all SSE connections
    await broadcast_memory(memory_event)
    
    return {
        "success": True,
        "memory_id": memory_id,
        "message": "Memory pushed to SSE stream",
        "stored_in_mem0": memory_event.get("stored", False),
        "active_connections": len(active_connections),
        "timestamp": memory_event["timestamp"]
    }

# ========== EXISTING ENDPOINTS ==========

@app.post("/api/memory/add")
async def add_memory(request: Request):
    """Add a memory via API (now also broadcasts to SSE)"""
    data = await request.json()
    message = data.get("message")
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    if not mem0_client:
        raise HTTPException(status_code=500, detail="Memory system not configured")
    
    # Generate metadata
    now = datetime.now()
    metadata = {
        "category": "api_added",
        "day": now.strftime("%Y-%m-%d"),
        "month": now.strftime("%Y-%m"),
        "year": now.strftime("%Y"),
        "client": CLIENT,
        "project_type": PROJECT_TYPE,
        "device": DEVICE,
        "timestamp": now.isoformat()
    }
    
    try:
        result = mem0_client.add(
            messages=[{"role": "user", "content": message}],
            user_id=USER_ID,
            metadata=metadata
        )
        
        # Broadcast to SSE
        memory_event = {
            "type": "memory_added",
            "message": message,
            "user_id": USER_ID,
            "result": result,
            "timestamp": now.isoformat()
        }
        await broadcast_memory(memory_event)
        
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory/search")
async def search_memory(request: Request):
    """Search memories via API"""
    data = await request.json()
    query = data.get("query")
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    if not mem0_client:
        raise HTTPException(status_code=500, detail="Memory system not configured")
    
    try:
        results = mem0_client.search(
            query=query,
            user_id=USER_ID,
            limit=5
        )
        
        # Broadcast search event to SSE
        search_event = {
            "type": "memory_search",
            "query": query,
            "results_count": len(results),
            "timestamp": datetime.now().isoformat()
        }
        await broadcast_memory(search_event)
        
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-memory")
async def test_memory():
    """Test memory system functionality"""
    if not mem0_client:
        return {"error": "Memory system not configured"}
    
    try:
        # Add a test memory
        test_message = f"Test from CombinedMemory web interface at {datetime.now()}"
        add_result = mem0_client.add(
            messages=[{"role": "user", "content": test_message}],
            user_id=USER_ID
        )
        
        # Search for recent memories
        search_results = mem0_client.search(
            query="CombinedMemory",
            user_id=USER_ID,
            limit=3
        )
        
        # Broadcast test event
        test_event = {
            "type": "test_completed",
            "message": test_message,
            "timestamp": datetime.now().isoformat()
        }
        await broadcast_memory(test_event)
        
        return {
            "test_status": "success",
            "memory_added": add_result,
            "recent_memories": search_results
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    if not mem0_client:
        return {"error": "Memory system not configured"}
    
    try:
        # Get recent memories count
        results = mem0_client.search(
            query="conversation",
            user_id=USER_ID,
            limit=10
        )
        
        return {
            "memory_count": len(results),
            "recent_activity": "Active" if results else "No recent activity",
            "user_id": USER_ID,
            "client": CLIENT,
            "agent_id": AGENT_ID,
            "sse_connections": len(active_connections)
        }
    except Exception as e:
        return {"error": str(e)}

# Webhook endpoint for ElevenLabs tools
@app.post("/webhook/elevenlabs/tools/{tool_name}")
async def handle_tool_call(tool_name: str, request: Request):
    """Handle tool calls from ElevenLabs agent"""
    data = await request.json()
    
    if not mem0_client:
        return {"error": "Memory system not configured"}
    
    try:
        if tool_name == "addMemories":
            message = data.get("parameters", {}).get("message")
            if message:
                result = mem0_client.add(
                    messages=[{"role": "user", "content": message}],
                    user_id=USER_ID
                )
                
                # Broadcast to SSE
                webhook_event = {
                    "type": "elevenlabs_memory",
                    "tool": "addMemories",
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                }
                await broadcast_memory(webhook_event)
                
                return {"success": True, "message": "Memory added successfully"}
        
        elif tool_name == "retrieveMemories":
            query = data.get("parameters", {}).get("message")
            if query:
                results = mem0_client.search(
                    query=query,
                    user_id=USER_ID,
                    limit=5
                )
                if results:
                    memories = "\n".join([f"- {r['memory']}" for r in results])
                    return {"success": True, "message": memories}
                return {"success": True, "message": "No relevant memories found"}
        
        elif tool_name == "getSessionSummary":
            results = mem0_client.search(
                query="recent topics",
                user_id=USER_ID,
                limit=3
            )
            if results:
                summary = "Recent: " + ", ".join([r["memory"][:30] for r in results])
                return {"success": True, "message": summary}
            return {"success": True, "message": "This is our first conversation"}
    
    except Exception as e:
        return {"error": str(e)}
    
    return {"error": f"Unknown tool: {tool_name}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting CombinedMemory Voice Agent on port {port}")
    print(f"📝 User ID: {USER_ID}")
    print(f"🤖 Agent ID: {AGENT_ID}")
    print(f"🧠 Memory Backend: {'Connected' if mem0_client else 'Not configured'}")
    print(f"📡 SSE Endpoint: Enabled at /sse")
    
    uvicorn.run(app, host="0.0.0.0", port=port)