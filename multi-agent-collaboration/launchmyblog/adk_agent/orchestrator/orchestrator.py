from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import dotenv

dotenv.load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DRAFTING_URL = os.getenv("DRAFTING_AGENT_URL", "http://localhost:8000/check")
PLAGIARISM_URL = os.getenv("PLAGIARISM_AGENT_URL", "http://localhost:8001/check")
SEO_URL = os.getenv("SEO_AGENT_URL", "http://localhost:8002/check")
PUBLISHING_URL = os.getenv("PUBLISHING_AGENT_URL", "http://localhost:8003/check")
FEEDBACK_URL = os.getenv("FEEDBACK_AGENT_URL", "http://localhost:8004/check")


# Replace with actual Cloud Run URLs after deployment
AGENT_URLS = {
    "drafting": DRAFTING_URL,
    "plagiarism": PLAGIARISM_URL,
    "seo": SEO_URL,
    "publishing": PUBLISHING_URL,
    "feedback": FEEDBACK_URL,
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
