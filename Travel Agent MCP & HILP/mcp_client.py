import os
import asyncio

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_STACK_API_KEY=os.getenv("AVIATION_STACK_API_KEY")
OPENWEATHER_API_KEY=os.getenv("OPENWEATHER_API_KEY")

client=MultiServerMCPClient(
    # Remote MCP servers configuration
    {
        "tavily":{
        "transport":"streamable_http",
        "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        },
        # Local MCP servers configuration
        "aviationstack":{
            "transport": "stdio",
            "command": r"D:\AI_Travel_Agent\AI_Travel_with_MCP\aviationstack-mcp\.venv\Scripts\python.exe",
            "args":[
                    "-m",
                    "aviationstack_mcp",
                    "mcp",
                    "run"
                ],
            "env":{
                "AVIATION_STACK_API_KEY": AVIATION_STACK_API_KEY
                }
        },
        # Custom weather MCP server configuration
        "weather":{
            "transport": "stdio",
            "command": r"D:\AI_Travel_Agent\venv\Scripts\python.exe",
            "args":[
                r"D:\AI_Travel_Agent\AI_Travel_with_MCP\custom_weather_mcp_server.py"
            ],
            "env": {
                "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY
            }
        }
    }
)
        
        
        
_tools_cache=None

async def get_tools():
    global _tools_cache
    if _tools_cache is None:
        try:
            _tools_cache=await client.get_tools()
            
        except Exception as e:
            print("\n=======Full Error=======")
            print(type(e))
            print(repr(e))
            
            if hasattr(e,"exceptions"):
                print("\nSUB EXCEPTIONS:")
                for i , sub in enumerate(e.exceptions):
                    print(f"\n--- Sub Exception {i+1} ---")
                    print(type(sub))
                    print(repr(sub))
                    
            raise
    return _tools_cache

async def call_tool(tool_name:str,args:dict=None):
    tools=await get_tools()
    
    tool=next(
        (tool for tool in tools if tool.name==tool_name),
        None,
    )
    if tool is None:
        raise ValueError(f"Tool '{tool_name}' not found")
    
    return await tool.ainvoke(args or {})



# ----------------
# Tavily MCP Tools 
#-----------------

async def tavily_search(query:str):
    return await call_tool("tavily_search" , {"query":query})

async def list_airports(search:str="",limit:int=10):
    return await call_tool("list_airports",{"search":search,"limit":limit,"offset":0})

async def list_airlines(search:str="",limit:int=10):
    return await call_tool("list_airlines",{"search":search,"limit":limit,"offset":0})

async def current_weather(city:str):
    return await call_tool("get_current_weather",{"city":city})

async def forecast(city:str):
    return await call_tool("get_forecast",{"city":city})




# search_tool = None
# aviation_tools={}
# async def initialize_mcp():
#     global search_tool
#     global aviation_tools
#     if search_tool is not None and aviation_tools:
#         return
    
#     tools= await client.get_tools()
    
#     print("Available MCP tools:\n")
    
#     for tool in tools:
#         print(tool.name)
#     search_tool = next(
#         tool for tool in tools if tool.name == "tavily_search"
#         )        
#     aviation_tools = {tool.name: tool for tool in tools 
#                       if tool.name!="tavily_search"
#                       }
        
# async def main():
#     tools = await client.get_tools()
#     search_tool = next(tool for tool in tools if tool.name == "tavily_search"
#     )
#     result = await search_tool.ainvoke(
#         {"query": "What is the capital of France?"}
#         )
#     print(f"Search result: {result}")


# async def tavily_mcp_search(query: str):
#     await initialize_mcp()
#     result = await search_tool.ainvoke(
#         {"query": query}
#     )
#     return result

# async def aviation_mcp_call(
#     tool_name: str,
#     tool_args: dict=None
#     ):
#     tools = await client.get_tools()
#     tool=next((t for t in tools if t.name==tool_name))
#     result = await tool.ainvoke(tool_args or {})
#     return result

# async def get_airports():
#     await initialize_mcp()
#     tool=aviation_tools.get("list_airports")
    
#     if not tool:
#         return "Airports tool unavailable"
    
#     result=await tool.ainvoke({})
#     return result

# async def get_airlines():
#     await initialize_mcp()
#     tool=aviation_tools.get("list_airlines")
    
#     if not tool:
#         return "Airlines tool unavailable"
    
#     result=await tool.ainvoke({})
#     return result
    
    
# weather_tools=None
# forecast_tool=None

# async def initialize_weather_tools():
#     global weather_tools
#     global forecast_tool
#     if weather_tools is not None and forecast_tool is not None:
#         return
    
#     tools= await client.get_tools()
    
#     print("Available MCP tools:\n")
        
#     weather_tools = next(
#         tool for tool in tools if tool.name == "get_current_weather"
#         )
    
#     forecast_tool = next(
#         tool for tool in tools if tool.name == "get_forecast"
#         )

# async def weather_mcp_search(city: str):
    
#     await initialize_weather_tools()
    
#     result = await weather_tools.ainvoke(
#         {"city": city}
#     )

# async def forecast_mcp_search(city: str):
    
#     await initialize_weather_tools()
    
#     result = await forecast_tool.ainvoke(
#         {"city": city}
#     )

# from langchain_groq import ChatGroq

# llm=ChatGroq(
#     model="llama-3.3-70b-versatile")

# def extract_destination(query: str):
#     prompt=f"""
#     Extract the destination city from the following user query:
#     Query:{query}

#     Return only Destination name.
#     """
#     response=llm.invoke(prompt)
#     return response.content.strip()

 
# if __name__ == "__main__":
#     asyncio.run(main())