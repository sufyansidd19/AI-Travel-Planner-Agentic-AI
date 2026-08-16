import asyncio
import json

from typing import Any

from click import prompt
from langchain_core.messages import AIMessage , HumanMessage,SystemMessage
from langgraph.types import interrupt


from config import get_llm
from mcp_client import current_weather , forecast , list_airlines , list_airports, tavily_search
from state import TravelState 


llm = get_llm()


def _llm_text(system:str , prompt:str)-> str:
    response=llm.invoke([SystemMessage(content=system),
                         HumanMessage(content=prompt)
                ])
    return response.content


def _json_from_llm(text:str)->dict:
    print("\n======== RAW LLM RESPONSE ====\n")
    print(text)
    print("================================\n")
    
    start=text.index("{")
    end=text.rindex("}")+1
    
    json_text=text[start:end]
    
    print("\n========EXTRACTED JSON==========")
    print(json_text)
    print("================================\n")
    
    return json.loads(json_text)

# With Guardrial
def supervisor_agent(state:TravelState):
    query=state["user_query"]
    
    guardrial_prompt=f"""
    Determine whether the following request is a valid travel planning request.
    
    Return only JSON in this format
    
    {{
        "allowed":true,
        "reason":""
    }}
    
    User request:
    {query}
    """
    guadrial_raw=_llm_text(
        "You are an input validation guardrail. Return strict JSON only.",
        guardrial_prompt,
    )

    print("\n=========GUADRAIL RAW RESPONSE=======")
    print(guadrial_raw)
    print("=====================================\n")
    
    guadrial_result=_json_from_llm(guadrial_raw)
    
    print("\n======Guadrail parsed response ==========")
    print(json.dumps(guadrial_result,indent=2))
    print("=========================================\n")
    
    if not guadrial_result.get("allowed",False):
        reason=guadrial_result.get(
            "reason",
            "Request rejected by input guadrail"
        )
        return{
            "selected_agents":[],
            "trip_constraints":{},
            "supervisor_reasoning":reason,
            "final_response":reason,
            "messages":[
                AIMessage(content=f"Guadrail blocked request: {reason}")
            ],
            "llm_calls":state.get("llm_calls",0)+1,
        }

    planning_prompt=f"""
    You are the supervisor of a real-world multi-agent travel planning system.

    Decide which specialist agents are needed for this user request.

    Available agents:
    - flight_agent: use when flights, airports, airlines, routes, or airfare guidance are needed
    - hotel_agent: use when hotels, stays, neighborhoods, or accommodation are needed
    - weather_agent: use when weather, climate, season, packing, or forecast is useful
    - budget_agent: use when budget, affordability, cost, or price constraints are mentioned
    - itinerary_agent: almost always needed to produce the travel plan

    Return only JSON with this schema:
    {{
      "selected_agents": ["flight_agent", "hotel_agent", "weather_agent", "budget_agent", "itinerary_agent"],
      "trip_constraints": {{
        "destination": "",
        "origin": "",
        "duration": "",
        "budget": "",
        "travel_style": "",
        "special_preferences": []
      }},
      "reasoning": ""
    }}

    User request:
    {query}
    """

    raw=_llm_text("You route work to specialist agents.", planning_prompt)
    parsed=_json_from_llm(raw)

    print("\n======== SUPERVISOR PARSED JSON ========\n")
    print(json.dumps(parsed, indent=2))
    print("========================================\n")

    selected=parsed["selected_agents"]
    if "itinerary_agent" not in selected:
        selected.append("itinerary_agent")

    return{
        "selected_agents": selected,
        "trip_constraints": parsed.get("trip_constraints",{}),
        "supervisor_reasoning": parsed.get("reasoning",""),
        "messages":[AIMessage(content="Supervisor created the agent plan")],
        "llm_calls":state.get("llm_calls",0)+1,
    }



# without guadrial

# def supervisor_agent(state:TravelState):
#     query=state["user_query"]
#     prompt = f"""
# You are the supervisor of a real-world multi-agent travel planning system.

# Decide which specialist agents are needed for this user request.

# Available agents:
# - flight_agent: use when flights, airports, airlines, routes, or airfare guidance are needed
# - hotel_agent: use when hotels, stays, neighborhoods, or accommodation are needed
# - weather_agent: use when weather, climate, season, packing, or forecast is useful
# - budget_agent: use when budget, affordability, cost, or price constraints are mentioned
# - itinerary_agent: almost always needed to produce the travel plan

