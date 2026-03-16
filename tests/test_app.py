import pytest
import app as app_module
from app import app as flask_app

# ─── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_tasks():
    """
    Remet la liste des tâches à l'état initial avant chaque test.
    Indispensable car votre app.py utilise une liste globale.
    """
    app_module.tasks.clear()
    app_module.tasks.extend([
        {"id": 1, "title": "Apprendre Docker", "done": False, "created_at": "2026-03-01"},
        {"id": 2, "title": "Configurer Kubernetes", "done": False, "created_at": "2026-03-02"},
    ])
    app_module.next_id = 3
    yield
    app_module.tasks.clear()

@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()


# ─── Route racine ───────────────────────────────────────────────────────────

def test_index(client):
    r = client.get("/")
    assert r.status_code == 200
    data = r.get_json()
    assert data["message"] == "API Task Manager"
    assert data["version"] == "1.0.0"
    assert "/health" in data["endpoints"]


# ─── Health check ───────────────────────────────────────────────────────────

def test_health_status_ok(client):
    r = client.get("/health")
    assert r.status_code == 200

def test_health_retourne_status_ok(client):
    r = client.get("/health")
    assert r.get_json()["status"] == "ok"

def test_health_retourne_timestamp(client):
    r = client.get("/health")
    assert "timestamp" in r.get_json()


# ─── GET /tasks ─────────────────────────────────────────────────────────────

def test_get_tasks_retourne_200(client):
    r = client.get("/tasks")
    assert r.status_code == 200

def test_get_tasks_retourne_liste(client):
    r = client.get("/tasks")
    data = r.get_json()
    assert "tasks" in data
    assert "total" in data

def test_get_tasks_total_correct(client):
    r = client.get("/tasks")
    data = r.get_json()
    assert data["total"] == 2
    assert len(data["tasks"]) == 2

def test_get_tasks_contient_donnees_initiales(client):
    r = client.get("/tasks")
    titres = [t["title"] for t in r.get_json()["tasks"]]
    assert "Apprendre Docker" in titres
    assert "Configurer Kubernetes" in titres


# ─── GET /tasks/<id> ────────────────────────────────────────────────────────

def test_get_task_existante(client):
    r = client.get("/tasks/1")
    assert r.status_code == 200
    assert r.get_json()["id"] == 1

def test_get_task_retourne_bonne_tache(client):
    r = client.get("/tasks/2")
    data = r.get_json()
    assert data["title"] == "Configurer Kubernetes"
    assert data["done"] is False

def test_get_task_inexistante_retourne_404(client):
    r = client.get("/tasks/999")
    assert r.status_code == 404

def test_get_task_inexistante_retourne_message_erreur(client):
    r = client.get("/tasks/999")
    assert "error" in r.get_json()


# ─── POST /tasks ────────────────────────────────────────────────────────────

def test_creer_tache_retourne_201(client):
    r = client.post("/tasks", json={"title": "Nouvelle tâche"})
    assert r.status_code == 201

def test_creer_tache_retourne_la_tache(client):
    r = client.post("/tasks", json={"title": "Configurer Terraform"})
    data = r.get_json()
    assert data["title"] == "Configurer Terraform"
    assert data["done"] is False
    assert "id" in data
    assert "created_at" in data

def test_creer_tache_incremente_id(client):
    r = client.post("/tasks", json={"title": "Tâche A"})
    assert r.get_json()["id"] == 3

def test_creer_tache_apparait_dans_la_liste(client):
    client.post("/tasks", json={"title": "Tâche test"})
    r = client.get("/tasks")
    assert r.get_json()["total"] == 3

def test_creer_tache_sans_titre_retourne_400(client):
    r = client.post("/tasks", json={"done": True})
    assert r.status_code in (400, 415)

def test_creer_tache_corps_vide_retourne_400(client):
    r = client.post("/tasks", json={})
    assert r.status_code in (400, 415)

def test_creer_tache_sans_json_retourne_erreur(client):
    r = client.post("/tasks")
    assert r.status_code in (400, 415)


# ─── PUT /tasks/<id> ────────────────────────────────────────────────────────

def test_modifier_titre(client):
    r = client.put("/tasks/1", json={"title": "Docker maîtrisé"})
    assert r.status_code == 200
    assert r.get_json()["title"] == "Docker maîtrisé"

def test_modifier_done(client):
    r = client.put("/tasks/1", json={"done": True})
    assert r.status_code == 200
    assert r.get_json()["done"] is True

def test_modifier_titre_et_done(client):
    r = client.put("/tasks/1", json={"title": "Nouveau titre", "done": True})
    data = r.get_json()
    assert data["title"] == "Nouveau titre"
    assert data["done"] is True

def test_modifier_tache_inexistante_retourne_404(client):
    r = client.put("/tasks/999", json={"title": "test"})
    assert r.status_code == 404

def test_modifier_ne_change_pas_id(client):
    r = client.put("/tasks/1", json={"title": "Modifié"})
    assert r.get_json()["id"] == 1


# ─── DELETE /tasks/<id> ─────────────────────────────────────────────────────

def test_supprimer_tache_retourne_200(client):
    r = client.delete("/tasks/1")
    assert r.status_code == 200

def test_supprimer_tache_retourne_message(client):
    r = client.delete("/tasks/1")
    assert "message" in r.get_json()

def test_supprimer_tache_disparait_de_la_liste(client):
    client.delete("/tasks/1")
    r = client.get("/tasks")
    assert r.get_json()["total"] == 1

def test_supprimer_tache_inexistante_retourne_404(client):
    r = client.delete("/tasks/999")
    assert r.status_code == 404

def test_supprimer_tache_puis_get_retourne_404(client):
    client.delete("/tasks/2")
    r = client.get("/tasks/2")
    assert r.status_code == 404
