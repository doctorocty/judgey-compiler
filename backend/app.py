from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS

import os

from backend.compiler import compile_code


app = Flask(__name__)

CORS(app)


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "frontend"
)

PICTURES_DIR = os.path.join(
    BASE_DIR,
    "pictures"
)

SOUNDS_DIR = os.path.join(
    BASE_DIR,
    "sounds"
)

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


@app.route("/style.css")
def style():

    return send_from_directory(
        FRONTEND_DIR,
        "style.css"
    )


@app.route("/script.js")
def script():

    return send_from_directory(
        FRONTEND_DIR,
        "script.js"
    )

@app.route("/pictures/<path:filename>")
def pictures(filename):

    return send_from_directory(
        PICTURES_DIR,
        filename
    )


@app.route("/sounds/<path:filename>")
def sounds(filename):

    return send_from_directory(
        SOUNDS_DIR,
        filename
    )

@app.route("/compile", methods=["POST"])
def compile():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "output": "",
            "error": "No data received."
        }), 400


    language = data.get("language")

    code = data.get("code")


    if not language:

        return jsonify({
            "success": False,
            "output": "",
            "error": "No programming language selected."
        }), 400


    if code is None:

        return jsonify({
            "success": False,
            "output": "",
            "error": "No code received."
        }), 400


    result = compile_code(
        language,
        code
    )


    return jsonify(result)

if __name__ == "__main__":

    app.run(
        debug=True
    )