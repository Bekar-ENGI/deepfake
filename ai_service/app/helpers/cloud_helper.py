import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment variables (no defaults)
CLOUD_KEY = os.getenv("CLOUD_KEY")
CLOUD_URL = os.getenv("AI_CLOUD_URL")


def cloud_init(data: str) -> dict:
    
    if not CLOUD_KEY or not CLOUD_URL:
        raise ValueError("CLOUD_KEY or CLOUD_URL is not set in environment variables.")

    response = requests.post(
        CLOUD_URL,
        json={
            "key": CLOUD_KEY,
            "text": data
        }
    )

    if 200 <= response.status_code < 300:
        res = response.json()
        score = res.get("score", 0)  # Sapling score between 0-1
        ai_confidence = round(score * 100, 2)  # convert to percentage
        verdict = f"The given document is/has AI-generated content. The AI confidence is {ai_confidence}%."
        return {"ai_confidence": ai_confidence, "verdict": verdict}

    # On error, just return zero confidence and verdict
    return {"ai_confidence": 0, "verdict": "Error detecting AI content."}

