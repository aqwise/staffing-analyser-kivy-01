from google.adk.agents import SequentialAgent
from google.adk.tools import google_search

from staffing_chainable_agents_request_pipeline.agents.agent_1_customer_identifier.agent_customer_identifier import \
    CustomerIdentifierAgent
from staffing_chainable_agents_request_pipeline.agents.agent_2_request_parser.agent_request_parser import \
    RequestParserAgent
from staffing_chainable_agents_request_pipeline.agents.agent_3_osint_researcher.agent_osint_researcher import \
    ParametrizedOSINTAgent
from staffing_chainable_agents_request_pipeline.agents.agent_4_attractiveness_profiler.agent_profiler import \
    ParametrizedAttractivenessProfilerAgent
from staffing_chainable_agents_request_pipeline.agents.agent_5_interview_tutor.agent_tutor import \
    ParametrizedInterviewTutorAgent
from staffing_chainable_agents_request_pipeline.agents.agent_6_report_finalizer.agent_finalizer import \
    ParametrizedReportFinalizerAgent

from staffing_chainable_agents_request_pipeline.utils import validate_business_domain


def create_parametrized_pipeline(business_domain: str):
    business_domain = validate_business_domain(business_domain)

    agent_1_customer_identifier = CustomerIdentifierAgent(
        name="customer_identifier_agent",
        model="gemini-2.0-flash-exp",
        tools=[google_search],
        output_key="customer_identifier_output"
    )

    agent_2_request_parser = RequestParserAgent(
        name="request_parser_agent",
        model="gemini-2.0-flash-exp",
        tools=[google_search],
        output_key="request_parser_agent_output"
    )

    agent_3_osint = ParametrizedOSINTAgent(
        name="osint_researcher_agent",
        business_domain=business_domain,
        model="gemini-2.0-flash-exp",
        tools=[google_search],
        output_key="osint_researcher_agent_output"
    )

    agent_4_profiler = ParametrizedAttractivenessProfilerAgent(
        name="attractiveness_profiler_agent",
        business_domain=business_domain,
        model="gemini-2.0-flash-exp",
        tools=[google_search],
        output_key="attractiveness_profiler_output"
    )

    agent_5_tutor = ParametrizedInterviewTutorAgent(
        name="interview_tutor_agent",
        business_domain=business_domain,
        model="gemini-2.0-flash-exp",
        tools=[google_search],
        output_key="interview_tutor_agent_output"
    )

    agent_6_finalizer = ParametrizedReportFinalizerAgent(
        name="report_finalizer_agent",
        business_domain=business_domain,
        model="gemini-2.0-flash-exp",
        tools=[],
        output_key=None
    )

    return SequentialAgent(
        name="staffing_request_pipeline",
        sub_agents=[
            agent_1_customer_identifier,
            agent_2_request_parser,
            agent_3_osint,
            agent_4_profiler,
            agent_5_tutor,
            agent_6_finalizer
        ]
    )
