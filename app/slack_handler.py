import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

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

    print("\n--------------------------------------------------")
    print(f"📩 New Message Received!")
    print(f"👤 Sender (User ID): {user}")
    print(f"💬 Content: {text}")
    print("--------------------------------------------------\n")


def start_slack_app():
    app_token = os.environ.get("SLACK_APP_TOKEN")
    if not app_token:
        raise ValueError("❌ Missing SLACK_APP_TOKEN in .env file.")

    handler = SocketModeHandler(app, app_token)
    print("⚡️ Smart Notification Filter is running in Socket Mode...")
    handler.start()

