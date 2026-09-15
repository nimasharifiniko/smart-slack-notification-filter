import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client configured for local Ollama
base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
model_name = os.getenv("AI_MODEL_NAME", "qwen2.5-coder:7b")

client = OpenAI(
    base_url=base_url,
    api_key="ollama"  # Dummy key required by OpenAI client SDK
)

SYSTEM_PROMPT = """
You are an AI assistant specialized in classifying workplace messages for notification filtering.

Analyze the given Slack message and classify it into one of two urgency levels:
1. URGENT: Requires immediate action, critical bug fixes, server outages, production failures, blocked work, or direct urgent requests.
2. NON_URGENT: Informational updates, general questions, status reports, social chat, or low-priority requests.

Return ONLY a valid JSON object with the following structure (no extra text or markdown formatting):
{
    "urgency": "URGENT" or "NON_URGENT",
    "category": "Critical Bug / System Outage / Status Update / General Question / Other",
    "reason": "Brief explanation of why this classification was chosen."
}
"""


def classify_message(message_text: str) -> dict:
    """
    Analyzes message content using local LLM and returns urgency classification.
    """
    if not message_text or not message_text.strip():
        return {
            "urgency": "NON_URGENT",
            "category": "Empty",
            "reason": "Empty message body."
        }

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Message: \"{message_text}\""}
            ],
            temperature=0.1
        )

        raw_output = response.choices[0].message.content.strip()

        # Clean potential markdown JSON backticks if present
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.startswith("```"):
            raw_output = raw_output[3:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]

        parsed_result = json.loads(raw_output.strip())
        return parsed_result

    except json.JSONDecodeError:
        print("⚠️ Warning: LLM output was not strict JSON. Fallback to NON_URGENT.")
        return {
            "urgency": "NON_URGENT",
            "category": "Parsing Error",
            "reason": "Failed to parse JSON response from LLM."
        }
    except Exception as e:
        print(f"❌ Classification error: {e}")
        return {
            "urgency": "NON_URGENT",
            "category": "Error",
            "reason": f"System error during analysis: {str(e)}"
        }


# Quick independent testing block
if __name__ == "__main__":
    test_messages = [
        "🚨 PRODUCTION DOWN! The database server is not responding!",
        "Hey team, don't forget we have free pizza in the kitchen today.",
        "Can someone review my pull request when you have time?"
    ]

    print("🧠 Testing AI Classification Engine...\n")
    for msg in test_messages:
        print(f"Input: \"{msg}\"")
        res = classify_message(msg)
        print(f"Output: {json.dumps(res, indent=2)}\n" + "-"*40)
