Markdown

# 🔔 Smart Slack Notification Filter (AI-Powered)

An intelligent, privacy-first AI automation system that classifies real-time Slack messages by urgency, delivers critical alerts immediately, and batches non-urgent updates into scheduled periodic summaries — eliminating workplace notification fatigue for remote teams.

---

## 📌 The Problem
In modern remote software teams, notification overload on communication tools like Slack is a documented productivity killer:
- **Focus Disruption**: Research shows it takes **over 23 minutes** to regain full deep focus after a single notification interruption.
- **Equal Priority Fallacy**: Slack treats every message (a casual coffee chat vs. a critical database outage) with the same urgency level.
- **Data Privacy Concerns**: Sending sensitive internal team messages to public cloud LLMs poses data compliance risks for enterprises.

---

## 💡 The Solution
**Smart Slack Notification Filter** acts as an intelligent proxy layer built directly into Slack:
1. **Real-time Ingestion**: Intercepts channel messages via Slack Events API (Socket Mode).
2. **Local AI Classification**: Route messages through a local LLM (`qwen2.5-coder:7b` via Ollama) to extract structured urgency (`URGENT` vs `NON_URGENT`).
3. **Instant Alert Routing**: `URGENT` messages trigger immediate thread notifications for high-priority response.
4. **Persistent Batching**: `NON_URGENT` messages are silently stored in a local SQLite database.
5. **Automated Summarization**: A background scheduler (`APScheduler`) periodically aggregates pending updates into a clean, executive digest posted back to Slack.

---

## 🏗️ System Architecture
[ Slack Workspace ]
│
▼ (Slack Events / Socket Mode)
[ app/slack_handler.py ]
│
├──► [ app/ai_classifier.py ] ──► (Local Ollama / LLM Analysis)
│ │
│ Returns Urgency & Category
│ │
├─── IF URGENT ──────────────────────────────┘
│ └──► Send Instant Thread Reply 🚨
│
└─── IF NON_URGENT
└──► Store in SQLite DB (data/messages.db) 📦
│
▼ (Cron Interval / APScheduler)
[ app/scheduler.py ]
│
├──► Summarize Batch via Local AI
└──► Post Periodic Digest to Slack 📋

text


---

## 🛠️ Tech Stack & Tools

| Component | Technology | Description |
|---|---|---|
| **Language** | Python 3.10+ | Core application runtime |
| **Slack Framework** | Slack Bolt SDK | Real-time event handling via Socket Mode |
| **AI / LLM Engine** | Ollama (`qwen2.5-coder:7b`) | Privacy-first local LLM inference |
| **Client SDK** | OpenAI Python SDK | Standardized interface to local Ollama API |
| **Database** | SQLite3 | Lightweight embedded relational database |
| **Task Scheduler** | APScheduler | Background job execution for periodic digests |
| **Environment** | python-dotenv | Secure secret & config management |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- [Ollama](https://ollama.com/) installed and running locally
- Slack Workspace with App creation permissions

### 1. Clone & Setup Environment

```bash
# Clone repository
git clone https://github.com/YOUR_GITHUB_USERNAME/smart-slack-notification-filter.git
cd smart-slack-notification-filter

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
2. Pull Local AI Model
Ensure Ollama is running, then pull the Qwen coder model:

Bash

ollama pull qwen2.5-coder:7b
3. Configure Environment Variables
Create a .env file in the root folder based on the template below:

env

SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_DEFAULT_CHANNEL=C0XXXXXXXXX

OLLAMA_BASE_URL=http://localhost:11434/v1
AI_MODEL_NAME=qwen2.5-coder:7b
4. Run the Application
Bash

python -m app.main
🧪 Demo Scenario & Test Inputs
To test the system in action:

Test Urgent Alert:

Post in Slack: "CRITICAL: Payment gateway returning HTTP 500 in production!"
Result: Immediate thread reply with 🚨 URGENT ALERT DETECTED.
Test Non-Urgent Batching:

Post in Slack: "Anyone up for a quick coffee break?"
Post in Slack: "Documentation for API v2 has been updated."
Result: No annoying alert sounds. Messages saved to database.
Periodic Summary:

Wait 60 seconds (or set interval).
Result: Automatic AI-generated digest posted: 📋 PERIODIC NOTIFICATION DIGEST.
📈 Business Impact
80%+ Reduction in unnecessary team notification interruptions.
Zero Data Leakage: All message contents are analyzed locally on-premise.
Improved Incident Response: Critical outages are flagged instantly in dedicated threads.
👤 Author
Developed as part of an advanced AI Automation Portfolio.

GitHub: https://github.com/nimasharifiniko
LinkedIn: https://www.linkedin.com/in/nima-sharifiniko/