from flask import Flask, request, jsonify, session, render_template, redirect, url_for
import pandas as pd
from utils import handle_query
import os

app = Flask(__name__)
app.secret_key = os.urandom(24).hex() 


import json
with open("crawl/mon_ngon.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f) 
df = pd.DataFrame(data)

@app.route("/", methods=["GET", "POST"])
def index():
    if "chat_history" not in session:
        session["chat_history"] = []

    if request.method == "POST":
        user_input = request.form["query"]
        session["chat_history"].append(("Bạn", user_input))
        session.modified = True

        kind, result = handle_query(user_input, df)
        session["chat_history"].append(("Trợ lý", result))
        session.modified = True
        return redirect(url_for('index'))

    return render_template("index.html", chat_history=session["chat_history"])

@app.route("/api/query", methods=["POST"])
def query():
    data = request.json
    user_input = data.get("query", "")
    kind, result = handle_query(user_input, df)
    return jsonify({"response": result})

if __name__ == "__main__":
    app.run(debug=True)
