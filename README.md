# Infrastructure DevOps — Master DSBD & IA

> Projet du module DevOps | Encadrant : Pr. F. Benabbou
> Faculté des Sciences Ben M'Sick — Université Hassan II de Casablanca

## Description

Ce projet met en place une infrastructure DevOps complète sur Microsoft Azure permettant de déployer automatiquement une application conteneurisée via une chaîne CI/CD entièrement automatisée, incluant des tests unitaires automatiques et un système de monitoring avec Grafana.

## Architecture
``````
PC Local (Windows)
    │
    ├── Terraform ──────────► Microsoft Azure
    │                              ├── VM k8s-master (68.221.161.55)
    │                              └── VM k8s-worker (20.251.155.11)
    │
    ├── Ansible ────────────► Installation Docker + Kubernetes sur les VMs
    │
    └── Git push ──────────► GitHub
                                 └── GitHub Actions (CI/CD — 27s)
                                         ├── Install dependencies
                                         ├── Run tests (29 tests pytest)
                                         ├── Build image Docker
                                         ├── Push → DockerHub
                                         └── Deploy → Kubernetes
``````

## Technologies Utilisées

| Outil | Rôle | Version |
|-------|------|---------|
| Microsoft Azure | Cloud provider — hébergement VMs | Azure for Students |
| Terraform | Infrastructure as Code | v1.14.7 |
| Azure CLI | Interface ligne de commande Azure | v2.84.0 |
| Ansible | Configuration automatique des serveurs | YAML Playbooks |
| Docker | Conteneurisation de l'application | v29.3.0 |
| Kubernetes (k3s) | Orchestration des conteneurs | v1.34.5+k3s1 |
| Python Flask | API REST + Interface Web | 3.11-slim |
| GitHub Actions | Pipeline CI/CD automatisé | YAML Workflow |
| DockerHub | Registre d'images Docker | Public |
| Grafana | Dashboard de monitoring | NodePort 30300 |
| Helm | Gestionnaire de packages Kubernetes | v3.20.1 |
| pytest | Tests unitaires automatisés | 29 tests |

## Structure du Projet
``````
devops-master/
├── .github/
│   └── workflows/
│       └── deploy.yml        # Pipeline CI/CD GitHub Actions
├── app/
│   ├── app.py                # Application Flask (API REST + Interface HTML)
│   ├── requirements.txt      # Dépendances Python
│   └── tests/
│       └── test_app.py       # 29 tests unitaires pytest
├── k8s/
│   ├── deployment.yml        # Manifest Kubernetes Deployment (2 replicas)
│   └── service.yml           # Manifest Kubernetes Service (NodePort 30080)
├── ansible/
│   ├── inventory.ini         # Inventaire des hôtes (master + worker)
│   ├── install_docker.yml    # Playbook installation Docker
│   └── install_k8s.yml       # Playbook installation Kubernetes
├── terraform/
│   ├── main.tf               # Ressources Azure (VMs, réseau, NSG)
│   ├── variables.tf          # Déclaration des variables
│   ├── provider.tf           # Configuration du provider Azure
│   └── outputs.tf            # Sorties (IPs des VMs)
├── Dockerfile                # Image Docker de l'application
├── .gitignore
└── README.md
``````

## Application

L'application est un gestionnaire de tâches full-stack développé avec Python Flask.
Elle expose une API REST complète et une interface web intégrée accessible depuis le navigateur.

### Endpoints API

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | /health | Health check (utilisé par Kubernetes) |
| GET | / | Interface web HTML |
| GET | /tasks | Liste toutes les tâches |
| GET | /tasks/<id> | Récupère une tâche par ID |
| POST | /tasks | Crée une nouvelle tâche |
| PUT | /tasks/<id> | Met à jour une tâche |
| DELETE | /tasks/<id> | Supprime une tâche |


## Pipeline CI/CD

Le pipeline se déclenche automatiquement à chaque ``git push`` sur la branche ``main`` :

1. **Checkout code** — Récupération du code source
2. **Install dependencies** — Installation de Flask et pytest
3. **Run tests** — Exécution des 29 tests unitaires (pytest)
4. **Build Docker image** — Construction depuis le Dockerfile
5. **Push DockerHub** — Publication sur ``salama12/devops-app:latest``
6. **Deploy Kubernetes** — SSH vers le master + ``kubectl rollout restart``

Durée totale : **~27 secondes** ✅

## Tests Unitaires

29 tests automatisés couvrant tous les endpoints de l'API :
``````bash
cd app && pytest tests/ -v
``````

- Routes : /, /health, /tasks, /tasks/<id>
- Opérations : GET, POST, PUT, DELETE
- Cas d'erreur : 404, 400, 415

## Monitoring

Grafana déployé via Helm sur le cluster Kubernetes :
``````bash
helm install grafana grafana/grafana --namespace monitoring --create-namespace
``````

Accès au dashboard :
``````
http://20.251.155.11:30300
Login : admin
``````

## Infrastructure Azure

- **VM Master** : k8s-master — IP 68.221.161.55 — Spain Central — Standard_B2s
- **VM Worker** : k8s-worker — IP 20.251.155.11 — Norway East — Standard_B2s
- **OS** : Ubuntu Server 22.04 LTS x64
- **Cluster** : Kubernetes v1.34.5+k3s1 — 2 nœuds Ready
- **Pods** : 2 replicas Running dans le namespace devops-app

## Prérequis pour Reproduire

1. Compte Microsoft Azure (ou Azure for Students)
2. Terraform v1.14.7+
3. Azure CLI v2.84.0+
4. Compte DockerHub
5. Compte GitHub avec Actions activé
6. Helm v3+

## Reproduction de l'Infrastructure
``````bash
# 1. Cloner le dépôt
git clone https://github.com/malikachaaban/devops-master.git

# 2. Déployer l'infrastructure
cd terraform && terraform init && terraform apply

# 3. Configurer les machines
ansible-playbook -i ansible/inventory.ini ansible/install_docker.yml
ansible-playbook -i ansible/inventory.ini ansible/install_k8s.yml

# 4. Initialiser le cluster (master)
sudo kubeadm init --pod-network-cidr=192.168.0.0/16

# 5. Joindre le worker
sudo kubeadm join <MASTER_IP>:6443 --token <TOKEN> --discovery-token-ca-cert-hash <HASH>

# 6. Déployer l'application
kubectl apply -f k8s/

# 7. Accéder à l'application
curl http://<IP_WORKER>:30080/health
``````

## Auteurs

- **Salama Boussaid**
- **Malika Chaaban**

## Encadrant

**Pr. F. Benabbou** — Faculté des Sciences Ben M'Sick, Université Hassan II de Casablanca

---
*Master DSBD & Intelligence Artificielle — Module DevOps — 2025/2026*
