from flask import Flask, request, jsonify, session, render_template, redirect, url_for
import os
from utils import handle_query, load_and_prepare_documents, Retriever

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

        kind, result = handle_query(user_input, retriever)
        session["chat_history"].append(("Trợ lý", result))
        session.modified = True
        return redirect(url_for('index'))

    return render_template("index.html", chat_history=session["chat_history"])

@app.route("/api/query", methods=["POST"])
def query():
    data = request.json
    user_input = data.get("query", "")
    kind, result = handle_query(user_input, retriever)
    return jsonify({"response": result})

if __name__ == "__main__":
    app.run(debug=True)
