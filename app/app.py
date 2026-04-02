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

# ── HTML de l'interface (old fashioned theme) ──────────────────────────────
HTML_PAGE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gestionnaire des Tâches</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>
  :root {
    --paper:#f5f0e8; --paper2:#ede7d6; --paper3:#e4dcc8;
    --ink:#1a1208; --ink2:#3d2f1a; --ink3:#6b5640; --ink4:#9a8268;
    --sepia:#8b6914; --sepia2:#c49a2a;
    --crimson:#7a1c1c; --crimson2:#a33030;
    --green-old:#1a4a2a; --border:#c4a96e; --border2:#8b6914;
    --shadow:rgba(26,18,8,0.15);
  }
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
  body{background:var(--paper3);background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='4' height='4'%3E%3Crect width='4' height='4' fill='%23e4dcc8'/%3E%3Crect x='0' y='0' width='1' height='1' fill='%23d8d0bb' opacity='.4'/%3E%3C/svg%3E");color:var(--ink);font-family:'Libre Baskerville',Georgia,serif;font-size:15px;line-height:1.7;min-height:100vh;}

  .masthead{background:var(--ink);color:var(--paper);text-align:center;padding:9px 24px;font-size:11px;letter-spacing:3px;text-transform:uppercase;border-bottom:3px double var(--sepia2);}

  header{background:var(--paper);border-bottom:1px solid var(--border);box-shadow:0 2px 8px var(--shadow);}
  .header-inner{max-width:900px;margin:0 auto;padding:0 32px;display:flex;align-items:center;justify-content:space-between;height:64px;}
  .logo{font-family:'Playfair Display',serif;font-size:22px;font-weight:900;font-style:italic;color:var(--ink);display:flex;align-items:center;gap:12px;text-decoration:none;}
  .logo em{color:var(--crimson);font-style:normal;}
  .logo-seal{width:38px;height:38px;border:2px solid var(--border2);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px;font-style:normal;background:var(--paper2);}
  .hdr-stats{display:flex;gap:24px;}
  .hstat{text-align:center;}
  .hstat-val{display:block;font-family:'Playfair Display',serif;font-size:18px;font-weight:700;color:var(--crimson);line-height:1;}
  .hstat-lbl{font-size:10px;color:var(--ink4);text-transform:uppercase;letter-spacing:1px;}

  .hero{background:var(--paper);border-bottom:4px double var(--border2);padding:40px 32px 32px;text-align:center;position:relative;}
  .hero::before{content:'';position:absolute;top:0;left:0;right:0;height:5px;background:repeating-linear-gradient(90deg,var(--border2) 0,var(--border2) 8px,transparent 8px,transparent 16px);}
  .hero-orn{font-size:22px;display:block;color:var(--sepia);margin-bottom:10px;letter-spacing:16px;}
  .hero h1{font-family:'Playfair Display',serif;font-size:clamp(26px,4vw,46px);font-weight:900;font-style:italic;color:var(--ink);line-height:1.1;margin-bottom:8px;}
  .hero h1 em{font-style:normal;color:var(--crimson);}
  .hero-rule{display:flex;align-items:center;justify-content:center;gap:14px;margin:12px 0;}
  .hero-rule span{height:1px;width:60px;background:var(--border2);display:block;}
  .hero p{font-size:14px;font-style:italic;color:var(--ink3);max-width:480px;margin:0 auto;}

  .main{max-width:900px;margin:36px auto;padding:0 32px;}

  .section-head{margin-bottom:22px;padding-bottom:10px;border-bottom:2px solid var(--ink);display:flex;align-items:center;justify-content:space-between;}
  .section-title{font-family:'Playfair Display',serif;font-size:22px;font-weight:700;font-style:italic;color:var(--ink);}

  /* Add form */
  .add-box{background:var(--paper);border:1px solid var(--border);padding:24px 28px;margin-bottom:32px;position:relative;}
  .add-box::before{content:'';position:absolute;inset:5px;border:1px solid var(--border);pointer-events:none;}
  .add-row{display:flex;gap:10px;align-items:flex-end;}
  .field{display:flex;flex-direction:column;gap:5px;flex:1;}
  .field label{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--ink4);font-weight:700;}
  .field input{background:var(--paper2);border:1px solid var(--border);padding:10px 14px;font-family:'Libre Baskerville',serif;font-size:13px;color:var(--ink);outline:none;transition:border-color .15s;box-shadow:inset 0 1px 3px var(--shadow);}
  .field input:focus{border-color:var(--sepia);}
  .field input::placeholder{color:var(--ink4);font-style:italic;}
  .btn-add{padding:10px 24px;background:var(--ink);color:var(--paper);border:1px solid var(--ink);font-family:'Libre Baskerville',serif;font-size:12px;text-transform:uppercase;letter-spacing:1.5px;cursor:pointer;transition:all .15s;white-space:nowrap;}
  .btn-add:hover{background:var(--crimson);border-color:var(--crimson);}

  /* Filters */
  .filters{display:flex;gap:8px;margin-bottom:22px;flex-wrap:wrap;}
  .filter-btn{padding:5px 16px;border:1px solid var(--border);background:var(--paper);color:var(--ink3);font-family:'Libre Baskerville',serif;font-size:12px;cursor:pointer;transition:all .15s;}
  .filter-btn:hover{background:var(--paper2);border-color:var(--border2);}
  .filter-btn.active{background:var(--ink);border-color:var(--ink);color:var(--paper);}
  .filter-btn.f-done.active{background:var(--green-old);border-color:var(--green-old);}
  .filter-btn.f-todo.active{background:var(--crimson);border-color:var(--crimson);}

  /* Task list */
  .tasks-list{display:flex;flex-direction:column;gap:12px;margin-bottom:48px;}

  .task-card{background:var(--paper);border:1px solid var(--border);position:relative;transition:box-shadow .2s,transform .2s;animation:fadeIn .3s both;}
  .task-card::before{content:'';position:absolute;inset:3px;border:1px solid var(--border);pointer-events:none;z-index:0;transition:border-color .2s;}
  .task-card:hover{box-shadow:4px 4px 0 var(--border2);transform:translate(-1px,-1px);}
  .task-card:hover::before{border-color:var(--border2);}
  .task-card.done-card{opacity:.7;}
  @keyframes fadeIn{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:none;}}

  .task-inner{display:flex;align-items:center;gap:14px;padding:16px 20px;position:relative;z-index:1;}

  .task-check{width:22px;height:22px;border:1px solid var(--border2);background:var(--paper2);cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:13px;transition:all .15s;}
  .task-check:hover{border-color:var(--green-old);}
  .task-check.checked{background:var(--green-old);border-color:var(--green-old);color:var(--paper);}

  .task-body{flex:1;min-width:0;}
  .task-title{font-family:'Playfair Display',serif;font-size:16px;font-weight:700;color:var(--ink);transition:all .2s;}
  .task-title.striked{text-decoration:line-through;color:var(--ink4);}
  .task-date{font-size:11px;color:var(--ink4);font-style:italic;margin-top:2px;}

  .task-status{padding:2px 10px;border:1px solid currentColor;font-size:10px;text-transform:uppercase;letter-spacing:1px;font-family:'Libre Baskerville',serif;}
  .status-todo{color:var(--crimson);}
  .status-done{color:var(--green-old);}

  .btn-del{padding:5px 14px;background:transparent;border:1px solid var(--border);color:var(--ink4);font-family:'Libre Baskerville',serif;font-size:11px;text-transform:uppercase;letter-spacing:1px;cursor:pointer;transition:all .15s;}
  .btn-del:hover{border-color:var(--crimson2);color:var(--crimson2);}

  .empty{text-align:center;padding:52px;color:var(--ink4);}
  .empty-orn{font-size:32px;display:block;color:var(--sepia);margin-bottom:12px;}
  .empty h3{font-family:'Playfair Display',serif;font-size:18px;font-style:italic;}

  .toast{position:fixed;bottom:22px;right:22px;background:var(--paper);border:1px solid var(--border);border-left:4px solid var(--sepia);padding:11px 18px;font-size:13px;font-style:italic;color:var(--ink);box-shadow:4px 4px 0 var(--border);transform:translateX(120%);opacity:0;transition:all .3s;z-index:999;max-width:280px;}
  .toast.show{transform:translateX(0);opacity:1;}
  .toast.ok{border-left-color:var(--green-old);}
  .toast.err{border-left-color:var(--crimson);}

  footer{border-top:4px double var(--border2);background:var(--paper2);text-align:center;padding:20px;color:var(--ink4);font-size:12px;font-style:italic;}
  footer strong{color:var(--ink2);font-style:normal;}

  @media(max-width:600px){
    .add-row{flex-direction:column;}
    .hdr-stats{display:none;}
    .main{padding-left:16px;padding-right:16px;}
  }
