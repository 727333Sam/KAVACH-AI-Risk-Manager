# AI Risk Manager for Razorpay

**Stop merchants losing money to fraud, chargebacks, and returns at scale.**

A comprehensive AI-powered risk management system for Indian e-commerce merchants using Razorpay, built for the Razorpay Buildathon Track 02: AI Risk Manager.

## Problem

At Razorpay scale (35M daily transactions, 400-500 TPS):
- **Fraud** costs merchants 0.5-1% of transaction volume
- **Chargebacks** result in 2-5% of orders being disputed
- **Return fraud** ("friendly fraud") claims 3-7% of returns as losses

A naive system that blocks 2% of legitimate transactions would incorrectly decline 7M+ transactions per day — causing customer churn and merchant loss of trust.

## Solution

**AI Risk Manager** is a modular, hybrid ML system that:

1. **Detects Real Fraud** — 70%+ recall at <0.5% false-positive rate
2. **Prevents Chargebacks** — 60%+ reduction via risk scoring + auto-evidence generation
3. **Catches Return Fraud** — 80%+ recall on serial returners and wardrobing patterns

### Key Features

- **Hybrid Scoring** — Rules-based heuristics (40%) + ML models (60%) for interpretability
- **Modular Engines** — Each merchant toggles fraud/chargeback/return detection independently
- **Graduated Actions** — ALERT → FLAG → HOLD → AUTO-EVIDENCE modes
- **False-Positive Tracking** — Real-time FPR monitoring with auto-alerts
- **Professional Dashboard** — Live transaction feeds, risk visualization, merchant configuration

## Architecture

```
Razorpay Transaction
        ↓
    ┌───────────────┐
    │  Rules Layer  │ (<50ms)
    └───────────────┘
        ↓
    ┌───────────────┐
    │  ML Models    │ (<200ms)
    └───────────────┘
        ↓
    ┌─────────────────────────────────────────┐
    │  Fraud Detector  │  Chargeback Predictor │  Return Classifier  │
    └─────────────────────────────────────────┘
        ↓
    ┌───────────────┐
    │ Action Engine │ (ALERT/FLAG/HOLD/AUTO-EVIDENCE)
    └───────────────┘
        ↓
    ┌──────────────┐
    │  Dashboard   │
    └──────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend API | Python + FastAPI |
| ML Models | scikit-learn + XGBoost |
| Database | PostgreSQL |
| Cache | Redis |
| Frontend | React + TailwindCSS + Recharts |
| Integration | Razorpay Python SDK |

## Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- Razorpay test account (free)

### Quick Start

```bash
# Clone and enter directory
cd razorpay-risk-manager

# Setup environment
cp .env.example .env
# Edit .env with your Razorpay test API keys

# Start services (PostgreSQL + Redis + Backend + Frontend)
docker-compose up -d

# Run backend migrations
docker-compose exec backend python -m alembic upgrade head

# Start development servers
docker-compose exec backend python app.py
docker-compose exec frontend npm start

# Dashboard available at http://localhost:3000
```

## Project Structure

```
razorpay-risk-manager/
├── backend/              # FastAPI server + ML engines
├── frontend/             # React dashboard
├── diagrams/             # Mermaid architecture diagrams
├── presentation/         # Demo materials
├── docker-compose.yml    # Service orchestration
└── README.md
```

## Key Metrics

| Metric | Target |
|--------|--------|
| Fraud Detection Rate | 70%+ recall @ 0.5% FPR |
| Chargeback Prevention | 60%+ reduction vs. baseline |
| Return Fraud Detection | 80%+ recall on known patterns |
| API Latency | <250ms p99 |
| False-Positive Rate | <0.5% (at Razorpay scale) |

## Implementation Timeline

- **Days 1-3:** Backend API + Rules Layer + ML Models
- **Days 4-5:** Dashboard UI + Modular Configuration
- **Days 6-7:** Dual-mode Latency + FPR Tuning + Sandbox Validation
- **Days 8-9:** Professional Diagrams + Demo Video + Presentation

## Hackathon Track

**Razorpay Buildathon 2026 — Track 02: AI Risk Manager**

Build a working detector, verifier, or auto-responder for one class of loss (fraud/chargebacks/returns) with measured precision and recall on a held-out test set. This project covers all three.

### Evaluation Criteria

- **Honest Metrics:** False-positive cost must be explicitly tracked and acceptable
- **Defense-Only:** No offensive capabilities; purely protective
- **Measurable:** Precision, recall, F1-score reported on held-out test data
- **Scalable:** Handles Razorpay's transaction volume (35M/day, 400-500 TPS)

## Next Steps

1. Initialize project repository ✓
2. Setup Docker Compose + database schema
3. Build Rules Layer (18 heuristics)
4. Generate synthetic training data
5. Train ML models
6. Implement dashboard
7. Razorpay API integration
8. E2E testing + FPR validation
9. Professional diagrams + demo video

## References

- [Razorpay API Docs](https://razorpay.com/docs/api/)
- [Razorpay Buildathon](https://razorpay.com/buildathon/)
- [AI Risk Manager Track](https://razorpay.com/buildathon/#track-02)

---

**Built for Razorpay Buildathon 2026**  
*Stop merchants losing money. Protect at scale.*
