import os
import asyncio
import json
from contextlib import AsyncExitStack
from typing import Any

import httpx
from groq import Groq  # ספריה חדשה
from client import MCPClient
from dotenv import load_dotenv

load_dotenv()

class ChatHost:
    def __init__(self):
        # הגדרת השרתים
        self.mcp_clients: list[MCPClient] = [
            MCPClient("./weather_USA.py"),
            MCPClient("./weather_Israel.py")
        ]
        self.tool_clients: dict[str, tuple[MCPClient, str]] = {}
        self.clients_connected = False
        
        # הגדרות Groq + נטפרי
        transport = httpx.HTTPTransport(verify=False)
        self.client = Groq(
            api_key = os.getenv("GROQ_API_KEY"),
            http_client=httpx.Client(transport=transport)
        )

    async def connect_mcp_clients(self):
        if self.clients_connected: return
        for client in self.mcp_clients:
            if client.session is None:
                await client.connect_to_server()
        self.clients_connected = True

    async def get_available_tools(self) -> list[dict[str, Any]]:
        """אוסף כלים מכל השרתים וממיר אותם לפורמט Groq/OpenAI"""
        await self.connect_mcp_clients()
        self.tool_clients = {}
        groq_tools = []

        for client in self.mcp_clients:
            try:
                response = await client.session.list_tools()
                for tool in response.tools:
                    exposed_name = f"{client.client_name}__{tool.name}"
                    self.tool_clients[exposed_name] = (client, tool.name)
                    
                    # המרה לפורמט JSON Schema ש-Groq מכיר
                    groq_tools.append({
                        "type": "function",
                        "function": {
                            "name": exposed_name,
                            "description": f"[{client.client_name}] {tool.description}",
                            "parameters": tool.inputSchema,
                        }
                    })
            except Exception as e:
                print(f"Warning: Failed tools from {client.client_name}: {e}")

        return groq_tools

    async def process_query(self, query: str) -> str:
        """שולח שאילתה ל-Groq ומנהל קריאות לכלים (Tools)"""
        messages = [{"role": "user", "content": query}]
        tools = await self.get_available_tools()

        while True:
            # שליחת הבקשה ל-Groq
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile", # מודל מומלץ ל-Tools
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            messages.append(response_message)

            # אם המודל לא ביקש להשתמש בכלי - סיימנו
            if not response_message.tool_calls:
                return response_message.content

            # אם המודל ביקש להפעיל כלים (אחד או יותר)
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                print(f"\n[מפעיל כלי: {tool_name} עם ארגומנטים: {tool_args}]")
                
                # ביצוע הקריאה לשרת ה-MCP המתאים
                client, original_name = self.tool_clients[tool_name]
                result = await client.session.call_tool(original_name, tool_args)
                
                # החזרת התוצאה למודל
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": str(result.content),
                })

    async def chat_loop(self):
        print("\nMCP Host (Groq Version) Started!")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() in ['quit', 'exit']: break
                
                response = await self.process_query(query)
                print("\nAssistant: " + response)
            except Exception as e:
                print(f"\nError: {str(e)}")

async def main():
    host = ChatHost()
    try:
        await host.chat_loop()
    finally:
        for client in host.mcp_clients:
            await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())