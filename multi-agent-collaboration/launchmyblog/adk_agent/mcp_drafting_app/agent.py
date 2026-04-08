import os
import dotenv
from mcp_drafting_app import tools
from google.adk.agents import LlmAgent
from google.adk import Agent
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from a2a.types import Message
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

dotenv.load_dotenv()

PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'project_not_set')

app = FastAPI()

# Agents
plagiarism_agent = RemoteA2aAgent(
    name="plagiarism-agent",
    description="Agent that detect overlapping content and plagiarism.",
)

agent = Agent("drafting-agent")

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
    agent.send(Message("plagiarism-agent", response))
    return response

maps_toolset = tools.get_maps_mcp_toolset()
bigquery_toolset = tools.get_bigquery_mcp_toolset()

root_agent = LlmAgent(
    model='gemini-2.5-flash-lite',
    name='drafting-agent',
    description="Creates drafts for blog content.",
    instruction=f"""
                Help the user answer questions by strategically combining insights from two sources:
                
                1.  **BigQuery toolset:** Access mcp-drafting-data in the mcp_blog dataset. Do not use any other dataset.
                Run all query jobs from project id: {PROJECT_ID}. 

                2.  **Maps Toolset:** Use this for real-world location analysis, finding competition/places and calculating necessary travel routes.
                    Include a hyperlink to an interactive map in your response where appropriate.
            """,
    tools=[maps_toolset, bigquery_toolset]
    sub_agents=[drafting-agent]
)
