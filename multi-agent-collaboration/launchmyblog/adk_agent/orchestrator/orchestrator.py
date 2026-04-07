from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Replace with actual Cloud Run URLs after deployment
AGENT_URLS = {
    "drafting": "https://drafting-agent-<region>.run.app/process",
    "plagiarism": "https://plagiarism-agent-<region>.run.app/check",
    "seo": "https://seo-agent-<region>.run.app/optimize",
    "publishing": "https://publishing-agent-<region>.run.app/publish",
    "feedback": "https://feedback-agent-<region>.run.app/feedback",
}

@app.post("/run")
def run_pipeline(draft: dict):
    structured = requests.post(AGENT_URLS["drafting"], json=draft).json()
    plagiarism = requests.post(AGENT_URLS["plagiarism"], json=structured).json()
    optimized = requests.post(AGENT_URLS["seo"], json=plagiarism).json()
    published = requests.post(AGENT_URLS["publishing"], json=optimized).json()
    feedback = requests.post(AGENT_URLS["feedback"], json=published).json()

    return {
        "drafting": structured,
        "plagiarism": plagiarism,
        "seo": optimized,
        "publishing": published,
        "feedback": feedback,
    }
