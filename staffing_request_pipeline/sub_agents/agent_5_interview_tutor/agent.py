from google.adk.agents import Agent
from .prompts import interview_tutor_prompt
from google.adk.tools import google_search 


root_agent = Agent(
    name="interview_tutor_agent",
    model="gemini-2.0-flash-exp",
    description="Агент для подготовки к собеседованию на позицию QA/AQA.",
    instruction=interview_tutor_prompt(),
    tools=[google_search],
    output_key="interview_tutor_agent_output",
)
