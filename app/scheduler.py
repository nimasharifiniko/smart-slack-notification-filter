import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
from openai import OpenAI
from dotenv import load_dotenv
from app.database import get_unsummarized_messages, mark_messages_as_summarized

load_dotenv()

# Initialize OpenAI client for local Ollama
base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
model_name = os.getenv("AI_MODEL_NAME", "qwen2.5-coder:7b")

client = OpenAI(
    base_url=base_url,
    api_key="ollama"
)

SUMMARY_SYSTEM_PROMPT = """
You are an executive AI assistant that creates concise work summaries for remote teams.

You will receive a list of non-urgent workplace messages.
Your task is to organize and summarize them into a clean Slack-formatted text.

Formatting Guidelines for Slack:
- Use *bold* for key categories.
- Use bullet points (•) for grouped items.
- Keep it extremely brief, clear, and action-oriented.
- Do NOT include markdown code blocks (```). Just plain Slack markdown text.

Example Output format:
📋 *PERIODIC ACTIVITY DIGEST*
• *General Updates*: 2 team members discussed lunch and coffee plans.
• *Documentation*: Request to review updated documentation link.
"""

def generate_ai_summary(messages: list) -> str:
    """
    Takes a list of message dicts and generates a bulleted summary using local LLM.
    """
    if not messages:
        return ""

    formatted_input = "\n".join([
        f"- [{msg.get('category', 'General')}]: {msg.get('text')}"
        for msg in messages
    ])

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": f"Messages to summarize:\n{formatted_input}"}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error generating summary from LLM: {e}")
        return "⚠️ Failed to generate AI summary."

def process_and_send_summary(slack_app):
    """
    Cron job function: Fetches unsummarized messages, summarizes via AI, posts to Slack.
    """
    print("\n⏰ Scheduler Triggered: Checking for pending non-urgent messages...")
    pending_messages = get_unsummarized_messages()

    if not pending_messages:
        print("ℹ️ No pending messages to summarize. Skipping job.")
        return

    print(f"📊 Found {len(pending_messages)} pending messages. Generating AI digest...")
    
    # Generate AI Digest
    summary_text = generate_ai_summary(pending_messages)
    
    # Target channel from env or first message channel
    target_channel = os.getenv("SLACK_DEFAULT_CHANNEL") or pending_messages[0]["channel_id"]

    try:
        # Send message to Slack channel
        slack_app.client.chat_postMessage(
            channel=target_channel,
            text=f"📋 *PERIODIC NOTIFICATION DIGEST*\n\n{summary_text}\n\n_Batch processed {len(pending_messages)} non-urgent notification(s)._"
        )
        print(f"✅ Summary posted successfully to channel [{target_channel}]!")

        # Mark messages as summarized in DB
        msg_ids = [msg["id"] for msg in pending_messages]
        mark_messages_as_summarized(msg_ids)
        print(f"💾 Marked {len(msg_ids)} messages as summarized in database.")

    except Exception as e:
        print(f"❌ Failed to send summary to Slack: {e}")

def start_scheduler(slack_app, interval_seconds=60):
    """
    Starts background scheduler running every `interval_seconds`.
    """
    scheduler = BackgroundScheduler()
    # Add recurring job
    scheduler.add_job(
        process_and_send_summary,
        'interval',
        seconds=interval_seconds,
        args=[slack_app]
    )
    scheduler.start()
    print(f"⏱️ Background Scheduler started (Running every {interval_seconds} seconds)...")
    return scheduler