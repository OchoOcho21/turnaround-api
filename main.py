import playwright.sync_api
import requests
import flask
import os
import time
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_browsers():
    """Ensure all browsers are properly installed"""
    try:
        with playwright.sync_api.sync_playwright() as p:
            for browser_type in [p.chromium, p.firefox, p.webkit]:
                try:
                    browser = browser_type.launch(headless=True)
                    version = browser.version
                    browser.close()
                    logger.info(f"{browser_type.name} verified (v{version})")
                except Exception as e:
                    logger.error(f"Browser {browser_type.name} failed: {str(e)}")
                    raise RuntimeError(f"Browser {browser_type.name} not functional")
        return True
    except Exception as e:
        logger.critical(f"Browser verification failed: {str(e)}")
        return False

def setup_solver():
    if not os.path.exists("utils"):
        os.mkdir("utils")
    
    files = [
        ("solver.py", "https://raw.githubusercontent.com/Body-Alhoha/turnaround/main/utils/solver.py"),
        ("page.html", "https://raw.githubusercontent.com/Body-Alhoha/turnaround/main/utils/page.html")
    ]
    
    for filename, url in files:
        try:
            if not os.path.exists(f"utils/{filename}"):
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                with open(f"utils/{filename}", "w") as f:
                    f.write(r.text)
        except Exception as e:
            logger.error(f"Failed to download {filename}: {str(e)}")
            if not os.path.exists(f"utils/{filename}"):
                raise RuntimeError(f"Critical file {filename} missing")

# Initialize
setup_solver()
if not verify_browsers():
    raise RuntimeError("Browser verification failed - check Dockerfile installation")

app = flask.Flask(__name__)
from utils import solver

@app.route("/")
def index():
    return flask.redirect("https://github.com/Euro-pol/turnaround-api")

@app.route("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "browsers": ["chromium", "firefox", "webkit"]
    }

@app.route("/solve", methods=["POST"])
def solve_captcha():
    start_time = time.time()
    
    if not flask.request.is_json:
        return flask.jsonify({
            "status": "error",
            "message": "Content-Type must be application/json",
            "time_elapsed": round(time.time() - start_time, 2)
        }), 400
    
    try:
        data = flask.request.get_json()
        required = ["sitekey", "url", "invisible"]
        if not all(k in data for k in required):
            return flask.jsonify({
                "status": "error",
                "message": f"Missing required fields: {required}",
                "time_elapsed": round(time.time() - start_time, 2)
            }), 400
        
        logger.info(f"Solving captcha for {data['url']}")
        
        with playwright.sync_api.sync_playwright() as p:
            # Force chromium if others fail
            browser_type = p.chromium
            captcha_solver = solver.Solver(
                p,
                browser_type=browser_type,
                proxy=data.get('proxy'),
                headless=True
            )
            
            try:
                token = captcha_solver.solve(
                    data['url'],
                    data['sitekey'],
                    data['invisible']
                )
                
                return flask.jsonify({
                    "status": "success" if token != "failed" else "error",
                    "token": token if token != "failed" else None,
                    "browser": browser_type.name,
                    "time_elapsed": round(time.time() - start_time, 2)
                })
                
            finally:
                captcha_solver.terminate()
                
    except Exception as e:
        logger.error(f"Captcha solve error: {str(e)}", exc_info=True)
        return flask.jsonify({
            "status": "error",
            "message": str(e),
            "time_elapsed": round(time.time() - start_time, 2)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)