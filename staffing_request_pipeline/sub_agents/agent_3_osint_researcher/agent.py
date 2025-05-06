from google.adk.agents import Agent
from .prompts import osint_researcher_prompt
from google.adk.tools import google_search 


root_agent = Agent(
    name="osint_researcher_agent",
    model="gemini-2.0-flash-exp",
    description="Агент для проведения OSINT-исследования всех упомянутых компаний с использованием Google Search.",
    instruction=osint_researcher_prompt(),
    tools=[google_search],
    output_key="osint_researcher_agent_output",
)
