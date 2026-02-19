import os
import re
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


# -----------------------------------
# DYNAMIC KNOWLEDGE TOKEN EXTRACTION
# -----------------------------------
def extract_knowledge_tokens(text):
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    return set(word for word in words if len(word) > 3)

KNOWLEDGE_TOKENS = extract_knowledge_tokens(ONEXA_DATA)


# -----------------------------------
# STRICT RELEVANCE CHECK (DYNAMIC)
# -----------------------------------
def is_onexa_related(message):
    words = re.findall(r'\b[a-zA-Z]+\b', message.lower())
    words = set(word for word in words if len(word) > 3)

    return len(words.intersection(KNOWLEDGE_TOKENS)) > 0


# -----------------------------------
# STRICT SYSTEM PROMPT
# -----------------------------------
SYSTEM_PROMPT = f"""
You are the official Onexa Assistive AI.

STRICT RULES:
1. Answer ONLY using the provided ONEXA KNOWLEDGE.
2. Do NOT add external information.
3. If user asks anything unrelated to the knowledge below,
   respond EXACTLY with:
   "I can assist only with Onexa-related services. Please contact support for further assistance."
4. Pricing questions → Suggest consultation call.
5. Enrollment issue → Ask for Customer ID.
6. Be professional and structured.

ONEXA KNOWLEDGE:
{ONEXA_DATA}
"""


# -----------------------------------
# ROUTES
# -----------------------------------
@app.route("/")
def home():
    session["history"] = []
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"reply": "Please enter a valid message."})

    # STRICT PRE-FILTER
    if not is_onexa_related(user_input):
        return jsonify({
            "reply": "I can assist only with Onexa-related services. Please contact support for further assistance."
        })

    # Initialize memory
    if "history" not in session:
        session["history"] = []

    session["history"].append({"role": "user", "content": user_input})
    session["history"] = session["history"][-6:]

    try:
        conversation_context = ""
        for msg in session["history"]:
            conversation_context += f"{msg['role']}: {msg['content']}\n"

        response = model.generate_content(
            SYSTEM_PROMPT + "\nConversation History:\n" + conversation_context
        )

        bot_reply = response.text.strip()

        # SECONDARY VALIDATION
        if not is_onexa_related(bot_reply):
            bot_reply = "I can assist only with Onexa-related services. Please contact support for further assistance."

    except Exception as e:
        print("Gemini API Error:", e)
        bot_reply = "Currently experiencing technical issues. Please contact support at support@onexa.com."

    session["history"].append({"role": "assistant", "content": bot_reply})

    return jsonify({"reply": bot_reply})


# -----------------------------------
# PRODUCTION START
# -----------------------------------
if __name__ == "__main__":
    print("🚀 Starting Onexa Assistant...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