</style>
</head>
<body>

<div class="masthead">✦ &nbsp; Registre des Tâches &amp; Missions &nbsp; ✦ &nbsp; Anno MMXXVI &nbsp; ✦</div>

<header>
  <div class="header-inner">
    <a class="logo" href="/">
      <div class="logo-seal">📋</div>
      Registre <em>des Tâches</em>
    </a>
    <div class="hdr-stats">
      <div class="hstat"><span class="hstat-val" id="hs-total">—</span><span class="hstat-lbl">Total</span></div>
      <div class="hstat"><span class="hstat-val" id="hs-done">—</span><span class="hstat-lbl">Accomplies</span></div>
      <div class="hstat"><span class="hstat-val" id="hs-todo">—</span><span class="hstat-lbl">En cours</span></div>
    </div>
  </div>
</header>

<div class="hero">
  <span class="hero-orn">— ✦ —</span>
  <h1>Registre des <em>Missions</em></h1>
  <div class="hero-rule"><span></span><b>❧</b><span></span></div>
  <p>Consignez, suivez et accomplissez vos tâches avec rigueur et méthode.</p>
</div>

<div class="main">

  <div class="section-head">
    <h2 class="section-title">Inscrire une nouvelle mission</h2>
  </div>
  <div class="add-box">
    <div class="add-row">
      <div class="field">
        <label>Intitulé de la tâche *</label>
        <input type="text" id="new-title" placeholder="ex : Déployer l'application sur Kubernetes…" onkeydown="if(event.key==='Enter') addTask()">
      </div>
      <button class="btn-add" onclick="addTask()">✦ Inscrire</button>
    </div>
  </div>

  <div class="section-head">
    <h2 class="section-title">Registre des missions <small id="count-lbl" style="font-size:13px;color:var(--ink4);font-style:normal;font-family:'Libre Baskerville',serif;margin-left:10px;font-weight:400;"></small></h2>
  </div>

  <div class="filters">
    <button class="filter-btn active" data-filter="all">Toutes</button>
    <button class="filter-btn f-todo" data-filter="todo">En cours</button>
    <button class="filter-btn f-done" data-filter="done">Accomplies</button>
  </div>

  <div class="tasks-list" id="tasks-list"></div>
