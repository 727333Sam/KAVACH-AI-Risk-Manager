# Risk Decision Tree

```mermaid
graph TD
    START([New Transaction]) --> CONFIG{Which Engines<br/>Enabled?}
    
    CONFIG -->|Fraud| FRAUD_ENGINE[Fraud Detector]
    CONFIG -->|Chargeback| CB_ENGINE[Chargeback Predictor]
    CONFIG -->|Return Fraud| RETURN_ENGINE[Return Classifier]
    CONFIG -->|All Three| ALL_ENGINES[All Engines]
    
    FRAUD_ENGINE --> F_SCORE{Fraud Score}
    F_SCORE -->|>85| F_HIGH[High Risk]
    F_SCORE -->|70-85| F_MED[Medium Risk]
    F_SCORE -->|50-70| F_LOW[Low Risk]
    F_SCORE -->|<50| F_ALLOW[Allow]
    
    CB_ENGINE --> CB_SCORE{Chargeback Score}
    CB_SCORE -->|>80| CB_HIGH[High Risk]
    CB_SCORE -->|65-80| CB_MED[Medium Risk]
    CB_SCORE -->|50-65| CB_LOW[Low Risk]
    CB_SCORE -->|<50| CB_ALLOW[Allow]
    
    RETURN_ENGINE --> R_SCORE{Return Fraud Score}
    R_SCORE -->|>75| R_HIGH[High Risk]
    R_SCORE -->|60-75| R_MED[Medium Risk]
    R_SCORE -->|45-60| R_LOW[Low Risk]
    R_SCORE -->|<45| R_ALLOW[Allow]
    
    ALL_ENGINES --> COMBINED{Combined<br/>Risk Score<br/>Max of All}
    
    F_HIGH --> ACTION_HIGH
    F_MED --> ACTION_MED
    F_LOW --> ACTION_LOW
    F_ALLOW --> ACTION_ALLOW
    
    CB_HIGH --> ACTION_HIGH
    CB_MED --> ACTION_MED
    CB_LOW --> ACTION_LOW
    CB_ALLOW --> ACTION_ALLOW
    
    R_HIGH --> ACTION_HIGH
    R_MED --> ACTION_MED
    R_LOW --> ACTION_LOW
    R_ALLOW --> ACTION_ALLOW
    
    COMBINED --> ACTION_HIGH[High Risk Path]
    COMBINED --> ACTION_MED[Medium Risk Path]
    COMBINED --> ACTION_LOW[Low Risk Path]
    COMBINED --> ACTION_ALLOW[Low Risk Path]
    
    ACTION_HIGH --> CONFIDENCE{ML Confidence?}
    CONFIDENCE -->|>0.85| VERY_CONFIDENT[Very Confident<br/>False-Positive: 0.01%]
    CONFIDENCE -->|0.70-0.85| CONFIDENT[Confident<br/>False-Positive: 1-2%]
    CONFIDENCE -->|<0.70| UNCERTAIN[Uncertain<br/>Flag for Human]
    
    VERY_CONFIDENT --> MODE_CHECK{Merchant's<br/>Action Mode?}
    MODE_CHECK -->|BLOCK| BLOCK[🚫 AUTO-BLOCK<br/>Decline Transaction<br/>Notify Merchant]
    MODE_CHECK -->|HOLD| HOLD[⏸️ HOLD<br/>Authorize but Don't Capture<br/>Manual Review Required]
    MODE_CHECK -->|FLAG| FLAG[🚩 FLAG<br/>Capture + Alert Merchant<br/>5-min Review Window]
    MODE_CHECK -->|ALERT| ALERT[⚠️ ALERT<br/>Proceed Normally<br/>Dashboard Notification]
    
    CONFIDENT --> FLAG
    UNCERTAIN --> FLAG
    
    ACTION_MED --> MED_MODE{Merchant's<br/>Medium-Risk Mode?}
    MED_MODE -->|FLAG| FLAG
    MED_MODE -->|ALERT| ALERT
    MED_MODE -->|ALLOW| ALLOW[✅ ALLOW<br/>Transaction Proceeds<br/>Log for Analytics]
    
    ACTION_LOW --> ALERT
    ACTION_ALLOW --> ALLOW
    
    BLOCK --> LOG_DB[(Log to Database<br/>• Transaction details<br/>• Risk scores<br/>• Action taken<br/>• Merchant decision)]
    HOLD --> LOG_DB
    FLAG --> LOG_DB
    ALERT --> LOG_DB
    ALLOW --> LOG_DB
    
    LOG_DB --> UPDATE_DASHBOARD[Push to Dashboard<br/>via WebSocket]
    UPDATE_DASHBOARD --> FPR_TRACK{Update FPR<br/>Tracking}
    
    FPR_TRACK --> FPR_CHECK{False-Positive<br/>Rate Check}
    FPR_CHECK -->|>1% FPR| FPR_ALERT[🚨 Alert Merchant<br/>"Threshold Too Aggressive"]
    FPR_CHECK -->|>2% FPR| FPR_AUTO[⚠️ Auto-Downgrade<br/>to ALERT Mode]
    FPR_CHECK -->|<1% FPR| FPR_OK[✅ Within Tolerance]
    
    FPR_ALERT --> TUNE[Suggest Threshold<br/>Adjustment]
    FPR_AUTO --> TUNE
    FPR_OK --> MONITOR[Continue Monitoring]
    
    TUNE --> END([End])
    MONITOR --> END
    
    %% Styling
    classDef start fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    classDef engine fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef score fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef risk fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef action fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef success fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    classDef alert fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    
    class START,END start
    class FRAUD_ENGINE,CB_ENGINE,RETURN_ENGINE,ALL_ENGINES engine
    class F_SCORE,CB_SCORE,R_SCORE,COMBINED score
    class F_HIGH,F_MED,CB_HIGH,CB_MED,R_HIGH,R_MED,ACTION_HIGH,ACTION_MED risk
    class BLOCK,HOLD,FLAG,MODE_CHECK,MED_MODE action
    class ALLOW,FPR_OK,MONITOR success
    class ALERT,FPR_ALERT,FPR_AUTO,TUNE alert
```

