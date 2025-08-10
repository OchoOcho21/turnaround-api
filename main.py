import asyncio
import requests
import quart
import json
import time
import os
import pyppeteer

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
app = quart.Quart(__name__)
from utils.solver import Solver

async def solve_captcha(url, sitekey, invisible, proxy=None):
    solver = Solver(proxy=proxy, headless=True)
    try:
        start_time = time.time()
        print(f'Solving captcha with proxy: {proxy}')
        token = await solver.solve(url, sitekey, invisible)
        print(f"took {time.time() - start_time} seconds :: {token[:10]}")
        return token
    finally:
        await solver.terminate()

@app.route("/")
async def index():
    return quart.redirect("https://github.com/OchoOcho21/turnaround-api")

@app.route("/solve", methods=["POST"])
async def solve():
    json_data = await quart.request.get_json()
    sitekey = json_data["sitekey"]
    invisible = json_data["invisible"]
    url = json_data["url"]
    proxy = json_data.get('proxy')
    
    token = await solve_captcha(url, sitekey, invisible, proxy)
    return await make_response(token)

async def make_response(captcha_key):
    if captcha_key == "failed":
        return quart.jsonify({"status": "error", "token": None})
    return quart.jsonify({"status": "success", "token": captcha_key})

if __name__ == "__main__":
    port = 12019
    app.run(host='0.0.0.0', port=port)