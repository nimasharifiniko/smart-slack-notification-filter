import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
from openai import OpenAI
from dotenv import load_dotenv
from app.database import get_unsummarized_messages, mark_messages_as_summarized

load_dotenv()

base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
model_name = os.getenv("AI_MODEL_NAME", "qwen2.5-coder:7b")

client = OpenAI(
    base_url=base_url,
    api_key="ollama"
)

SUMMARY_SYSTEM_PROMPT = """
You are an executive AI assistant creating concise work summaries for remote teams.

Summarize the provided workplace messages into a clean Slack-formatted text.

Formatting Guidelines for Slack:
- Use *bold* for categories.
- Use bullet points (•) for items.
- Keep it brief, clear, and actionable.
- Do NOT use markdown code blocks (```).

Example:
📋 *PERIODIC ACTIVITY DIGEST*
• *General Updates*: 2 team members discussed lunch plans.
• *Documentation*: Request to review updated docs.
"""


def generate_ai_summary(messages: list) -> str:
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
        print(f"❌ Error generating summary: {e}")
        return "⚠️ Failed to generate AI summary."


def process_and_send_summary(slack_app):
    print("\n⏰ Scheduler Triggered: Checking for pending messages...")
    pending_messages = get_unsummarized_messages()

    if not pending_messages:
        print("ℹ️ No pending messages. Skipping digest job.")
        return

    print(
        f"📊 Processing {len(pending_messages)} pending message(s) for AI digest...")
    summary_text = generate_ai_summary(pending_messages)

    target_channel = os.getenv(
        "SLACK_DEFAULT_CHANNEL") or pending_messages[0]["channel_id"]

    try:
        slack_app.client.chat_postMessage(
            channel=target_channel,
            text=f"📋 *PERIODIC NOTIFICATION DIGEST*\n\n{summary_text}\n\n_Batch processed {len(pending_messages)} non-urgent notification(s)._"
        )
        print(f"✅ Digest posted successfully to channel [{target_channel}]!")

        msg_ids = [msg["id"] for msg in pending_messages]
        mark_messages_as_summarized(msg_ids)
        print(f"💾 Marked {len(msg_ids)} messages as summarized in SQLite.")

    except Exception as e:
        print(f"❌ Failed to send summary to Slack: {e}")


def start_scheduler(slack_app, interval_seconds=None):
    if interval_seconds is None:
        interval_seconds = int(os.getenv("DIGEST_INTERVAL_SECONDS", "60"))

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        process_and_send_summary,
        'interval',
        seconds=interval_seconds,
        args=[slack_app]
    )
    scheduler.start()
    print(f"⏱️ Background Scheduler active (Interval: {interval_seconds}s)...")
    return scheduler
