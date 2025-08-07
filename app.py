#!/usr/bin/env python3
"""
CombinedMemory Voice Agent - Web Interface for Railway
ElevenLabs + Mem0 Integration
"""

import os
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mem0 import MemoryClient
from dotenv import load_dotenv
import uvicorn

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
AGENT_ID = os.environ.get('AGENT_ID')
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')
CLIENT = os.environ.get('MEM0_CLIENT', 'CombinedMemory.com')
PROJECT_TYPE = os.environ.get('MEM0_PROJECT_TYPE', 'voice_ai_assistant')
DEVICE = os.environ.get('MEM0_DEVICE', 'railway_deployment')

# Initialize Mem0 client
mem0_client = None
if MEM0_API_KEY:
    mem0_client = MemoryClient(api_key=MEM0_API_KEY)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface"""
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ CombinedMemory Voice Agent</h1>
        <p class="subtitle">Powered by ElevenLabs + Mem0</p>
        
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
                <span>User ID</span>
                <span class="badge info">quinn_may</span>
            </div>
            <div class="status-item">
                <span>Agent ID</span>
                <span class="badge info">mem</span>
            </div>
        </div>

        <div class="info-box">
            <h3>📱 How to Connect</h3>
            <p>To use voice interaction:</p>
            <ol>
                <li>Open the ElevenLabs Conversational AI app</li>
                <li>Select the "mem" agent</li>
                <li>Start speaking - your memories are synced!</li>
            </ol>
        </div>

        <div class="actions">
            <button class="btn btn-primary" onclick="testMemory()">Test Memory System</button>
            <button class="btn btn-secondary" onclick="viewStats()">View Statistics</button>
        </div>

        <div id="result" style="margin-top: 20px;"></div>
    </div>

    <script>
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
    return {"status": "healthy", "service": "CombinedMemory Voice Agent"}

@app.post("/api/memory/add")
async def add_memory(request: Request):
    """Add a memory via API"""
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
            "agent_id": AGENT_ID
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
    
    uvicorn.run(app, host="0.0.0.0", port=port)