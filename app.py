import os
from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from dotenv import load_dotenv
from knowledge import ONEXA_DATA

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")



SYSTEM_PROMPT = f"""
You are the official Onexa Assistive AI.

STRICT RULES:
1. Answer ONLY Onexa-related queries.
2. Use ONLY the provided Onexa knowledge.
3. If unrelated, say:
"I can assist only with Onexa-related services. Please contact support for further assistance."
4. If enrollment issue → Ask for Customer ID.
5. If pricing asked → Suggest consultation call.
6. If course planning asked → Generate structured roadmap.
7. Be professional and concise.

ONEXA KNOWLEDGE:
{ONEXA_DATA}
"""

@app.route("/")
def home():
    session["history"] = []
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]

    

    # Initialize memory if not exists
    if "history" not in session:
        session["history"] = []

    # Add user message
    session["history"].append({"role": "user", "content": user_input})

    # Keep last 6 messages only (memory limit)
    session["history"] = session["history"][-6:]

    try:
        # Build conversation context
        conversation_context = ""
        for msg in session["history"]:
            conversation_context += f"{msg['role']}: {msg['content']}\n"

        response = model.generate_content(
            SYSTEM_PROMPT + "\nConversation History:\n" + conversation_context
        )

        bot_reply = response.text

    except Exception as e:
        # Fallback to knowledge base responses when API fails
        print(f"API Error: {e}")
        bot_reply = "Currently experiencing technical issues. Please contact support at support@onexa.com."

    # Add bot reply to memory
    session["history"].append({"role": "assistant", "content": bot_reply})

    return jsonify({"reply": bot_reply})


if __name__ == "__main__":
    print("🚀 Starting Onexa Assistant...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


#if __name__ == "__main__":
 #   app.run(debug=True)
