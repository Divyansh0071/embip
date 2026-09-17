# Infrastructure & Deployment (`infrastructure/`)

This directory contains container configurations, deployment manifests, and CI/CD pipelines.

## Directory Structure

```
infrastructure/
├── docker/     # Dockerfiles for FastAPI backend and environment services
├── deployment/ # Deployment manifests and cloud deployment scripts (Vercel / GCP / AWS)
├── cicd/       # GitHub Actions CI/CD workflows and automated pipelines
└── README.md   # Documentation
```

## Implementation Plan
* **Phase 19 (Deployment):** Packaging FastAPI into Docker containers, configuring Vercel environment variables, and establishing CI/CD deployment verification.
