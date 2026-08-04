"""
Legal Compass — Flask Backend
REST API connecting the NLP engine and SQLite database to the frontend.

Endpoints:
  GET  /                  → serves maincode.html
  POST /api/chat          → process a legal query
  GET  /api/history       → fetch conversation history
  POST /api/clear         → clear session history
  GET  /api/stats         → usage statistics
  GET  /api/suggestions   → suggested legal questions
  GET  /api/categories    → KB category counts
"""
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from database import init_db, save_conversation, get_history, clear_history, get_stats
from nlp_engine import LegalNLPEngine

# ── App setup ──────────────────────────────────────────────────
app = Flask(__name__, static_folder=".", template_folder=".")
CORS(app)  # Allow cross-origin requests from the HTML frontend

print("\n" + "=" * 55)
print("  Legal Compass — AI-Powered Legal Assistant")
print("=" * 55)

# Initialise database and NLP engine at startup
init_db()
nlp = LegalNLPEngine()

print("=" * 55)
print("  Backend ready. Serving on http://localhost:5000")
print("=" * 55 + "\n")


# ── Routes ─────────────────────────────────────────────────────
@app.route("/")
def index():
    """Serve the main frontend HTML."""
    return send_from_directory(".", "maincode.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Process a legal query through the NLP pipeline.
    Body: { "message": str, "session_id": str (optional) }
    """
    data = request.get_json(force=True, silent=True) or {}
    message = (data.get("message") or "").strip()
    session_id = (data.get("session_id") or "default").strip()

    if not message:
        return jsonify({"error": "Message cannot be empty."}), 400

    result = nlp.answer(message)
    save_conversation(
        session_id,
        message,
        result["answer"],
        result.get("category", "general"),
    )

    return jsonify(
        {
            "answer": result["answer"],
            "category": result.get("category", "general"),
            "confidence": result.get("confidence", 0),
            "sources": result.get("sources", []),
        }
    )


@app.route("/api/history", methods=["GET"])
def history():
    """
    Return the last 50 messages for a session.
    Query param: session_id (optional, default='default')
    """
    session_id = request.args.get("session_id", "default")
    return jsonify(get_history(session_id))


@app.route("/api/clear", methods=["POST"])
def clear():
    """
    Delete all messages for a session.
    Body: { "session_id": str }
    """
    data = request.get_json(force=True, silent=True) or {}
    session_id = (data.get("session_id") or "default").strip()
    clear_history(session_id)
    return jsonify({"status": "ok", "message": "Chat history cleared."})


@app.route("/api/stats", methods=["GET"])
def stats():
    """Return aggregate usage statistics."""
    return jsonify(get_stats())


@app.route("/api/suggestions", methods=["GET"])
def suggestions():
    """
    Return suggested legal questions.
    Query param: category (constitution | ipc | crpc | general)
    """
    category = request.args.get("category", None)
    return jsonify(nlp.get_suggestions(category))


@app.route("/api/categories", methods=["GET"])
def categories():
    """Return entry counts per category in the knowledge base."""
    return jsonify(nlp.get_categories())


# ── Entry point ────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") != "production"
    app.run(debug=debug, port=port, host="0.0.0.0")
