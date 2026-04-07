from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


def _call_model(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text.strip() if response.text else "No response generated."


def ask_ai(question: str, context: str = "") -> str:
    prompt = f"""
You are a helpful AI assistant inside a Discord server.

Use the recent channel context if relevant.
Be clear, accurate, and concise.

Recent channel context:
{context}

User question:
{question}

Give a helpful answer.
"""
    return _call_model(prompt)


def rewrite_ai(text: str) -> str:
    prompt = f"""
Rewrite the following text so it is clearer, more polished, and professional.
Keep the original meaning.

Text:
{text}
"""
    return _call_model(prompt)


def summarize_ai(chat_text: str) -> str:
    prompt = f"""
Summarize the following Discord conversation in short bullet points.
Mention the key discussion topics and action items if any.

Conversation:
{chat_text}
"""
    return _call_model(prompt)