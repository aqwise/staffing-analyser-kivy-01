import os
from google.genai import types
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from staffing_request_pipeline.agent import root_agent

# Initialize services
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()

def process(query: str, api_key: str) -> str:
    """
    Process the staffing request using the agent pipeline.
    
    Args:
        query (str): The input text to analyze
        api_key (str): The API key for authentication
        
    Returns:
        str: The analysis result
    """
    # Set up environment
    os.environ['GOOGLE_API_KEY'] = api_key
    
    # Create a session
    session = session_service.create_session(
        app_name="StaffingAnalyzer",
        user_id="user"
    )
    
    # Set up the runner
    runner = Runner(
        app_name="StaffingAnalyzer",
        agent=root_agent,
        artifact_service=artifact_service,
        session_service=session_service,
    )
    
    # Create content for the agent
    content = types.Content(
        role="user", 
        parts=[types.Part(text=query)]
    )
    
    try:
        # Run the agent pipeline
        events = list(runner.run(
            user_id="user",
            session_id=session.id,
            new_message=content
        ))
        
        # Get the final response from the last event
        if events:
            last_event = events[-1]
            final_response = "".join(
                [part.text for part in last_event.content.parts if part.text]
            )
            return final_response
        return "No response generated from the analysis."
        
    except Exception as e:
        return f"Error during analysis: {str(e)}"