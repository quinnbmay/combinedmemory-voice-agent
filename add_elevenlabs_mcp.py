#!/usr/bin/env python3
"""
Add MCP server (webhook) to ElevenLabs for mem0 integration
"""

import os
import requests
import json

# API configuration
API_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_f9bf84125ea4a0dcbbe4adcf9e655439a9c08ea8fef16ab6")
AGENT_ID = "74Vinci9jnFDyA4G6SUm"

def create_mcp_server():
    """Create MCP server for mem0 webhook"""
    
    url = "https://api.elevenlabs.io/v1/convai/mcp-servers"
    
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "config": {
            "url": "https://mcp.combinedmemory.com/elevenlabs/webhook",
            "name": "mem0",
            "description": "Store conversation memories in Mem0 for long-term recall",
            "transport": "SSE",
            "approval_policy": "auto_approve_all"
        }
    }
    
    print("Creating MCP server for mem0...")
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ MCP server created successfully!")
        print(f"Server ID: {result.get('id')}")
        print(f"Name: {result['config']['name']}")
        print(f"URL: {result['config']['url']}")
        return result
    else:
        print(f"❌ Error creating MCP server: {response.status_code}")
        print(response.text)
        return None

def list_mcp_servers():
    """List existing MCP servers"""
    
    url = "https://api.elevenlabs.io/v1/convai/mcp-servers"
    
    headers = {
        "xi-api-key": API_KEY
    }
    
    print("\nListing MCP servers...")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # Handle both list and dict responses
        if isinstance(data, dict):
            servers = data.get('servers', data.get('items', [data]))
        else:
            servers = data if isinstance(data, list) else []
            
        if servers:
            for server in servers:
                if isinstance(server, dict) and 'config' in server:
                    print(f"- {server['config']['name']}: {server['config']['url']}")
                elif isinstance(server, dict):
                    print(f"- Server: {json.dumps(server, indent=2)}")
        else:
            print("No MCP servers found")
        return servers
    else:
        print(f"Error listing MCP servers: {response.status_code}")
        return []

def attach_to_agent(mcp_server_id):
    """Attach MCP server to agent"""
    
    # Update agent to use the MCP server
    url = f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}"
    
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Get current agent config first
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        agent = response.json()
        
        # Add MCP server to agent
        if 'mcp_servers' not in agent:
            agent['mcp_servers'] = []
        
        if mcp_server_id not in agent['mcp_servers']:
            agent['mcp_servers'].append(mcp_server_id)
            
            # Update agent
            update_response = requests.patch(url, headers=headers, json={
                "mcp_servers": agent['mcp_servers']
            })
            
            if update_response.status_code == 200:
                print(f"✅ MCP server attached to agent {AGENT_ID}")
                return True
            else:
                print(f"Error updating agent: {update_response.status_code}")
                print(update_response.text)
        else:
            print("MCP server already attached to agent")
            return True
    else:
        print(f"Error getting agent: {response.status_code}")
        
    return False

if __name__ == "__main__":
    # List existing servers
    response = requests.get("https://api.elevenlabs.io/v1/convai/mcp-servers", 
                           headers={"xi-api-key": API_KEY})
    
    server_id = None
    
    if response.status_code == 200:
        data = response.json()
        
        # Find the mem0 server
        if 'mcp_servers' in data:
            for server in data['mcp_servers']:
                if 'mcp.combinedmemory.com' in server['config'].get('url', ''):
                    print(f"✅ Found existing mem0 server with ID: {server['id']}")
                    server_id = server['id']
                    break
        
        if not server_id:
            # Create new MCP server
            result = create_mcp_server()
            if result:
                server_id = result['id']
    
    if server_id:
        # The MCP server is ready!
        print(f"\n✅ MCP Server ID: {server_id}")
        print(f"✅ Webhook URL: https://mcp.combinedmemory.com/elevenlabs/webhook")
        print(f"\nYour ElevenLabs agent can now use this MCP server!")
        print("\nTo attach to agent {AGENT_ID}:")
        print(f"1. Go to your agent settings in ElevenLabs dashboard")
        print(f"2. Add the MCP server with ID: {server_id}")
        print(f"3. Or the webhook is already configured and ready to receive memories!")