# Return only JSON with this schema:
# {{
#   "selected_agents": ["flight_agent", "hotel_agent", "weather_agent", "budget_agent", "itinerary_agent"],
#   "trip_constraints": {{
#     "destination": "",
#     "origin": "",
#     "duration": "",
#     "budget": "",
#     "travel_style": "",
#     "special_preferences": []
#   }},
#   "reasoning": ""
# }}

# User request:
# {query}
# """
    
    
#     raw=_llm_text("You route work to specialist agents.", prompt,)
#     print("\n======== RAW LLM RESPONSE ====\n")
#     print(raw)
#     print("================================\n")
    
#     parsed=_json_from_llm(raw)
#     print("\n======== PARSED JSON ====\n")
#     print(json.dumps(parsed,indent=2))
#     print("===========================\n")
    
    
#     print(type(raw))
#     print(type(parsed))
    
#     selected=parsed["selected_agents"]
    
#     return{
#         "selected_agents": selected,
#         "trip_constraints": parsed["trip_constraints"],
#         "supervisor_reasoning": parsed["reasoning"],
#         "messages":[AIMessage(content="Supervisor created the agent plan")],
#         "llm_calls":state.get("llm_calls",0)+1
#     } 
    
    
def flight_agent(state:TravelState):
    query=state["user_query"]
    constraints=state["trip_constraints"]
    destination=constraints["destination"]
    
    print("\n======== FLIGHT AGENT INPUT========\n")
    print("Query: ", query)
    print("Constraints:",constraints)
    print("================================\n")
    
    airports=asyncio.run(list_airports(destination,limit=10))
    airlines=asyncio.run(list_airlines("",limit=10))
    
    print("\n======== AIRPORT MCP DATA ========\n")
    print(airports)
    print("================================\n")
    
    print("\n======== AIRLINE MCP DATA ========\n")
    print(airlines)
    print("================================\n")
    
    prompt=f"""
    Create flight guidance for this trip 
    User request: {query}
    Trip constraints: {constraints}
    Aiport MCP data: {str(airports)[:3000]}
    Airline MCP data: {str(airlines)[:3000]}
    
    Include likely departure / arrival airports , relevant airlines ,
    estimated duration , fare range , peak season warning ,
    and booking advice. """
    
    result=_llm_text("You are a flight planning specialist.",
                     prompt)
    
    print("\n======== FLIGHT AGENT OUTPUT ========\n")
    print(result)
    print("================================\n")
    
    return{
        "flight_results": result,
        "messages":[AIMessage(content="Flight agent completed work")],
        "llm_calls":state.get("llm_calls",0)+1
    }
    
    
