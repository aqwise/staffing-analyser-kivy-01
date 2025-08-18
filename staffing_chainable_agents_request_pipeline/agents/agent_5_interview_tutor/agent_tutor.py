from google.adk import Agent

from staffing_chainable_agents_request_pipeline.agents.agent_5_interview_tutor.prompts_tutor import \
    interview_tutor_prompt


class ParametrizedInterviewTutorAgent(Agent):
    def __init__(self, business_domain=None, **kwargs):
        instruction = interview_tutor_prompt(business_domain)
        super().__init__(instruction=instruction, **kwargs)
        self._business_domain = business_domain
