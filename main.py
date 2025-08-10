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
        try:
            r = requests.get(file, timeout=10)
            r.raise_for_status()
            with open("utils/" + file.split("/")[-1], "w", encoding='utf-8') as f:
                f.write(r.text)
        except Exception as e:
            print(f"Error downloading {file}: {str(e)}")

setup_solver()
app = Quart(__name__)

async def solve_captcha(url, sitekey, invisible, proxy=None):
    try:
        solver = Solver(proxy=proxy, headless=True)
        start_time = time.time()
        print(f'Solving captcha with proxy: {proxy or "No proxy"}')
        try:
            token = await solver.solve(url, sitekey, invisible)
            print(f"Success in {time.time()-start_time:.2f}s, token: {token[:10]}...")
            return token
        except Exception as solve_error:
            print(f"Solve error: {str(solve_error)}")
            return "failed"
        finally:
            await solver.terminate()
    except Exception as init_error:
        print(f"Solver initialization error: {str(init_error)}")
        return "failed"

@app.route("/")
async def index():
    return redirect("https://github.com/OchoOcho21/turnaround-api")

@app.route("/solve", methods=["POST"])
async def solve():
    try:
        json_data = await request.get_json()
        if not json_data:
            return jsonify({"status": "error", "message": "No JSON data"}), 400

        required = ["sitekey", "invisible", "url"]
        if any(field not in json_data for field in required):
            return jsonify({"status": "error", "message": "Missing fields"}), 400

        token = await solve_captcha(
            json_data["url"],
            json_data["sitekey"],
            json_data["invisible"],
            json_data.get('proxy')
        )

        response = {
            "status": "success" if token != "failed" else "error",
            "token": token if token != "failed" else None
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=12019)