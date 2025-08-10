import asyncio
import requests
import os
import time
from utils.solver import Solver


try:
    from quart import Quart, request, jsonify, redirect
except ImportError:
    raise ImportError("Please install Quart with: pip install quart==0.18.3")

def setup_solver():
    if not os.path.exists("utils"): 
        os.mkdir("utils")
    files = [
        "https://raw.githubusercontent.com/OchoOcho21/ocho-turnstile-solver/main/utils/solver.py",
        "https://raw.githubusercontent.com/OchoOcho21/ocho-turnstile-solver/main/utils/page.html"
    ]
    for file in files:
        r = requests.get(file).text
        with open("utils/" + file.split("/")[-1], "w") as f:
            f.write(r)

setup_solver()
app = Quart(__name__)

async def solve_captcha(url, sitekey, invisible, proxy=None):
    solver = Solver(proxy=proxy, headless=True)
    try:
        start_time = time.time()
        print(f'Solving captcha with proxy: {proxy}')
        token = await solver.solve(url, sitekey, invisible)
        print(f"took {time.time() - start_time} seconds :: {token[:10]}")
        return token
    except Exception as e:
        print(f"Error solving captcha: {str(e)}")
        return "failed"
    finally:
        await solver.terminate()

@app.route("/")
async def index():
    return redirect("https://github.com/OchoOcho21/turnaround-api")

@app.route("/solve", methods=["POST"])
async def solve():
    try:
        json_data = await request.get_json()
        if not json_data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400
            
        required_fields = ["sitekey", "invisible", "url"]
        if not all(field in json_data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        token = await solve_captcha(
            json_data["url"],
            json_data["sitekey"],
            json_data["invisible"],
            json_data.get('proxy')
        )
        
        return jsonify({
            "status": "success" if token != "failed" else "error",
            "token": token if token != "failed" else None
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=12019)