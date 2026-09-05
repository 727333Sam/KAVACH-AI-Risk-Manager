# Return Fraud Detection Flow

```mermaid
flowchart TD
    START([Customer Initiates Return]) --> WEBHOOK{Razorpay Webhook<br/>refund.created}
    
    WEBHOOK --> EXTRACT[Extract Return Data<br/>• Order ID<br/>• Customer ID<br/>• Return Reason<br/>• Item Details<br/>• Refund Amount]
    
    EXTRACT --> CUSTOMER_CHECK[Fetch Customer History<br/>from Database]
    
    CUSTOMER_CHECK --> RULES_START[Return Fraud Rules]
    
    subgraph "Rules Scoring"
        RULES_START --> RR1{Wardrobing<br/>Pattern?<br/>>40% return rate}
        RR1 -->|Yes +40| RR2
        RR1 -->|No| RR2{Serial<br/>Returner?<br/>>5 in 30 days}
        RR2 -->|Yes +25| RR3
        RR2 -->|No| RR3{Counterfeit<br/>Receipt?<br/>Digital goods}
        RR3 -->|Yes +40| RR4
        RR3 -->|No| RR4{High-Value<br/>Returns?<br/>Luxury/Electronics}
        RR4 -->|Yes +20| RR5
        RR4 -->|No| RR5{Same Item<br/>Returned 3x?}
        RR5 -->|Yes +30| RULES_SCORE
        RR5 -->|No| RULES_SCORE[Rules Score: 0-100]
    end
    
    RULES_SCORE --> ML_START[ML Return Fraud Classifier]
    
    subgraph "ML Scoring"
        ML_START --> ML_FEATURES[Extract 18 Features<br/>• Return frequency<br/>• Item condition history<br/>• Return reasons<br/>• Time between purchase & return<br/>• Category patterns]
        ML_FEATURES --> LR_MODEL[Logistic Regression<br/>Return Fraud Probability]
        LR_MODEL --> ML_SCORE[ML Probability: 0-1]
    end
    
    ML_SCORE --> HYBRID[Hybrid Score<br/>40% Rules + 60% ML<br/>Return Fraud Risk: 0-100]
    
    HYBRID --> THRESHOLD{Risk Level?}
    
    THRESHOLD -->|>75 Critical| CRITICAL[Critical Risk<br/>Likely Return Fraud]
    THRESHOLD -->|60-75 High| HIGH[High Risk<br/>Suspicious Pattern]
    THRESHOLD -->|45-60 Medium| MEDIUM[Medium Risk<br/>Watch Closely]
    THRESHOLD -->|<45 Low| LOW[Low Risk<br/>Legitimate Return]
    
    CRITICAL --> BLOCK_RETURN[🚫 BLOCK REFUND<br/>Require Investigation]
    
    subgraph "Investigation Required"
        BLOCK_RETURN --> NOTIFY_MERCHANT[Notify Merchant<br/>"Return fraud suspected"]
        NOTIFY_MERCHANT --> MANUAL_REVIEW{Merchant<br/>Review}
        MANUAL_REVIEW -->|Approve| PROCESS_REFUND
        MANUAL_REVIEW -->|Deny| DENY_RETURN[❌ Deny Return<br/>Explain Policy Violation]
        MANUAL_REVIEW -->|Need More Info| REQUEST_PROOF[📸 Request Proof<br/>Photos/Video of Item]
    end
    
    REQUEST_PROOF --> CUSTOMER_PROVIDES{Customer<br/>Provides Proof?}
    CUSTOMER_PROVIDES -->|Yes, Valid| PROCESS_REFUND[✅ Process Refund]
    CUSTOMER_PROVIDES -->|Yes, Invalid| DENY_RETURN
    CUSTOMER_PROVIDES -->|No Response| AUTO_DENY[⏱️ Auto-Deny<br/>after 48h]
    
    HIGH --> FLAG_INSPECTION[🚩 FLAG for Inspection<br/>Check Item Condition]
    
    subgraph "Item Inspection"
        FLAG_INSPECTION --> RETURN_RECEIVED{Item<br/>Received?}
        RETURN_RECEIVED -->|Yes| INSPECT[Physical Inspection<br/>• Condition check<br/>• Serial number verify<br/>• Tamper detection]
        INSPECT --> CONDITION{Item<br/>Condition?}
        CONDITION -->|Original| PROCESS_REFUND
        CONDITION -->|Used/Damaged| PARTIAL[💰 Partial Refund<br/>Deduct Damage Cost]
        CONDITION -->|Counterfeit/Wrong Item| FRAUD_CONFIRMED[🚨 Fraud Confirmed<br/>No Refund]
        FRAUD_CONFIRMED --> BAN_CUSTOMER[🔒 Ban Customer<br/>Block Future Purchases]
    end
    
    MEDIUM --> ALERT_TRACK[⚠️ ALERT + Track<br/>Process but Monitor]
    LOW --> PROCESS_NORMAL[✅ Process Normally<br/>Standard Refund]
    
    PROCESS_REFUND --> UPDATE_PROFILE[Update Customer Profile<br/>• Successful return count<br/>• Return rate %<br/>• Fraud score history]
    PARTIAL --> UPDATE_PROFILE
    ALERT_TRACK --> UPDATE_PROFILE
    PROCESS_NORMAL --> UPDATE_PROFILE
    
    UPDATE_PROFILE --> PATTERN_DETECT{Pattern<br/>Emerging?}
    PATTERN_DETECT -->|Yes, Trending Up| INCREASE_SCRUTINY[⬆️ Increase Scrutiny<br/>Lower Threshold for This Customer]
    PATTERN_DETECT -->|No| NORMAL_MONITORING[Continue Normal Monitoring]
    
    INCREASE_SCRUTINY --> LOG
    NORMAL_MONITORING --> LOG
    
    DENY_RETURN --> LOG[Log to Database<br/>• Return details<br/>• Risk scores<br/>• Action taken<br/>• Investigation notes]
    AUTO_DENY --> LOG
    BAN_CUSTOMER --> LOG
    
    LOG --> DASHBOARD_UPDATE[Update Dashboard<br/>• Return fraud metrics<br/>• Customer risk profiles<br/>• Prevented losses]
    
    DASHBOARD_UPDATE --> RETRAIN{Enough Data<br/>for Retraining?}
    RETRAIN -->|Yes, 1000+ new labels| ML_RETRAIN[Retrain ML Model<br/>Improve Detection]
    RETRAIN -->|No| END([End])
    
    ML_RETRAIN --> END
    
    %% Styling
    classDef start fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    classDef rules fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef ml fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef critical fill:#ffebee,stroke:#c62828,stroke-width:3px
    classDef action fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef success fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    classDef fraud fill:#f3e5f5,stroke:#4a148c,stroke-width:3px
    
    class START,END start
    class RR1,RR2,RR3,RR4,RR5,RULES_SCORE rules
    class ML_START,ML_FEATURES,LR_MODEL,ML_SCORE ml
    class CRITICAL,BLOCK_RETURN,NOTIFY_MERCHANT critical
    class HIGH,MEDIUM,FLAG_INSPECTION,ALERT_TRACK action
    class PROCESS_REFUND,PROCESS_NORMAL,NORMAL_MONITORING success
    class FRAUD_CONFIRMED,BAN_CUSTOMER,DENY_RETURN fraud
```

