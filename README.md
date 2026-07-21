# TQNN Fault-Tolerant Inference API

Commercial fault-tolerant inference infrastructure from **TQNN Labs**.

TQNN provides a managed cloud runtime for confidence-aware inference when data may be noisy, incomplete, corrupted, or unreliable.

Developers can access the platform through the REST API or the official Python SDK without managing specialized AI infrastructure or quantum hardware.

---

# Platform Overview

The TQNN API provides one hosted interface for running inference across multiple forms of structured numerical data.

Every response includes far more than a prediction.

The platform returns:

- Prediction results
- Confidence scoring
- Confidence margins
- Normalized entropy
- Input-integrity measurements
- Missing-value diagnostics
- Constant-input detection
- Decision thresholds
- Acceptance or review status
- Runtime diagnostics

The underlying execution substrate, orchestration system, inference architecture, and production infrastructure are privately managed by TQNN Labs.

---

# Core Capability

TQNN is designed for:

> **Fault-tolerant, confidence-aware inference under imperfect data conditions.**

Rather than simply returning a prediction, the runtime evaluates both the prediction itself and the integrity of the supplied input before producing a controlled decision.

Applications can distinguish between:

- High-confidence accepted predictions
- Predictions requiring review
- Inputs containing missing values
- Constant or low-information inputs
- Results that fail acceptance thresholds

---

# Supported Modes

The public API currently supports:

- ANY
- TABULAR
- EEG
- FINANCE
- IMAGE

## ANY Mode

`ANY` is the default general-purpose mode.

It accepts structured numerical data and routes it through the platform's domain-agnostic inference pipeline.

Domain-specific modes are available when additional context is known.

---

# Cloud Runtime

The TQNN runtime is fully managed and hosted by TQNN Labs.

Applications can connect from virtually any device capable of making HTTPS requests, including:

- Desktop applications
- Cloud services
- Mobile applications
- Embedded systems
- Research notebooks
- Backend services
- Automation pipelines

No local AI or quantum hardware is required.

---

# Installation

```bash
pip install tqnn
```

---

# Python Quick Start

```python
from tqnn import TQNNClient

client = TQNNClient(
    api_key="TQNN_xxxxxxxxxxxxxxxxx"
)

result = client.run_any(
    data=[1,2,3,4],
    mode="ANY",
    task="classification",
    label="example"
)

print(result)
```

The SDK automatically connects to the managed TQNN cloud runtime.

---

# REST API

## Endpoint

```
POST /run/any
```

## Authentication

Every request requires a valid API key.

```
x-api-key: TQNN_xxxxxxxxxxxxxxxxx
```

---

# Request Example

```bash
curl -X POST "https://YOUR_API_ENDPOINT/run/any" \
  -H "Content-Type: application/json" \
  -H "x-api-key: TQNN_xxxxxxxxxxxxxxxxx" \
  -d '{
    "data":[1,2,3,4],
    "mode":"ANY",
    "task":"classification",
    "label":"example",
    "metadata":{
        "source":"curl-demo"
    }
}'
```

---

# Request Schema

```json
{
  "data":[1,2,3,4],
  "mode":"ANY",
  "task":"classification",
  "label":"example",
  "sfreq":null,
  "metadata":{}
}
```

---

# Example Response

```json
{
  "platform":"TQNN",
  "engine":"TQNN Fault-Tolerant Inference Engine",
  "engine_version":"2.0.0",
  "mode":"ANY",
  "task":"classification",
  "label":"example",

  "result":{
      "prediction_index":2,
      "prediction_label":"class_2",
      "confidence":0.947,
      "decision":"ACCEPT"
  },

  "tqnn_report":{
      "primary_capability":"fault-tolerant inference",
      "task":"classification",
      "inference_mode":"ANY",

      "confidence":{
          "score":0.947,
          "label":"high",
          "margin":0.284,
          "entropy":0.173
      },

      "data_integrity":{
          "score":1.0,
          "label":"valid",
          "feature_count":4,
          "finite_fraction":1.0,
          "missing_fraction":0.0,
          "constant_input":false
      },

      "decision":{
          "status":"ACCEPT",
          "threshold_met":true
      },

      "warnings":[]
  },

  "diagnostics":{
      "probabilities":[0.031,0.022,0.947],
      "acceptance_threshold":0.61,
      "threshold_met":true,
      "confidence_margin":0.284,
      "normalized_entropy":0.173,
      "qualia":{},
      "intent":[],
      "meta":{}
  }
}
```

