from google.adk.agents import Agent

from .prompts_customer import identify_companies


class CustomerIdentifierAgent(Agent):
    def __init__(self, **kwargs):
        instruction = identify_companies()
        super().__init__(instruction=instruction, **kwargs)