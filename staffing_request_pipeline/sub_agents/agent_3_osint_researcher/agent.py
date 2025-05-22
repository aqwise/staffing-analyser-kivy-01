from google.adk.agents import Agent, LoopAgent
from .prompts import osint_researcher_prompt
from google.adk.tools import google_search 



osint_agent = Agent(
    name="osint_researcher_agent",
    model="gemini-2.5-pro-preview-05-06",
    description="Агент для проведения OSINT-исследования всех упомянутых компаний с использованием Google Search.",
    instruction=osint_researcher_prompt(),
    tools=[google_search],
    output_key="osint_researcher_agent_output",
)


root_agent = LoopAgent(
    name="osint_researcher_looping_agent",
    max_iterations=6,
    sub_agents=[osint_agent],
    description="Агент для проведения OSINT-исследования всех упомянутых компаний с использованием Google Search в цикле.",
    )
