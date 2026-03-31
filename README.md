# GenAI App Deployment Repo

This repository contains:

- FastAPI application
- Dockerfile
- Jenkins pipeline
- Kubernetes manifests for EKS deployment

## Structure

- `app/` → application code
- `k8s/` → Kubernetes manifests
- `Dockerfile` → container image build
- `Jenkinsfile` → CI/CD pipeline

## End-to-end flow

1. Developer pushes code to GitHub
2. Jenkins detects changes
3. Jenkins builds Docker image
4. Jenkins pushes image to Amazon ECR
5. Jenkins deploys app to Amazon EKS

## Local run

```bash
pip install -r app/requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
