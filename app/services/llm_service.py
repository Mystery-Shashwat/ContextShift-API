import os
import json
import httpx
from fastapi import HTTPException

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

async def generate_structured_context(raw_context: str) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not set.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = (
        "Convert the following raw context into structured JSON with: "
        "problem, current_progress, next_step, open_questions, notes. "
        "Return ONLY valid JSON.\n\n"
        f"Raw Context:\n{raw_context}"
    )

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(GROQ_API_URL, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        except httpx.HTTPStatusError as e:
            error_details = e.response.text
            raise HTTPException(status_code=500, detail=f"LLM generation failed: {e}. Details: {error_details}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")
