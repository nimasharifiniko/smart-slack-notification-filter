import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from app.ai_classifier import classify_message
from app.database import init_db, save_message

# Load environment variables
load_dotenv()

# Initialize Slack App instance
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


@app.event("message")
def handle_message_events(body, say, logger):
    event = body.get("event", {})
    text = event.get("text")
    user = event.get("user")
    channel = event.get("channel")
    thread_ts = event.get("ts")

    # Ignore bot messages to prevent infinite loops
    if event.get("subtype") == "bot_message" or event.get("bot_id"):
        return

    if not text:
        return

    print("\n--------------------------------------------------")
    print(f"📩 New Message in Channel [{channel}] from User [{user}]:")
    print(f"💬 Text: \"{text}\"")
    print("🤖 Analyzing with Local AI Engine...")

    # AI Urgency Analysis
    analysis = classify_message(text)
    urgency = analysis.get("urgency", "NON_URGENT")
    category = analysis.get("category", "General")
    reason = analysis.get("reason", "N/A")

    if urgency == "URGENT":
        print("🚨 URGENT message detected! Sending immediate alert to Slack...")
        # Reply directly in thread for urgent alerts
        alert_text = (
            f"🚨 *URGENT ALERT DETECTED*\n"
            f"*Category:* {category}\n"
            f"*Reason:* {reason}\n"
            f"_Immediate team attention required!_"
        )
        say(text=alert_text, thread_ts=thread_ts)
    else:
        print("ℹ️ NON_URGENT message detected. Storing into database for batch summary...")
        msg_id = save_message(
            channel_id=channel,
            user_id=user,
            text=text,
            urgency=urgency,
            category=category,
            reason=reason
        )
        print(f"💾 Saved to SQLite DB with Record ID: {msg_id}")

    print("--------------------------------------------------\n")


def start_slack_app():
    # Initialize SQLite database schema
    init_db()

    app_token = os.environ.get("SLACK_APP_TOKEN")
    if not app_token:
        raise ValueError("❌ Missing SLACK_APP_TOKEN in .env file.")

    # Import scheduler here to avoid circular imports
    from app.scheduler import start_scheduler

    # Start Background Scheduler (Runs every 60 seconds for demo/testing)
    start_scheduler(app, interval_seconds=60)

    handler = SocketModeHandler(app, app_token)
    print("⚡️ Smart Notification Filter Pipeline active with DB, AI & Scheduler...")
    handler.start()
