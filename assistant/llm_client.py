import os
from dotenv import load_dotenv
from fastapi import HTTPException
from google import genai
from google.genai import types

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = (
    "You are an inventory assistant for a shop. "
    "Answer ONLY from the data provided in the message. "
    "Never invent numbers, products or facts. "
    "If the data does not contain the answer, say so. Be concise."
)

_client = None


def _get_client():
    """Create the Gemini client on first use, so a missing key does not
    stop the whole API from starting."""
    global _client
    if _client is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=503, detail="GOOGLE_API_KEY is not set on the server.")
        _client = genai.Client(api_key=api_key)
    return _client


def ask_llm(prompt: str) -> str:
    try:
        response = _get_client().models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0,
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI service unavailable (quota or network?): {type(e).__name__}"
        )
    return response.text or "The AI service returned an empty answer. Please try again."