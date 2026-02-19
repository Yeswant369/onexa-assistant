import os
from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from dotenv import load_dotenv
from knowledge import ONEXA_DATA

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

import re

def is_onexa_related(message):
    message = message.lower()

    # Extract words from knowledge base dynamically
    knowledge_words = set(
        re.findall(r'\b[a-zA-Z]+\b', ONEXA_DATA.lower())
    )

    # Extract words from user message
    user_words = set(
        re.findall(r'\b[a-zA-Z]+\b', message)
    )

    # Remove very small words
    knowledge_words = {w for w in knowledge_words if len(w) > 3}
    user_words = {w for w in user_words if len(w) > 3}

    # Allow if at least one meaningful word overlaps
    return len(user_words.intersection(knowledge_words)) > 0


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

def get_knowledge_response(message):
    """Fallback response generator based on knowledge base"""
    message = message.lower()
    
    if "c++" in message or "cpp" in message:
        return """C++ Programming Course

**Current Use Cases of C++:**
• System/software development (operating systems, compilers)
• Game development (high-performance graphics)
• Embedded systems and IoT devices
• High-frequency trading systems
• Database management systems
• Browser development

**Standard Durations:**
• Beginner Level: 3-4 months (basic syntax, OOP concepts)
• Intermediate Level: 4-5 months (data structures, STL)
• Advanced Level: 5-6 months (system design, competitive programming)

**Customizable Duration:**
The actual course duration can be customized based on:
• Your current programming experience
• Weekly time commitment (2-6 hours/week)
• Specific learning goals (placement prep, projects, etc.)

For a personalized learning plan and exact duration:

📧 Email: support@onexa.com
📞 Phone: +91-9000000000

Contact us for a free consultation!"""
    
    elif "course" in message or "program" in message:
        return """We offer several programs:

1. IIT Foundation & Advanced Program (6-12 months)
   • Live Google Meet sessions
   • Mathematics & Physics focus
   • Weekly mock tests

2. Computer Science Track (4-6 months)
   • Python/C++ programming
   • Data Structures & Algorithms
   • Real-world projects

3. Communication & Personality Development (3 months)
   • Public speaking
   • Interview preparation
   • Confidence building

Which program interests you?"""
    
    elif "enroll" in message or "admission" in message:
        return """To enroll in Onexa:

• Request a consultation call
• Academic assessment
• Personalized roadmap creation
• Program onboarding

Please provide your Customer ID if you have one, or I can help you start the enrollment process."""
    
    elif "price" in message or "pricing" in message or "cost" in message:
        return "For pricing details, I recommend booking a **consultation call** where we can discuss the best program for your needs and provide customized pricing. Would you like me to help you schedule one?"
    
    elif "contact" in message or "support" in message or "help" in message:
        return """You can reach Onexa support at:

• Email: support@onexa.com
• Phone: +91-9000000000

For enrollment issues, please provide your Customer ID for faster assistance."""
    
    elif "demo" in message or "trial" in message:
        return "Yes! We offer demo sessions. Please contact our support team at support@onexa.com or +91-9000000000 to schedule a demo."
    
    elif "roadmap" in message or "plan" in message:
        return "I can help create a personalized roadmap for you! First, let me know which program you're interested in (IIT, CSE, or Communication), and I'll generate a structured learning plan."
    
    elif "iit" in message or "jee" in message:
        return """IIT Foundation & Advanced Program

Duration: 6-12 months
Mode: Live Google Meet

Includes:
• Concept mastery sessions
• Weekly mock tests
• Doubt clearing
• Personalized mentor guidance

Ideal for: Students preparing for IIT/JEE or those weak in mathematics/physics

Would you like to enroll?"""
    
    elif "cse" in message or "coding" in message or "programming" in message or "python" in message:
        return """Computer Science & Engineering Track

Duration: 4-6 months

Includes:
• Programming fundamentals (Python/C++)
• Data Structures & Algorithms
• Live coding practice
• Real-world project building
• Career roadmap guidance

Ideal for: Beginners in coding and students aiming for tech careers

Interested in learning more?"""
    
    elif "duration" in message or "time" in message or "how long" in message or "length" in message:
        return """The course duration depends on your individual requirements and current skill level.

For personalized details about program duration and scheduling:

📧 Email: support@onexa.com
📞 Phone: +91-9000000000

Contact us for a free consultation where we can assess your needs and recommend the best timeline for you."""
    
    elif "communication" in message or "speaking" in message or "interview" in message:
        return """Communication & Personality Development

Duration: 3 months

Includes:
• Public speaking training
• Interview preparation
• Confidence building
• Mock interviews with feedback

Ideal for: College students and job aspirants

Ready to improve your communication skills?"""
    
    elif "backend" in message or "b.tech" in message or "btech" in message or "engineering" in message:
        return """Great! Based on your background in B.Tech and interest in backend development, I recommend:

Computer Science & Engineering Track (4-6 months)

This program is perfect for you:
• Programming fundamentals (Python/C++)
• Data Structures & Algorithms - essential for backend
• Live coding practice with real projects
• Backend system design concepts
• Career roadmap guidance for software development

As a B.Tech first year student, this will give you a strong foundation and practical skills for backend development careers.

Would you like to:
• Learn more about the curriculum?
• Schedule a consultation call?
• Get enrollment details?"""
    
    else:
        return "I can assist only with Onexa-related services. Please contact support for further assistance."

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]

    if not is_onexa_related(user_input):
        return jsonify({
            "reply": "I can assist only with Onexa-related services. Please contact support for further assistance."
        })

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
        bot_reply = get_knowledge_response(user_input)

    # Add bot reply to memory
    session["history"].append({"role": "assistant", "content": bot_reply})

    return jsonify({"reply": bot_reply})


if __name__ == "__main__":
    print("🚀 Starting Onexa Assistant...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


#if __name__ == "__main__":
 #   app.run(debug=True)
