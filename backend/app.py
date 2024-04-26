import os
import random

import torch
import yaml
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from src.attention import get_attention_matrices
from src.functional import detensorize_objects
from src.models import ModelandTokenizer

###################### INITIALIZATION ######################
app = Flask(__name__)
CORS(app)
MODEL_LOCKED = False

# Opens path to current file where the config is found, loads connfig
PATH = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(PATH, "../config.yml"), "r") as f:
    config = yaml.safe_load(f)

URL = config["APP"]["backend_url"]
BACKEND_PORT = config["APP"]["backend_port"]

MODEL_NAME = config["model"]

MT = ModelandTokenizer(model_path=MODEL_NAME, torch_dtype=torch.float32)

###############################################################


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


def pool_for_attention_info(prompt):
    global MODEL_LOCKED
    while True:
        if MODEL_LOCKED == True:
            print(f"prompt={prompt[:min(len(prompt), 80)]}... is waiting for model")
            continue
        else:
            MODEL_LOCKED = True
            print(f"Processing request: {prompt[:min(len(prompt), 80)]}")
            attention_information = get_attention_matrices(
                prompt=prompt,
                mt=MT,
            )
            MODEL_LOCKED = False
            return attention_information


@app.route("/attnmatrix")
def attnmatrix():
    prompt = request.args.get("prompt")
    print(f"{prompt=}")

    # attention_information = get_attention_matrices(
    #     prompt=prompt,
    #     mt=MT,
    # )
    attention_information = pool_for_attention_info(prompt)

    attention_information = detensorize_objects(attention_information)
    return jsonify(attention_information.to_dict())


if __name__ == "__main__":
    print(f"host={URL}, port={BACKEND_PORT}")
    app.run(host=URL, port=BACKEND_PORT, debug=True, use_reloader=False)
