# Infrastructure DevOps — Master DSBD & IA

> Projet du module DevOps | Encadrant : Pr. F. Benabbou
> Faculté des Sciences Ben M'Sick — Université Hassan II de Casablanca

## Description

Ce projet met en place une infrastructure DevOps complète sur Microsoft Azure permettant de déployer automatiquement une application conteneurisée via une chaîne CI/CD entièrement automatisée.

## Architecture
```
PC Local (Windows)
    │
    ├── Terraform ──────────► Microsoft Azure
    │                              ├── VM k8s-master (68.221.161.55)
    │                              └── VM k8s-worker (20.251.155.11)
    │
    └── Git push ──────────► GitHub
                                 └── GitHub Actions (CI/CD)
                                         ├── Build image Docker
                                         ├── Push → DockerHub
                                         └── Deploy → Kubernetes
```

## Technologies Utilisées

| Outil | Rôle | Version |
|-------|------|---------|
| Microsoft Azure | Cloud provider — hébergement VMs | Azure for Students |
| Terraform | Infrastructure as Code | v1.14.7 |
| Azure CLI | Interface ligne de commande Azure | v2.84.0 |
| Ansible | Configuration automatique des serveurs | YAML Playbooks |
| Docker | Conteneurisation de l'application | v29.3.0 |
| Kubernetes (k3s) | Orchestration des conteneurs | v1.34.5+k3s1 |
| Python Flask | API REST | 3.11-slim |
| GitHub Actions | Pipeline CI/CD automatisé | YAML Workflow |
| DockerHub | Registre d'images Docker | Public |

## Structure du Projet
```
devops-master/
├── .github/
│   └── workflows/
│       └── deploy.yml        # Pipeline CI/CD GitHub Actions
├── app/
│   ├── app.py                # Application Flask (API REST)
│   ├── requirements.txt      # Dépendances Python
│   └── tests/                # Tests unitaires
├── k8s/
│   ├── deployment.yml        # Manifest Kubernetes Deployment
│   └── service.yml           # Manifest Kubernetes Service (NodePort)
├── ansible/
│   ├── inventory.ini         # Inventaire des hôtes
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
```

## API REST — Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | /health | Health check (utilisé par Kubernetes) |
| GET | / | Informations de l'API |
| GET | /tasks | Liste toutes les tâches |
| GET | /tasks/<id> | Récupère une tâche par ID |
| POST | /tasks | Crée une nouvelle tâche |
| PUT | /tasks/<id> | Met à jour une tâche |
| DELETE | /tasks/<id> | Supprime une tâche |

## Pipeline CI/CD

Le pipeline se déclenche automatiquement à chaque `git push` sur la branche `main` :

1. **Login DockerHub** — Authentification avec les secrets GitHub
2. **Build Docker image** — Construction depuis le Dockerfile
3. **Push DockerHub** — Publication sur `salama12/devops-app:latest`
4. **Deploy Kubernetes** — SSH vers le master + `kubectl rollout restart`



## Infrastructure Azure

- **VM Master** : k8s-master — IP 68.221.161.55 — Spain Central — Standard_B2s
- **VM Worker** : k8s-worker — IP 20.251.155.11 — Norway East — Standard_B2s
- **OS** : Ubuntu Server 22.04 LTS x64
- **Cluster** : Kubernetes v1.34.5+k3s1 — 2 nœuds Ready

## Prérequis pour Reproduire

1. Compte Microsoft Azure (ou Azure for Students)
2. Terraform v1.14.7+
3. Azure CLI v2.84.0+
4. Compte DockerHub
5. Compte GitHub avec Actions activé

## Auteurs

- **Salama Boussaid**
- **Malika Chaaban**

## Encadrant

**Pr. F. Benabbou** — Faculté des Sciences Ben M'Sick, Université Hassan II de Casablanca

---
*Master DSBD & Intelligence Artificielle — Module DevOps — 2025/2026*
