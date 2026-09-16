import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from app.ai_classifier import classify_message

# Load environment variables from .env
load_dotenv()

# Initialize Slack App instance
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Event listener for channel messages


@app.event("message")
def handle_message_events(body, logger):
    event = body.get("event", {})
    text = event.get("text")
    user = event.get("user")

    # Ignore bot messages to prevent infinite loops
    if event.get("subtype") == "bot_message" or event.get("bot_id"):
        return

    if not text:
        return

    print("\n--------------------------------------------------")
    print(f"📩 New Message Received from User [{user}]:")
    print(f"💬 Text: \"{text}\"")
    print("🤖 Analyzing message urgency with local AI...")

    # Classify urgency using AI engine
    analysis = classify_message(text)

    urgency_emoji = "🚨" if analysis.get("urgency") == "URGENT" else "ℹ️"

    print(f"\n{urgency_emoji} AI Classification Result:")
    print(f"   • Urgency: {analysis.get('urgency')}")
    print(f"   • Category: {analysis.get('category')}")
    print(f"   • Reason: {analysis.get('reason')}")
    print("--------------------------------------------------\n")


def start_slack_app():
    app_token = os.environ.get("SLACK_APP_TOKEN")
    if not app_token:
        raise ValueError("❌ Missing SLACK_APP_TOKEN in .env file.")

    handler = SocketModeHandler(app, app_token)
    print("⚡️ Smart Notification Filter with AI is active in Socket Mode...")
    handler.start()
