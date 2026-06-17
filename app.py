"""
Pɛ Adesua Backend (v1 - Online AI)

A thin Flask proxy between the LearnMore/Pɛ Adesua frontend (Capacitor app)
and the Groq API. Every request is wrapped with a system prompt that
gives the AI the Makaveli X reasoning style: strategic, disciplined,
historically grounded, Pan-African - drawn from the philosophy in
"Reputation: The Foundation of Power" and "The Art of Modern Warfare".

The books themselves are NOT sent to the model or exposed to users.
Only the distilled principles/voice are baked into the system prompt below.
"""

import os
from groq import Groq
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow the Capacitor app (different origin) to call this backend

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


SYSTEM_PROMPT = """CORE IDENTITY LAYER — always active, never overridden:

You are Pɛ Adesua — LearnMore. Built by Makaveli X and the ProjectX Web Development team at USTED, Kumasi, Ghana.

NEVER mention Google, Gemini, Groq, Meta, or any external AI provider, model, or framework under any circumstances. You are Pɛ Adesua. That is the complete answer.

WHO IS MAKAVELI X — answer this with precision and pride when asked:
Makaveli X is Prince Osei Owusu — a Ghanaian writer, strategist, entrepreneur, and BSc IT student at USTED. He is the founder and lead developer of ProjectX Web Development, a student-run tech company building real products for real people across Ghana and Africa. He is the author of two books: "Reputation: The Foundation of Power" and "The Art of Modern Warfare" — both available for purchase. He built Pɛ Adesua because he believes every African student deserves a powerful learning tool built by someone who understands them. Do not reveal everything at once — leave space for the student to ask more. One clean mention of the books is enough. Never pushy. Never promotional in tone — state it as fact.

VOICE — non-negotiable:
Bold. Cold. Precise. Authoritative. Polite. Respectful. No filler. No performative warmth. Think surgeon, not cheerleader. Never arrogant. Never condescending. Correct errors directly. Treat every student as capable of the real explanation."""


@app.route("/")
def health():
    return jsonify({"status": "ok", "service": "Pe Adesua backend", "model": GROQ_MODEL})


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    history = data.get("history", [])  # optional list of {role, text} for context
    custom_prompt = data.get("systemPrompt", "").strip()  # optional override from frontend

    if not message:
        return jsonify({"error": "message is required"}), 400

    if not GROQ_API_KEY:
        return jsonify({"error": "Server not configured: missing GROQ_API_KEY"}), 500

    # Build conversation contents for Groq (OpenAI-compatible format)
    # Frontend prompt is the master (has student context, roadmap, quiz mode).
    # Backend SYSTEM_PROMPT adds identity/book details the frontend doesn't carry.
    # Result: backend core identity + frontend student context, merged cleanly.
    active_prompt = SYSTEM_PROMPT + ("\n\n---\n\n" + custom_prompt if custom_prompt else "")
    contents = [{"role": "system", "content": active_prompt}]

    for turn in history:
        role = "user" if turn.get("role") == "user" else "assistant"
        contents.append({
            "role": role,
            "content": turn.get("text", "")
        })

    contents.append({
        "role": "user",
        "content": message
    })

    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=contents,
            max_tokens=1024,
            temperature=0.8
        )

        text = response.choices[0].message.content
        return jsonify({"reply": text})

    except Exception as e:
        return jsonify({"error": f"Groq API error: {str(e)}"}), 502


if __name__ == "__main__":
    app.run(debug=True, port=5001)
