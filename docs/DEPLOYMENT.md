Deployment Architecture


GitLab Repository
        ↓
  CI/CD Pipeline
  (Tests, Build, Deploy)
        ↓
  ┌─────────────┐
  │ Google Cloud│
  │ Container   │
  │ Registry    │
  └─────────────┘
        ↓
  ┌─────────────┐
  │ Kubernetes  │
  │ (GKE)       │
  └─────────────┘
        ↓
  ┌─────────────┐
  │   Monitoring│
  │ (Cloud      │
  │  Trace &    │
  │  Logging)   │