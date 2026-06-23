from flask import Flask, request, jsonify, render_template

from .classifier import classify_image
from .stats      import tracker
from .database   import save_classification, get_recent, get_counts, delete_all, delete_by_id


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

    @app.route("/admin")
    def admin():
        """Serve the admin database viewer page."""
        counts  = get_counts()
        history = get_recent(100)
        return render_template("admin.html", counts=counts, history=history)

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

    @app.route("/delete-history", methods=["POST"])
    def delete_history():
        """Delete all classification history from database."""
        delete_all()
        tracker.reset()  # reset in-memory stats too
        return jsonify({"success": True, "message": "All history deleted"})

    @app.route("/delete-record/<int:record_id>", methods=["POST"])
    def delete_record(record_id):
        """Delete a single record by ID."""
        try:
            delete_by_id(record_id)
            return jsonify({"success": True, "message": f"Record {record_id} deleted"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400