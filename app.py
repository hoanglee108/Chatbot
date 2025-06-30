from flask import Flask, render_template, request
import pandas as pd
from utils import handle_query

app = Flask(__name__)
df = pd.read_csv("crawl/mon_ngon.csv").fillna("")

@app.route("/", methods=["GET", "POST"])
def index():
    response = None
    if request.method == "POST":
        user_input = request.form["query"]
        kind, result = handle_query(user_input, df)

        if kind == "list":
            response = {"type": "list", "data": result.to_dict(orient="records")}
        elif kind == "detail":
            response = {"type": "detail", **result}
        else:
            response = {"type": "error", "message": result}

    return render_template("index.html", response=response)

if __name__ == "__main__":
    app.run(debug=True)