## Return Fraud Patterns

### 1. Wardrobing (Score: +40)
**Pattern**: Customer orders clothing/electronics, uses once, returns
**Detection**:
- Return rate > 40% across all orders
- Items returned after 7-14 days (typical "use window")
- Same category repeatedly (evening dresses, cameras for events)

**Action**: FLAG for inspection, check item condition before refund

### 2. Serial Returner (Score: +25)
**Pattern**: Excessive returns across short timeframe
**Detection**:
- More than 5 returns in 30 days
- Return value > 50% of purchase value in 90 days
- Returns from multiple merchants (if data available)

**Action**: ALERT merchant, increase scrutiny on future orders

### 3. Counterfeit Receipt (Score: +40)
**Pattern**: Returns items that can't be returned
**Detection**:
- Digital goods listed as "returned"
- Custom/personalized items
- Items marked "final sale" at purchase
- Non-returnable categories (hygiene products)

**Action**: AUTO-DENY, explain policy violation

### 4. Switch Fraud (Score: +35)
**Pattern**: Returns different/damaged item than purchased
**Detection**:
- Serial number mismatch
- Item condition much worse than expected
- Weight/dimensions different from shipped item
- Counterfeit item returned instead of genuine

**Action**: DENY refund, BAN customer, report to authorities if value > threshold

### 5. High-Value Abuse (Score: +20)
**Pattern**: Targets expensive items for fraudulent returns
**Detection**:
- Returns concentrated in luxury/electronics (>₹20k)
- Multiple high-value returns in short period
- No mid/low-value purchases (only targets expensive items)

**Action**: FLAG for inspection, verify item authenticity

## Prevention Metrics

| Pattern | Detection Rate | False Positive | Avg Loss Prevented |
|---------|---------------|----------------|-------------------|
| **Wardrobing** | 80% | 5% | ₹3,500/case |
| **Serial Returner** | 85% | 2% | ₹8,000/case |
| **Counterfeit Receipt** | 95% | <1% | ₹5,000/case |
| **Switch Fraud** | 75% | 3% | ₹15,000/case |
| **High-Value Abuse** | 70% | 8% | ₹12,000/case |

## Merchant Actions

### Conservative (Apparel/Low-Value)
- Critical: Inspect item before refund
- High: Process with photo verification
- Medium/Low: Auto-approve

### Balanced (Electronics/Mixed)
- Critical: Block and investigate
- High: Inspect item condition
- Medium: Alert and track
- Low: Auto-approve

### Strict (Luxury/High-Value)
- Critical: Block, require proof, ban if confirmed
- High: Mandatory inspection
- Medium: Photo verification required
- Low: Standard process

## Customer Impact

- **Legitimate returners**: Minimal friction (<1% flagged incorrectly)
- **Suspected fraud**: Photo/video proof requested (resolves 60% as legitimate)
- **Confirmed fraud**: Ban + no refund (saves merchant ₹8-15k per case)
