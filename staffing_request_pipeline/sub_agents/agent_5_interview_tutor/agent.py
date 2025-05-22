from google.adk.agents import Agent, LoopAgent
from .prompts import interview_tutor_prompt
from google.adk.tools import google_search 


root_agent = Agent(
    name="interview_tutor_agent",
    model="gemini-2.5-pro-preview-05-06",
    description="Агент для подготовки к собеседованию на позицию QA/AQA.",
    instruction=interview_tutor_prompt(),
    tools=[google_search],
    output_key="interview_tutor_agent_output",
)

# root_agent = LoopAgent(
#     name="osint_researcher_looping_agent",
#     max_iterations=3,
#     sub_agents=[interview_tutor_agent],
#     description="Агент для подготовки к собеседованию на позицию QA/AQA в цикле.",
#     )
