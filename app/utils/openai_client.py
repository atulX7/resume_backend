import openai
import google.generativeai as genai
from app.core.config import settings

openai.api_key = settings.OPENAI_API_KEY  # Set OpenAI API key
genai.configure(api_key=settings.GEMINI_API_KEY)


def call_openai(prompt: str):
    """Sends a request to OpenAI's GPT-4o and retrieves the response."""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}]
    )
    content = response.choices[0].message.content
    return content
    # try:
    #     # ✅ Use Google's Gemini Model (Free Access Available)
    #     model = genai.GenerativeModel("gemini-pro")
    #     response = model.generate_content(prompt)
    #
    #     # ✅ Ensure valid response structure
    #     if response and response.text:
    #         return response.text.strip()
    #
    #     return "No valid response from Gemini."
    #
    # except Exception as e:
    #     print(f"Error in Gemini API call: {str(e)}")
    #     return "Error processing AI request."
