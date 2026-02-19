import os
from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from dotenv import load_dotenv
from knowledge import ONEXA_DATA

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# -------------------------------
# STRICT ONEXA CONTEXT PROMPT
# -------------------------------
SYSTEM_PROMPT = f"""
You are the official Onexa Assistive AI.

STRICT RULES:
1. Answer ONLY questions related to Onexa programs, services, enrollment, or support.
2. Use ONLY the knowledge provided below.
3. If the user asks anything unrelated (general knowledge, personal advice, politics, coding help, etc.),
   reply EXACTLY with:
   "I can assist only with Onexa-related services. Please contact support for further assistance."
4. If pricing is asked → Suggest consultation call.
5. If enrollment issue → Ask for Customer ID.
6. Be professional and concise.
7. Do NOT hallucinate information.

ONEXA KNOWLEDGE:
{ONEXA_DATA}
"""

# -------------------------------
# STRICT RELEVANCE CHECK
# -------------------------------
def is_onexa_related(message):
    message = message.lower()

    # Check if at least one meaningful word matches knowledge base
    knowledge_words = set(
        word.strip(".,:-").lower()
        for word in ONEXA_DATA.split()
        if len(word) > 3
    )

    user_words = set(
        word.strip(".,:-").lower()
        for word in message.split()
        if len(word) > 3
    )

    # If intersection exists → related
    return len(user_words.intersection(knowledge_words)) > 0


# -------------------------------
# ROUTES
# -------------------------------
@app.route("/")
def home():
    session["history"] = []
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"reply": "Please enter a valid message."})

    # Strict relevance block BEFORE Gemini
    if not is_onexa_related(user_input):
        return jsonify({
            "reply": "I can assist only with Onexa-related services. Please contact support for further assistance."
        })

    # Initialize memory
    if "history" not in session:
        session["history"] = []

    session["history"].append({"role": "user", "content": user_input})

    # Keep last 6 messages only
    session["history"] = session["history"][-6:]

    try:
        # Build conversation context
        conversation_context = ""
        for msg in session["history"]:
            conversation_context += f"{msg['role']}: {msg['content']}\n"

        response = model.generate_content(
            SYSTEM_PROMPT + "\nConversation History:\n" + conversation_context
        )

        bot_reply = response.text.strip()

        # Secondary guard (extra safety)
        if not is_onexa_related(bot_reply):
            bot_reply = "I can assist only with Onexa-related services. Please contact support for further assistance."

    except Exception as e:
        print("Gemini API Error:", e)
        bot_reply = "Currently experiencing technical issues. Please contact support at support@onexa.com."

    session["history"].append({"role": "assistant", "content": bot_reply})

    return jsonify({"reply": bot_reply})


# -------------------------------
# PRODUCTION SAFE START
# -------------------------------
if __name__ == "__main__":
    print("🚀 Starting Onexa Assistant...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
