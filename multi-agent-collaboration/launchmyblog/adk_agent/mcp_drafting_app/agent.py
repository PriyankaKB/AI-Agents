import os
import dotenv
from mcp_drafting_app import tools
from google.adk.agents import LlmAgent
from google.adk import Agent
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from a2a.types import Message, AgentCard
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

dotenv.load_dotenv()

PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'project_not_set')

app = FastAPI()

DRAFTING_URL = os.getenv("DRAFTING_AGENT_URL", "http://localhost:8000/check")
PLAGIARISM_URL = os.getenv("PLAGIARISM_AGENT_URL", "http://localhost:8001/check")

drafting_card = AgentCard(
    name="drafting_agent",
    description="Checks drafts or crate new drafts for new content.",
    defaultInputModes=["text/plain"],
    defaultOutputModes=["application/json"],
    skills=[
        {
            "id": "drafting_agent",
            "name": "drafting_agent",
            "description": "Checks drafts or crate new drafts for new content.",
            "tags": ["drafting"]
        }
    ],
    url=DRAFTING_URL,   # use env var for Cloud Run URL
    capabilities={},      # can be empty if no special capabilities
    version="1.0.0"
)

plagiarism_card = AgentCard(
    name="plagiarism_agent",
    description="Checks drafts for plagiarism.",
    defaultInputModes=["text/plain"],
    defaultOutputModes=["application/json"],
    skills=[
        {
            "id": "plagiarism_agent",
            "name": "plagiarism_agent",
            "description": "Checks drafts for plagiarism.",
            "tags": ["plagiarism"]
        }
    ],
    url=PLAGIARISM_URL,   # use env var for Cloud Run URL
    capabilities={},      # can be empty if no special capabilities
    version="1.0.0"
)

# Agents
plagiarism_agent = RemoteA2aAgent(
    name="plagiarism_agent",
    description="Agent that detect overlapping content and plagiarism.",
    agent_card=plagiarism_card
)

drafting_agent_api = Agent(agent_card=drafting_card)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process")
async def process(request: Request):
    data = await request.json()
    text = data.get("draft", "")
    structured = f"# Introduction\n{text}\n\n# References\n- Author: Human Researcher"
    response = {"structured_draft": structured}
    drafting_agent_api.send(Message("plagiarism_agent", response))
    return response

maps_toolset = tools.get_maps_mcp_toolset()
bigquery_toolset = tools.get_bigquery_mcp_toolset()

root_agent = LlmAgent(
    model='gemini-2.5-flash-lite',
    name='drafting_agent',
    description="Creates drafts for blog content.",
    instruction=f"""
                Help the user answer questions by strategically combining insights from two sources:
                
                1.  **BigQuery toolset:** Access mcp-drafting-data in the mcp_blog dataset. Do not use any other dataset.
                Run all query jobs from project id: {PROJECT_ID}. 

                2.  **Maps Toolset:** Use this for real-world location analysis, finding competition/places and calculating necessary travel routes.
                    Include a hyperlink to an interactive map in your response where appropriate.
            """,
    tools=[maps_toolset, bigquery_toolset],
    sub_agents=[drafting_agent_api]
)
