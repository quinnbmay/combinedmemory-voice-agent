#!/usr/bin/env python3
"""
Add webhook tool to ElevenLabs agent using SDK
"""

import os
from elevenlabs import ElevenLabs
import json

# Initialize ElevenLabs client
client = ElevenLabs(
    api_key=os.environ.get("ELEVENLABS_API_KEY", "sk_f9bf84125ea4a0dcbbe4adcf9e655439a9c08ea8fef16ab6")
)

# Agent ID
AGENT_ID = "74Vinci9jnFDyA4G6SUm"

def add_webhook_tool():
    """Add the webhook tool to the agent"""
    try:
        # Create the webhook tool
        print(f"Adding webhook tool to agent {AGENT_ID}...")
        
        tool = client.conversational_ai.tools.create(
            agent_id=AGENT_ID,
            name="mem0",
            type="webhook",
            description="Store important information from conversations in long-term memory. Use when user shares personal info, preferences, work context, or asks to remember something.",
            config={
                "server_url": "https://mcp.combinedmemory.com/elevenlabs/webhook",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json"
                },
                "parameters": {
                    "text": {
                        "type": "string", 
                        "description": "The message or information to remember from the conversation",
                        "required": True
                    },
                    "agent_id": {
                        "type": "string",
                        "default": AGENT_ID,
                        "required": False
                    }
                }
            }
        )
        
        print("✅ Webhook tool added successfully!")
        print(f"Tool ID: {tool.tool_id if hasattr(tool, 'tool_id') else 'Created'}")
        
        return tool
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTrying alternative format...")
        
        # Try the server tool format
        try:
            tool = client.conversational_ai.tools.create(
                agent_id=AGENT_ID,
                name="mem0",
                type="server_tool",
                description="Store memories from conversations",
                server_tool_config={
                    "url": "https://mcp.combinedmemory.com/elevenlabs/webhook",
                    "method": "POST",
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "text": "{text}",
                        "agent_id": AGENT_ID
                    }
                }
            )
            print("✅ Server tool added successfully!")
            return tool
            
        except Exception as e2:
            print(f"Alternative format also failed: {e2}")
            return None

def list_tools():
    """List existing tools for the agent"""
    try:
        print(f"\nListing tools for agent {AGENT_ID}...")
        tools = client.conversational_ai.tools.list(agent_id=AGENT_ID)
        
        if hasattr(tools, '__iter__'):
            for tool in tools:
                print(f"- {tool.name}: {tool.type}")
        else:
            print(f"Tools response: {tools}")
            
    except Exception as e:
        print(f"Error listing tools: {e}")

if __name__ == "__main__":
    # First list existing tools
    list_tools()
    
    # Add the webhook tool
    result = add_webhook_tool()
    
    if result:
        print("\n✅ Complete! Your ElevenLabs agent now has the mem0 webhook tool configured.")
        print("The agent will automatically send memories to https://mcp.combinedmemory.com/elevenlabs/webhook")
    
    # List tools again to confirm
    list_tools()