## Decision Matrix

| Risk Score | Confidence | Default Action | False-Positive Rate | Impact |
|------------|-----------|----------------|-------------------|--------|
| **>85** | >0.85 | BLOCK | 0.01% | Transaction declined immediately |
| **>85** | 0.70-0.85 | FLAG | 1-2% | Hold for merchant review (5 min) |
| **>85** | <0.70 | FLAG | 2-3% | Hold for merchant review |
| **70-85** | Any | FLAG or ALERT | 2-5% | Merchant configuration decides |
| **50-70** | Any | ALERT | No impact | Dashboard notification only |
| **<50** | Any | ALLOW | No impact | No action, log for analytics |

## Merchant Configuration Examples

### Conservative (Minimize False Positives)
```json
{
  "fraud_action_mode": "ALERT",
  "chargeback_action_mode": "ALERT",
  "return_action_mode": "ALERT",
  "fraud_threshold": 0.90,
  "chargeback_threshold": 0.85,
  "return_fraud_threshold": 0.85
}
```
**Effect**: Only the most obvious fraud is flagged. 0.1% FPR, 60% recall.

### Balanced (Default)
```json
{
  "fraud_action_mode": "FLAG",
  "chargeback_action_mode": "ALERT",
  "return_action_mode": "ALERT",
  "fraud_threshold": 0.75,
  "chargeback_threshold": 0.65,
  "return_fraud_threshold": 0.70
}
```
**Effect**: Standard protection. 0.5% FPR, 70% recall.

### Aggressive (Maximize Protection)
```json
{
  "fraud_action_mode": "BLOCK",
  "chargeback_action_mode": "HOLD",
  "return_action_mode": "FLAG",
  "fraud_threshold": 0.60,
  "chargeback_threshold": 0.50,
  "return_fraud_threshold": 0.55
}
```
**Effect**: Maximum fraud prevention. 2% FPR, 85% recall.

## Circuit Breaker

If false-positive rate exceeds 2% across all transactions:
1. **Auto-downgrade** all engines to ALERT mode
2. **Send alert** to merchant with FPR metrics
3. **Log incident** for investigation
4. **Suggest** threshold recalibration

This prevents catastrophic over-blocking during:
- Model degradation
- Data drift
- Configuration errors
- External attack patterns that confuse the model
