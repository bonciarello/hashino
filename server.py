#!/usr/bin/env python3
"""Hashino — Calcolatore di checksum e hash per file e testo incollato."""

import hashlib
import os
from flask import Flask, request, jsonify, send_from_directory, render_template

app = Flask(__name__, template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = 110 * 1024 * 1024  # 110 MB

ALGORITHMS = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
}


def compute_hashes(data: bytes, algorithms: list[str]) -> dict[str, str]:
    """Compute requested hashes for the given data."""
    results = {}
    for alg in algorithms:
        if alg in ALGORITHMS:
            h = ALGORITHMS[alg]()
            h.update(data)
            results[alg] = h.hexdigest()
    return results


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt")


@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory("static", "sitemap.xml")


@app.route("/api/hash", methods=["POST"])
def api_hash():
    algorithms = request.form.getlist("algorithms")
    if not algorithms:
        algorithms = ["sha256"]

    # Validate algorithms
    valid_algs = [a for a in algorithms if a in ALGORITHMS]
    if not valid_algs:
        return jsonify({"error": "Nessun algoritmo valido specificato"}), 400

    data = None

    # Check for file upload
    if "file" in request.files:
        f = request.files["file"]
        if f and f.filename:
            data = f.read()
            if not data:
                return jsonify({"error": "Il file è vuoto"}), 400

    # Check for text input
    if data is None:
        text = request.form.get("text", "")
        if not text:
            return jsonify({"error": "Fornisci un testo o carica un file"}), 400
        data = text.encode("utf-8")

    try:
        hashes = compute_hashes(data, valid_algs)
        return jsonify({"hashes": hashes, "size_bytes": len(data)})
    except Exception as e:
        return jsonify({"error": f"Errore nel calcolo: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4601))
    app.run(host="0.0.0.0", port=port, debug=False)
