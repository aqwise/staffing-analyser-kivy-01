from google.adk.agents import Agent

from .prompts_parser import request_parsing_prompt


class RequestParserAgent(Agent):
    def __init__(self, **kwargs):
        instruction = request_parsing_prompt()
        super().__init__(instruction=instruction, **kwargs)
