import os
import random

import yaml
from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Opens path to current file where the config is found, loads connfig
PATH = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(PATH, "../config.yml"), "r") as f:
    config = yaml.safe_load(f)

URL = config["APP"]["url"]
BACKEND_PORT = config["APP"]["backend_port"]


# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory("frontend/public", "index.html")


# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory("frontend/public", path)


@app.route("/rand")
def hello():
    return str(random.randint(0, 100))


if __name__ == "__main__":
    app.run(host=URL, port=BACKEND_PORT, debug=True, use_reloader=False)
