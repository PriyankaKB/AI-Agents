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

FEEDBACK_URL = os.getenv("FEEDBACK_AGENT_URL", "http://localhost:8004/check")

feedback_card = AgentCard(
    name="feedback-agent",
    description="Checks feedback from content reader.",
    defaultInputModes=["text/plain"],
    defaultOutputModes=["application/json"],
    skills=[
        {
            "id": "feedback-agent",
            "name": "feedback-agent",
            "description": "Checks feedback from content reader.",
            "tags": ["feedback"]
        }
    ],
    url=FEEDBACK_URL,     # set via env var, e.g. http://localhost:8004/check or Cloud Run URL
    capabilities={},      # can be empty if no special capabilities
    version="1.0.0"
)

# Agents
feedback-agent = RemoteA2aAgent(
    name="feedback-agent",
    description="Agent that gets blog feedback from user.",
    agent_card=feedback_card
)

agent = Agent("publishing-agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/publish")
async def publish(request: Request):
    data = await request.json()
    text = data.get("optimized_draft", "")
    print("🌐 Publishing Agent: Blog post published.")
    response = {"status": "published", "content": text}
    agent.send(Message("feedback-agent", response))
    return response

maps_toolset = tools.get_maps_mcp_toolset()
bigquery_toolset = tools.get_bigquery_mcp_toolset()

root_agent = LlmAgent(
    model='gemini-2.5-flash-lite',
    name='root_agent',
    instruction=f"""
                Help the user answer questions by strategically combining insights from two sources:
                
                1.  **BigQuery toolset:** Access mcp-publishing-data in the mcp_blog dataset. Do not use any other dataset.
                Run all query jobs from project id: {PROJECT_ID}. 

                2.  **Maps Toolset:** Use this for real-world location analysis, finding competition/places and calculating necessary travel routes.
                    Include a hyperlink to an interactive map in your response where appropriate.
            """,
    tools=[maps_toolset, bigquery_toolset],
    sub_agents=[publishing-agent]
)
