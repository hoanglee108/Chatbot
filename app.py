from flask import Flask, request, jsonify, session, render_template, redirect, url_for, Response
import os
import json
import time
from datetime import datetime
from utils import handle_query, load_and_prepare_documents, Retriever, stream_generator

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# Load dữ liệu & khởi tạo retriever
json_path = "crawl/mon_ngon.json"
df, documents = load_and_prepare_documents(json_path)
retriever = Retriever(documents)

@app.route("/", methods=["GET", "POST"])
def index():
    if "chat_history" not in session:
        session["chat_history"] = []

    if request.method == "POST":
        user_input = request.form["query"]
        session["chat_history"].append(("Bạn", user_input))
        session.modified = True

        kind, result = handle_query(user_input, retriever, df)
        session["chat_history"].append(("Trợ lý", result))
        session.modified = True
        return redirect(url_for('index'))

    return render_template("index.html", chat_history=session["chat_history"])

@app.route("/api/query", methods=["POST"])
def query():
    data = request.json
    user_input = data.get("query", "")
    kind, result = handle_query(user_input, retriever, df)

    def generate_stream():
        for chunk in stream_generator(result):
            yield f"data: {chunk}\n\n"
            time.sleep(0.03)

    return Response(generate_stream(), mimetype="text/event-stream")

@app.route("/api/save_chat", methods=["POST"])
def save_chat():
    data = request.json
    chat = data.get("chat", [])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("history", exist_ok=True)
    file_path = os.path.join("history", f"chat_{timestamp}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chat, f, ensure_ascii=False, indent=2)
    return jsonify({"status": "saved"})

@app.route("/api/history_list", methods=["GET"])
def history_list():
    os.makedirs("history", exist_ok=True)
    files = sorted(os.listdir("history"), reverse=True)
    return jsonify(files)

@app.route("/api/load_chat/<filename>", methods=["GET"])
def load_chat(filename):
    file_path = os.path.join("history", filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "not found"}), 404
    with open(file_path, "r", encoding="utf-8") as f:
        chat = json.load(f)
    return jsonify(chat)

if __name__ == "__main__":
    app.run(debug=True)
