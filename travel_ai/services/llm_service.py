# travel_ai/services/llm_service.py

import httpx
from typing import Dict, Any
from travel_ai.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_URL,
    MODEL_NAME,
    TEMPERATURE,
    REQUEST_TIMEOUT,
)
from travel_ai.utils.logger import get_logger

logger = get_logger("llm_service")


async def generate_content(system_prompt: str, user_prompt: str) -> str:
    headers: Dict[str, str] = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload: Dict[str, Any] = {
        "model": MODEL_NAME,
        "temperature": TEMPERATURE,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        response = await client.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
        )

    if response.status_code != 200:
        logger.error(f"OpenRouter error: {response.text}")
        raise RuntimeError(f"OpenRouter API failed: {response.status_code}")

    data = response.json()
    return data["choices"][0]["message"]["content"]