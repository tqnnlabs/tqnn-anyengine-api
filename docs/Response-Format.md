# Response Format

Every successful inference request returns a standardized response structure.

The response is designed to provide more than a prediction by communicating confidence, observable input integrity, operational decision status, and developer diagnostics.

---

# Top-Level Structure

```json
{
  "platform": "TQNN",
  "engine": "fault_tolerant_inference",
  "engine_version": "2.0.0",

  "mode": "TABULAR",
  "task": "fault_diagnosis",

  "result": {},
  "tqnn_report": {},
  "diagnostics": {}
}
```

---

# Top-Level Fields

| Field | Description |
|---------|-------------|
| platform | Platform identifier |
| engine | Inference engine identifier |
| engine_version | Runtime version |
| mode | Requested inference mode |
| task | Application context supplied by the caller |
| result | Primary inference result |
| tqnn_report | Confidence and integrity report |
| diagnostics | Developer-oriented diagnostic information |

---

# Result

The `result` section contains the primary inference outcome.

Example:

```json
{
    "prediction_index": 1,
    "prediction_label": "fault",
    "confidence": 0.94,
    "decision": "accept"
}
```

## Fields

| Field | Description |
|---------|-------------|
| prediction_index | Numeric prediction identifier |
| prediction_label | Human-readable prediction label (when available) |
| confidence | Confidence score between 0 and 1 |
| decision | Recommended operational action |

---

# TQNN Report

The `tqnn_report` provides additional context for interpreting the prediction.

Example:

```json
{
    "primary_capability": "Fault Diagnosis",

    "confidence": {
        "score": 0.94,
        "label": "high",
        "margin": 0.72,
        "normalized_entropy": 0.18
    },

    "data_integrity": {
        "score": 0.98,
        "label": "nominal",
        "feature_count": 52,
        "finite_fraction": 1.0,
        "missing_fraction": 0.0,
        "constant_input": false
    },

    "decision": {
        "status": "accept",
        "threshold_met": true
    },

    "warnings": []
}
```

---

# Confidence

The confidence section summarizes how strongly the runtime supports the returned prediction.

| Field | Description |
|---------|-------------|
| score | Confidence score (0–1) |
| label | Low, Medium, or High confidence |
| margin | Separation between the top prediction and alternatives |
| normalized_entropy | Prediction uncertainty metric |

---

# Data Integrity

The data integrity section summarizes observable characteristics of the submitted input.

| Field | Description |
|---------|-------------|
| score | Overall integrity score |
| label | Qualitative assessment |
| feature_count | Number of processed features |
| finite_fraction | Fraction of finite numeric values |
| missing_fraction | Fraction of missing values |
| constant_input | Indicates whether the input lacks variation |

The data integrity report evaluates observable input quality. It does not diagnose the real-world cause of degraded data.

---

# Decision

The decision section summarizes the platform's recommended operational action.

Example:

```json
{
    "status": "accept",
    "threshold_met": true
}
```

Possible values:

| Decision | Meaning |
|-----------|---------|
| accept | Prediction satisfies current confidence and integrity thresholds |
| review | Additional human review is recommended |
| reject | The input is insufficient for a reliable inference |

---

# Warnings

Warnings contain informational messages generated during inference.

Example:

```json
{
    "warnings": [
        "Input contains missing values."
    ]
}
```

An empty list indicates that no warnings were generated.

---

# Diagnostics

The `diagnostics` section provides additional information intended primarily for developers and debugging.

Example:

```json
{
    "probabilities": [],
    "acceptance_threshold": 0.70,
    "threshold_met": true,
    "confidence_margin": 0.72,
    "normalized_entropy": 0.18,
    "qualia": {},
    "intent": [],
    "meta": {}
}
```

## Diagnostic Fields

| Field | Description |
|---------|-------------|
| probabilities | Prediction probability distribution |
| acceptance_threshold | Decision threshold used during inference |
| threshold_met | Indicates whether the confidence threshold was satisfied |
| confidence_margin | Margin between leading predictions |
| normalized_entropy | Prediction uncertainty metric |
| qualia | Runtime-specific diagnostic metadata |
| intent | Runtime decision metadata |
| meta | Additional implementation metadata |

---

# Response Philosophy

The TQNN API is designed to communicate more than a prediction.

Each response includes:

- The prediction itself
- Confidence information
- Observable input integrity
- Operational decision guidance
- Optional diagnostics

This standardized response format helps developers build systems that can reason about uncertainty rather than assuming perfect information.

---

# Version

Current response contract:

```text
v2.0.0
```

Future versions will preserve compatibility whenever practical. Breaking changes will be introduced through versioned API releases.