*Example values shown above are illustrative.*

---

# Response Contract

Every successful inference response contains:

```
platform
engine
engine_version
mode
task
result
tqnn_report
diagnostics
```

---

# Controlled Decisions

TQNN evaluates whether an inference result satisfies the configured acceptance threshold.

Possible decision states include:

```
ACCEPT
REVIEW
REJECT
```

Applications should use the returned decision status rather than relying solely on the highest predicted probability.

---

# Input Integrity

The runtime validates numerical inputs before execution.

Integrity reporting can identify:

- Missing values
- Non-finite values
- Constant inputs
- Low-information inputs
- Unsupported structures
- Invalid runtime modes

---

# API Keys & Usage

API keys are issued automatically after subscription.

Usage is tracked according to the active subscription tier.

Each key maintains:

- Usage count
- Monthly quota
- Subscription status
- Customer account
- Billing tier
- Last-used timestamp
- Active status

---

# Subscription Plans

## Starter

**CA$23.99/month**

10,000 API calls/month

---

## Builder

**CA$79.99/month**

50,000 API calls/month

---

## Scale

**CA$249.99/month**

200,000 API calls/month

Sign up at:

https://tqnnlabs.com

---

# Runtime Status

- Managed cloud runtime
- API key authentication
- Usage metering
- Confidence-aware inference
- Input-integrity reporting
- Controlled decision logic
- Hosted production infrastructure
- End-to-end runtime operational

---

# Official Python SDK

Install from PyPI:

```bash
pip install tqnn
```

The SDK includes:

- Python client
- API interface
- Client utilities
- Response models
- Example integrations
- Public documentation

---

# Public Repository Includes

- Python SDK
- REST API interface
- Client utilities
- Public request/response contracts
- Sample integrations
- Documentation

---

# Proprietary Components

The following remain proprietary intellectual property of TQNN Labs:

- Internal inference substrate
- Quantum circuit implementations
- Private execution runtime
- Production orchestration
- Runtime optimization
- Deployment infrastructure
- Monitoring systems
- Billing infrastructure

---

# Security

The platform uses:

- API key authentication
- HTTPS encrypted communication
- Managed cloud execution
- Usage metering
- Runtime isolation
- Private production infrastructure

Use environment variables whenever possible:

```bash
export TQNN_API_KEY="TQNN_xxxxxxxxxxxxxxxxx"
```

```python
import os

from tqnn import TQNNClient

client = TQNNClient(
    api_key=os.environ["TQNN_API_KEY"]
)
```

---

# Licensing

The MIT License applies to:

- Python SDK
- Client libraries
- Integration utilities
- Examples

The managed TQNN runtime, inference substrate, execution engine, and production infrastructure remain proprietary intellectual property of TQNN Labs.

---

# Enterprise

For enterprise licensing, commercial partnerships, research collaborations, custom integrations, or deployment inquiries:

tqnnlabs@gmail.com

---

# About TQNN Labs

TQNN Labs develops cloud-hosted fault-tolerant inference infrastructure for applications operating on noisy, incomplete, or unreliable data.

The platform combines:

- Domain-agnostic data encoding
- Hybrid quantum-classical execution
- Confidence-aware inference
- Input-integrity reporting
- Controlled decision logic
- Managed cloud delivery

Website:

https://tqnnlabs.com

Built in Canada 🇨🇦

---

# Vision

TQNN Labs is building inference infrastructure that does more than return predictions.

The goal is to help applications understand:

- What the model predicted
- How confident the result is
- Whether the input can be trusted
- Whether the decision threshold was met
- When a result should be accepted, reviewed, or rejected

> **Reliable inference should not disappear when real-world data becomes imperfect.**

## Build once. Infer through uncertainty.