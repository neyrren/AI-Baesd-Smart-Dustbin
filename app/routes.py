from flask import Flask, request, jsonify, render_template

from .classifier import classify_image
from .stats      import tracker
from .database   import save_classification, get_recent, get_counts


def register_routes(app: Flask) -> None:

    @app.route("/")
    def welcome():
        """Serve the welcome/landing page."""
        return render_template("welcome.html")

    @app.route("/dashboard")
    def dashboard():
        """Serve the live monitoring dashboard."""
        return render_template("dashboard.html")

    @app.route("/upload")
    def upload():
        """Serve the upload/classify page."""
        return render_template("upload.html")

    @app.route("/stats")
    def get_stats():
        """Return live in-memory stats as JSON."""
        return jsonify(tracker.to_dict())

    @app.route("/history")
    def get_history():
        """Return persistent classification history from database."""
        counts  = get_counts()
        history = get_recent(20)
        return jsonify({**counts, "history": history})

    @app.route("/classify", methods=["POST"])
    def classify():
        """Classify image, save to DB, update live stats, return result."""
        file_bytes = request.files["image"].read()
        result     = classify_image(file_bytes)

        tracker.record(result["result"], result["confidence"])
        save_classification(result["result"], result["confidence"])

        print(f"Result: {result['result'].upper()} ({result['confidence']} confidence)")
        return jsonify(result)