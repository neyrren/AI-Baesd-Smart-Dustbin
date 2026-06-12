from flask import Flask, request, jsonify, render_template, send_from_directory
import os

from .classifier import classify_image
from .stats      import tracker

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')

def register_routes(app: Flask) -> None:

    @app.route("/")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/static/<path:filename>")
    def static_files(filename):
        return send_from_directory(TEMPLATES_DIR, filename)

    @app.route("/stats")
    def get_stats():
        return jsonify(tracker.to_dict())

    @app.route("/classify", methods=["POST"])
    def classify():
        file_bytes = request.files["image"].read()
        result     = classify_image(file_bytes)
        tracker.record(result["result"], result["confidence"])
        print(f"Result: {result['result'].upper()} ({result['confidence']} confidence)")
        return jsonify(result)
