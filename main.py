import playwright.sync_api
import requests
import flask
import os

def setup_solver():
    if not os.path.exists("utils"): os.mkdir("utils")
    files = [
        "https://raw.githubusercontent.com/Body-Alhoha/turnaround/main/utils/solver.py",
        "https://raw.githubusercontent.com/Body-Alhoha/turnaround/main/utils/page.html"
    ]
    for file in files:
        r = requests.get(file).text
        with open("utils/" + file.split("/")[-1], "w") as f:
            f.write(r)

setup_solver()
app = flask.Flask(__name__)
from utils import solver

@app.route("/")
def index():
    return flask.redirect("https://github.com/Euro-pol/turnaround-api")

@app.route("/health")
def health():
    return {"status": "healthy"}

@app.route("/solve", methods=["POST"])
def solve():
    json_data = flask.request.json
    sitekey = json_data["sitekey"]
    invisible = json_data["invisible"]
    url = json_data["url"]
    proxy = json_data.get('proxy')
    
    with playwright.sync_api.sync_playwright() as p:
        s = solver.Solver(p, proxy=proxy, headless=True)
        token = s.solve(url, sitekey, invisible)
        s.terminate()
        return flask.jsonify({
            "status": "success" if token != "failed" else "error",
            "token": token if token != "failed" else None
        })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)