</div>

<footer>
  <strong>Gestionnaire de Tâches</strong> — API REST Flask sur <code>/tasks</code><br>
  <span style="font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--ink4)">✦ &nbsp; Nulla dies sine linea &nbsp; ✦</span>
</footer>

<div class="toast" id="toast"></div>

<script>
let allTasks = [];
let currentFilter = 'all';

function toast(msg, type='ok') {
  const t = document.getElementById('toast');
  t.textContent = msg; t.className = `toast ${type} show`;
  setTimeout(() => t.className='toast', 3000);
}

function updateStats() {
  const done = allTasks.filter(t => t.done).length;
  document.getElementById('hs-total').textContent = allTasks.length;
  document.getElementById('hs-done').textContent  = done;
  document.getElementById('hs-todo').textContent  = allTasks.length - done;
}

function getFiltered() {
  if (currentFilter === 'done') return allTasks.filter(t => t.done);
  if (currentFilter === 'todo') return allTasks.filter(t => !t.done);
  return allTasks;
}

function render() {
  const list = getFiltered();
  const g = document.getElementById('tasks-list');
  document.getElementById('count-lbl').textContent = `— ${list.length} tâche${list.length>1?'s':''}`;
  updateStats();

  if (!list.length) {
    g.innerHTML = `<div class="empty"><span class="empty-orn">✦</span><h3>Aucune mission enregistrée</h3></div>`;
    return;
  }

  g.innerHTML = list.map(t => `
    <div class="task-card ${t.done?'done-card':''}">
      <div class="task-inner">
        <div class="task-check ${t.done?'checked':''}" onclick="toggleTask(${t.id})">
          ${t.done ? '✓' : ''}
        </div>
        <div class="task-body">
          <div class="task-title ${t.done?'striked':''}">${t.title}</div>
          <div class="task-date">Créée le ${t.created_at}</div>
        </div>
        <span class="task-status ${t.done?'status-done':'status-todo'}">${t.done?'Accomplie':'En cours'}</span>
        <button class="btn-del" onclick="deleteTask(${t.id})">Supprimer</button>
      </div>
    </div>`).join('');
}

async function loadTasks() {
  try {
    const r = await fetch('/tasks');
    const data = await r.json();
    allTasks = data.tasks;
    render();
  } catch { toast('Erreur de chargement.', 'err'); }
}

async function addTask() {
  const input = document.getElementById('new-title');
  const title = input.value.trim();
  if (!title) { toast('Veuillez saisir un intitulé.', 'err'); return; }
  try {
    const r = await fetch('/tasks', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({title})
    });
    const task = await r.json();
    allTasks.push(task);
    input.value = '';
    render();
    toast(`« ${task.title} » inscrite au registre.`);
  } catch { toast('Erreur lors de la création.', 'err'); }
}

async function toggleTask(id) {
  const task = allTasks.find(t => t.id === id);
  if (!task) return;
  try {
    const r = await fetch(`/tasks/${id}`, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({done: !task.done})
    });
    const updated = await r.json();
    allTasks = allTasks.map(t => t.id === id ? updated : t);
    render();
    toast(updated.done ? `« ${updated.title} » accomplie !` : `« ${updated.title} » réouverte.`);
  } catch { toast('Erreur de mise à jour.', 'err'); }
}

async function deleteTask(id) {
  const task = allTasks.find(t => t.id === id);
  if (!confirm(`Supprimer « ${task?.title} » ?`)) return;
  try {
    await fetch(`/tasks/${id}`, {method: 'DELETE'});
    allTasks = allTasks.filter(t => t.id !== id);
    render();
    toast(`Tâche supprimée du registre.`);
  } catch { toast('Erreur de suppression.', 'err'); }
}

document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.filter;
    render();
  });
});

loadTasks();
</script>
</body>
</html>"""

# ── Health check (utilisé par Kubernetes pour les probes) ──────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()}), 200

# ── Route racine — sert l'interface HTML ───────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    return HTML_PAGE, 200, {"Content-Type": "text/html; charset=utf-8"}

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
