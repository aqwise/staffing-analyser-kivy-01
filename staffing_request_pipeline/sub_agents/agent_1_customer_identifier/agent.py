from google.adk.agents import Agent
from .prompts import identify_companies
from google.adk.tools import google_search 


root_agent = Agent(
    name="customer_identifier_agent",
    model="gemini-2.0-flash-exp",
    description="Агент для определения всех упомянутых компаний из стаффинг-запроса.",
    instruction=identify_companies(),
    tools=[google_search],
    output_key="customer_identifier_output",
)
