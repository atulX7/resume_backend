import logging

import openai
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger("app")
openai.api_key = settings.OPENAI_API_KEY  # Set OpenAI API key


def call_openai(prompt: str):
    """Sends a request to OpenAI's GPT-4o and retrieves the response."""
    logger.info("📡 Sending prompt to OpenAI GPT-4o")
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}]
        )
        content = response.choices[0].message.content
        logger.info("✅ Successfully received response from OpenAI")
        return content
    except openai.OpenAIError as e:
        logger.error(f"❌ OpenAI API error: {str(e)}", exc_info=True)
        raise Exception(f"OpenAI API error: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error calling OpenAI: {str(e)}", exc_info=True)
        raise Exception(f"Unexpected error calling OpenAI: {str(e)}")

