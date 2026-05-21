from flask import Flask, render_template, request, Response, jsonify, stream_with_context
import anthropic
import json
import time
import os
import threading

app = Flask(__name__)

_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
client = anthropic.Anthropic(api_key=_api_key) if _api_key else None

conversation_history = []
history_lock = threading.Lock()

SYSTEM_PROMPT = """You are Jarvis, a personal AI assistant running exclusively on a dedicated Samsung Galaxy tablet. This device exists for one purpose: to communicate with you. The user built this tablet specifically for you.

Be natural, warm, and genuinely helpful. Keep responses conversational and appropriately concise — this interface supports voice output.

You have access to device tools. To trigger them, append a hashtag command at the very end of your response (after all your text). The user will never see these tags:
- #weather — fetch current weather
- #play — play music via Spotify
- #pause — pause music
- #skip — next track
- #previous — previous track
- #search-<query> — image search

Use these silently and only when clearly relevant."""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    def error_stream(msg):
        def gen():
            yield f"data: {json.dumps({'type': 'error', 'text': msg})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'speech': ''})}\n\n"
        return Response(stream_with_context(gen()), mimetype="text/event-stream",
                        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    if not client:
        return error_stream("ANTHROPIC_API_KEY not configured. Edit .env and restart.")

    data = request.get_json()
    if not data or not data.get("message", "").strip():
        return jsonify({"error": "No message"}), 400

    user_message = data["message"].strip()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    with history_lock:
        conversation_history.append({"role": "user", "content": f"{user_message} [{timestamp}]"})
        messages_snapshot = list(conversation_history)

    def generate():
        full_response = ""
        try:
            with client.messages.stream(
                model="claude-opus-4-7",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=messages_snapshot,
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    yield f"data: {json.dumps({'type': 'token', 'text': text})}\n\n"
        except anthropic.AuthenticationError:
            yield f"data: {json.dumps({'type': 'error', 'text': 'Invalid API key. Check your ANTHROPIC_API_KEY.'})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'speech': ''})}\n\n"
            return
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'text': str(e)})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'speech': ''})}\n\n"
            return

        with history_lock:
            conversation_history.append({"role": "assistant", "content": full_response})

        speech_text = full_response
        tool_cmd = None
        if "#" in full_response:
            parts = full_response.split("#", 1)
            speech_text = parts[0].strip()
            tool_cmd = parts[1].strip()

        if tool_cmd:
            try:
                import tools
                result = tools.parse_command(tool_cmd)
                if result:
                    yield f"data: {json.dumps({'type': 'tool', 'data': str(result)})}\n\n"
            except Exception as e:
                print(f"Tool error: {e}")

        yield f"data: {json.dumps({'type': 'done', 'speech': speech_text})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/clear", methods=["POST"])
def clear():
    global conversation_history
    with history_lock:
        conversation_history = []
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Jarvis running at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
