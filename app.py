from flask import Flask, jsonify, request
from datetime import datetime
import os

app = Flask(__name__)

# Base de données en mémoire (simple pour le projet)
tasks = [
    {"id": 1, "title": "Apprendre Docker", "done": False, "created_at": "2026-03-01"},
    {"id": 2, "title": "Configurer Kubernetes", "done": False, "created_at": "2026-03-02"},
]
next_id = 3


# ── Health check (utilisé par Kubernetes pour les probes) ──────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()}), 200


# ── Route racine ───────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "API Task Manager",
        "version": "1.0.0",
        "endpoints": ["/health", "/tasks", "/tasks/<id>"]
    }), 200


# ── GET toutes les tâches ──────────────────────────────────────────────────
@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify({"tasks": tasks, "total": len(tasks)}), 200


# ── GET une tâche par ID ───────────────────────────────────────────────────
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Tâche introuvable"}), 404
    return jsonify(task), 200


# ── POST créer une tâche ───────────────────────────────────────────────────
@app.route("/tasks", methods=["POST"])
def create_task():
    global next_id
    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({"error": "Le champ 'title' est requis"}), 400

    task = {
        "id": next_id,
        "title": data["title"],
        "done": False,
        "created_at": datetime.utcnow().strftime("%Y-%m-%d")
    }
    tasks.append(task)
    next_id += 1
    return jsonify(task), 201


# ── PUT mettre à jour une tâche ────────────────────────────────────────────
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Tâche introuvable"}), 404

    data = request.get_json()
    if "title" in data:
        task["title"] = data["title"]
    if "done" in data:
        task["done"] = data["done"]
    return jsonify(task), 200


# ── DELETE supprimer une tâche ─────────────────────────────────────────────
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Tâche introuvable"}), 404

    tasks = [t for t in tasks if t["id"] != task_id]
    return jsonify({"message": f"Tâche {task_id} supprimée"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
