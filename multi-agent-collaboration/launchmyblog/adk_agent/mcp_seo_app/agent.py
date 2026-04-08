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

SEO_URL = os.getenv("SEO_AGENT_URL", "http://localhost:8002/check")
PUBLISHING_URL = os.getenv("PUBLISHING_AGENT_URL", "http://localhost:8003/check")

seo_card = AgentCard(
    name="seo_agent",
    description="Agent that detects keywords and metadata for SEO.",
    defaultInputModes=["text/plain"],
    defaultOutputModes=["application/json"],
    skills=[
        {
            "id": "seo_agent",
            "name": "seo_agent",
            "description": "Agent that detects keywords and metadata for SEO.",
            "tags": ["seo"]
        }
    ],
    url=SEO_URL,          # set via env var, e.g. http://localhost:8002/check or Cloud Run URL
    capabilities={},      # can be empty if no special capabilities
    version="1.0.0"
)

publishing_card = AgentCard(
    name="publishing_agent",
    description="Checks data for publishing on end blog platform.",
    defaultInputModes=["text/plain"],
    defaultOutputModes=["application/json"],
    skills=[
        {
            "id": "publishing_agent",
            "name": "publishing_agent",
            "description": "Checks data for publishing on end blog platform.",
            "tags": ["publishing"]
        }
    ],
    url=PUBLISHING_URL,   # set via env var, e.g. http://localhost:8003/check or Cloud Run URL
    capabilities={},      # can be empty if no special capabilities
    version="1.0.0"
)

# Agents
publishing_agent = RemoteA2aAgent(
    name="publishing_agent",
    description="Agent that publish content on blog platform.",
    agent_card=publishing_card
)

agent = Agent(agent_card=seo_card)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/optimize")
async def optimize(request: Request):
    data = await request.json()
    text = data.get("draft", "")
    optimized = text + "\n\n# SEO\nKeywords: blogging, research, learning"
    response = {"optimized_draft": optimized}
    agent.send(Message("publishing_agent", response))
    return response

maps_toolset = tools.get_maps_mcp_toolset()
bigquery_toolset = tools.get_bigquery_mcp_toolset()

root_agent = LlmAgent(
    model='gemini-2.5-flash-lite',
    name='root_agent',
    instruction=f"""
                Help the user answer questions by strategically combining insights from two sources:
                
                1.  **BigQuery toolset:** Access mcp-seo-data in the mcp_blog dataset. Do not use any other datasets.
                Run all query jobs from project id: {PROJECT_ID}. 

                2.  **Maps Toolset:** Use this for real-world location analysis, finding competition/places and calculating necessary travel routes.
                    Include a hyperlink to an interactive map in your response where appropriate.
            """,
    tools=[maps_toolset, bigquery_toolset],
    sub_agents=[seo_agent]
)