def hotel_agent(state:TravelState):
    query=f"Best hotels and areas to stay for : {state['user_query']}"
    print("\n======== HOTEL AGENT INPUT ========\n")
    print("Query: ", query)
    print("================================\n")
    
    raw_search=asyncio.run(tavily_search(query))
    
    print("\n======== HOTEL AGENT RAW SEARCH ========\n")
    print(raw_search)
    print("================================\n")
    
    prompt=f"""
    The following are raw web-search results about hotels and the best areas to stay
    for this traveller's trip:

    User request: {state['user_query']}

    Raw search results:
    {str(raw_search)[:6000]}

    Write a clean, friendly summary for the traveller covering:
    1. The best areas / neighborhoods to stay in
    2. A few standout hotel options with rough price levels
    3. Practical booking tips

    Write it as plain, well-structured prose with short sections.
    Do NOT include URLs, links, search metadata, or raw search data.
    """
    result=_llm_text("You are a hotel and accommodation specialist who writes for travellers.",
                     prompt)
    
    print("\n======== HOTEL AGENT OUTPUT ========\n")
    print(result)
    print("================================\n")
    
    return{
        "hotel_results": result,
        "messages":[AIMessage(content="Hotel agent completed work")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
    
    
def weather_agent(state:TravelState):
    constraints=state["trip_constraints"]
    city=constraints["destination"] 
    
    print("\n======== WEATHER AGENT INPUT ========\n")
    print("City: ", city)
    print("================================\n")
    
    weather_data=asyncio.run(current_weather(city))
    forecast_data=asyncio.run(forecast(city))
    
    print("\n======== CURRENT WEATHER ========\n")
    print(weather_data)
    print("================================\n")
    
    print("\n======== WEATHER FORECAST ========\n")
    print(forecast_data)
    print("================================\n")
    
    prompt=f"""
    The following is raw weather data for {city} during the traveller's planned trip.

    Current weather: {str(weather_data)[:3000]}
    Forecast: {str(forecast_data)[:3000]}

    Write a clean, friendly summary for the traveller covering:
    1. What the weather will realistically be like
    2. What to expect across the trip (temperature, rain, conditions)
    3. Simple packing and planning advice

    Write it as plain, well-structured prose with short sections.
    Do NOT include raw JSON, API data, or technical details.
    """
    result=_llm_text("You are a weather specialist who writes for travellers.", prompt)
    
    print("\n======== WEATHER AGENT OUTPUT ========\n")
    print(result)
    print("================================\n")
    
    return{
        "weather_results": result,
        "messages":[AIMessage(content="Weather agent completed work")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
    
    
def budget_agent(state:TravelState):
    print("\n======== BUDGET AGENT INPUT ========\n")
    print("Trip Constraints:")
    print(state.get("trip_constraints"))
    print("\nFlight Results:")
    print(state.get("flight_results"))
    print("\nHotel Results:")
    print(state.get("hotel_results"))
    print("\nWeather Results:")
    print(state.get("weather_results"))
    print("================================\n")
    
    prompt=f"""
    Analyze whether this trip plan is realistic for the user's budget
    
    User request: {state['user_query']}
    
    Constraints: {state.get('trip_constraints',{})}
    
    Flight results: {state.get('flight_results','')}
    
    
    Return a concise budget assessment withL
    1. estimated cost categories 
    2. risk areas 
    3. money-saving suggestions
    4. whether the plan seems feasible
    """
    
    result=_llm_text("You are a practical travel budget analyst.",
                     prompt)
    
    print("\n======== BUDGET AGENT OUTPUT ========\n")
    print(result)
    print("================================\n")
    
    return{
        "budget_results": result,
        "messages":[AIMessage(content="Budget agent completed work")],
        "llm_calls":state.get("llm_calls",0)+1
    }
    

def itinerary_agent(state:TravelState):
    print("\n======== ITINERARY AGENT INPUT ========\n")
    print("Trip Constraints:")
    print(state.get("trip_constraints"))
    print("\nFlight Results:")
    print(state.get("flight_results"))
    print("\nHotel Results:")
    print(state.get("hotel_results"))
    print("\nWeather Results:")
    print(state.get("weather_results"))
    print("\nBudget Results:")
    print(state.get("budget_results"))
    print("================================\n")
    
    prompt=f"""
    Create a clear draft travel itinerary 
    
    User request: {state['user_query']}
    
    Constraints: {state.get('trip_constraints',{})}
    
    Flight results: {state.get('flight_results','')}
    
    Hotel results: {state.get('hotel_results','')}
    
    Weather results: {state.get('weather_results','')}
    
    Budget results: {state.get('budget_results','')}
    
    Make the output structured , practical , and ready for human review
    """
    result=_llm_text("You are an expert itinerary planner.",prompt,)
    print("\n======== ITINERARY AGENT OUTPUT ========\n")
    print(result)
    print("================================\n")
    
    approval_request=f"""
    please review this draft travel plan
    {result}
    Reply with approval or feedback
    """
    
    return {
        "itinerary": result,
        "approval_request": approval_request,
        "messages":[AIMessage(content="Draft Itinerary created for human review")],
        "llm_calls":state.get("llm_calls",0)+1
    }
    
    
    
def human_approval_agent(state:TravelState):
    feedback=interrupt(
        {
        "question":"Do you approve this itinerary?",
        "draft_itinerary": state.get('itinerary',''),
        "approval_request": state.get('approval_request',''),
        "expected_response":{
            "approved": True,
            "feedback": "Optional feedback for revision"
        },
    })
    
    approved=feedback["approved"]
    human_feedback=feedback["feedback"]

    return {
        "approved": approved,
        "human_feedback": human_feedback,
    }
    
def final_response_agent(state:TravelState):
    print("\n======== FINAL RESPONSE AGENT INPUT ========\n")
    print("Approved:", state.get("approved"))
    print("Human Feedback:", state.get("human_feedback"))
    print("\n========================================\n")
    
    if state["approved"]:
        prompt=f"""
        The humnan approved this draft iternary.
        
        Produce the final polished travel plan.
        
        Draft Itinerary: {state['itinerary']}
        
        Budget notes:{state['budget_results']}
        
        """
        
    else:
        prompt=f"""
        The human did not approve the draft 
        
        Original user request:
        {state['user_query']}
        
        Draft Itinerary: {state['itinerary']}
        
        Human feedback: {state['human_feedback']}
        
        Budget notes:{state['budget_results']}
        """
        
        
        result=_llm_text("You produce final user-ready travel plans.",prompt,)
        
        print("\n======== FINAL RESPONSE AGENT OUTPUT ========\n")
        print(result)
        print("================================\n")
        
    return{
        "final_response": result,
        "messages":[AIMessage(content=result)],
        "llm_calls": state.get("llm_calls", 0) + 1,
        }