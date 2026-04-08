import os
import dotenv
from mcp_plagiarism_app import tools
from google.adk.agents import LlmAgent
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from a2a_sdk import Agent, Message

dotenv.load_dotenv()

PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'project_not_set')

app = FastAPI()
agent = Agent("plagiarism-agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/check")
async def check(request: Request):
    data = await request.json()
    text = data.get("structured_draft", "")
    report = "Overlap detected with common topic. Proceed allowed."
    response = {"plagiarism_report": report, "draft": text}
    agent.send(Message("seo-agent", response))
    return response

maps_toolset = tools.get_maps_mcp_toolset()
bigquery_toolset = tools.get_bigquery_mcp_toolset()

root_agent = LlmAgent(
    model='gemini-2.5-flash-lite',
    name='root_agent',
    instruction=f"""
                Help the user answer questions by strategically combining insights from two sources:
                
                1.  **BigQuery toolset:** Access mcp-plagiarism-data in the mcp_blog dataset. Do not use any other dataset.
                Run all query jobs from project id: {PROJECT_ID}. 

                2.  **Maps Toolset:** Use this for real-world location analysis, finding competition/places and calculating necessary travel routes.
                    Include a hyperlink to an interactive map in your response where appropriate.
            """,
    tools=[maps_toolset, bigquery_toolset]
)
