# System Architecture

```mermaid
graph TB
    subgraph "External Systems"
        RZP[Razorpay Payment Gateway]
        MERCHANT[Merchant Store]
        CUSTOMER[Customer Browser]
    end

    subgraph "AI Risk Manager"
        subgraph "Ingestion Layer"
            WEBHOOK[Webhook Handler]
            API[REST API]
        end

        subgraph "Processing Layer"
            RULES[Rules Engine<br/>18 Heuristics<br/>&lt;50ms]
            ML[ML Models<br/>XGBoost/RF/LR<br/>&lt;200ms]
        end

        subgraph "Scoring Engines"
            FRAUD[Fraud Detector<br/>XGBoost]
            CHARGEBACK[Chargeback Predictor<br/>Random Forest]
            RETURN[Return Fraud Classifier<br/>Logistic Regression]
        end

        subgraph "Action Engine"
            DECISION[Decision Logic<br/>Confidence-Based]
            ACTION[Action Executor<br/>ALERT/FLAG/HOLD/EVIDENCE]
        end

        subgraph "Data Layer"
            POSTGRES[(PostgreSQL<br/>Transactions<br/>Risk Scores<br/>Audit Trail)]
            REDIS[(Redis Cache<br/>ML Predictions<br/>Session Data)]
        end

        subgraph "Presentation Layer"
            DASHBOARD[React Dashboard<br/>Real-time Monitoring]
            WEBSOCKET[WebSocket Server<br/>Live Updates]
        end
    end

    %% Flow: Transaction Processing
    RZP -->|payment.authorized| WEBHOOK
    WEBHOOK --> RULES
    RULES --> ML
    ML --> FRAUD
    ML --> CHARGEBACK
    ML --> RETURN
    
    FRAUD --> DECISION
    CHARGEBACK --> DECISION
    RETURN --> DECISION
    
    DECISION --> ACTION
    ACTION --> POSTGRES
    ACTION --> REDIS
    
    %% Flow: Dashboard
    MERCHANT --> DASHBOARD
    DASHBOARD <-->|Real-time| WEBSOCKET
    WEBSOCKET --> REDIS
    POSTGRES --> DASHBOARD
    
    %% API Access
    MERCHANT -->|/api/v1/risk/score| API
    API --> RULES
    
    %% Styling
    classDef external fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef ingestion fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef processing fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef scoring fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef action fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef data fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    classDef presentation fill:#fff9c4,stroke:#f57f17,stroke-width:2px

    class RZP,MERCHANT,CUSTOMER external
    class WEBHOOK,API ingestion
    class RULES,ML processing
    class FRAUD,CHARGEBACK,RETURN scoring
    class DECISION,ACTION action
    class POSTGRES,REDIS data
    class DASHBOARD,WEBSOCKET presentation
```

## Key Components

### 1. Ingestion Layer
- **Webhook Handler**: Processes Razorpay payment events in real-time
- **REST API**: Synchronous risk scoring endpoint for checkout integration

### 2. Processing Layer
- **Rules Engine**: 18 deterministic heuristics (<50ms latency)
  - Fraud rules: velocity, geolocation, device fingerprint, BIN risk, time anomaly
  - Chargeback rules: high-value first txn, quick returns, tracking behavior
  - Return fraud rules: wardrobing, serial returner patterns
- **ML Models**: Probabilistic scoring (<200ms latency)
  - Cached predictions in Redis for sub-10ms lookups

### 3. Scoring Engines (Modular)
- **Fraud Detector**: XGBoost (70% recall @ 0.5% FPR)
- **Chargeback Predictor**: Random Forest (60% chargeback prevention)
- **Return Fraud Classifier**: Logistic Regression (80% recall on patterns)

### 4. Action Engine
- **Decision Logic**: Confidence-based bucketing (high/medium/low)
- **Action Executor**: ALERT → FLAG → HOLD → AUTO-EVIDENCE modes

### 5. Data Layer
- **PostgreSQL**: Persistent storage for transactions, scores, audit trail
- **Redis**: ML model cache, session management, real-time queues

### 6. Presentation Layer
- **React Dashboard**: Merchant-facing UI with real-time transaction feeds
- **WebSocket**: Live updates for instant risk score visibility

## Latency Targets

| Component | Target | Why |
|-----------|--------|-----|
| Rules Engine | <50ms | Synchronous checkout integration |
| ML Inference | <200ms | Acceptable for risk scoring |
| End-to-End API | <250ms p99 | Doesn't slow down payment flow |
| Dashboard Updates | <1s | Real-time merchant visibility |

## Scale Targets

- **Throughput**: 500 TPS (matches Razorpay scale)
- **Daily Volume**: 35M transactions
- **False-Positive Rate**: <0.5% (17,500 incorrect flags/day max)
- **Availability**: 99.9% uptime target
