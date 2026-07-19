# TQNN API — Developer Guide

Welcome to the TQNN API.

The TQNN API provides a unified interface for confidence-aware inference across structured data.

Rather than returning only predictions, every inference includes a standardized **TQNN Report** describing confidence, observable input integrity, decision status, and diagnostics.

This guide explains how to integrate with the API using:

- The official Python SDK
- Direct HTTP requests
- Mode-specific payloads
- Standardized API responses

---

# Protected Runtime

> **Notice**
>
> The TQNN Core Runtime is proprietary technology owned by TQNN Labs.
>
> This documentation describes the public API only. It does not expose or imply implementation details of the underlying inference runtime.

---

# Authentication

Every request requires an API key.

```text
x-api-key: YOUR_TQNN_API_KEY
```

API keys are linked to an active subscription.

Usage is metered automatically.

---

# Base URL

```text
https://api.tqnnlabs.com
```

---

# Endpoint

## Run Inference

```text
POST /run/any
```

---

# Python SDK

Install:

```bash
pip install tqnn
```

Example:

```python
from tqnn import TQNNClient

client = TQNNClient(
    api_key="YOUR_API_KEY"
)

response = client.run_any(
    data=[[1, 2, 3]],
    mode="TABULAR",
    task="fault_diagnosis",
    label="demo"
)

print(response)
```

---

# Direct HTTP Example

```http
POST /run/any
```

```json
{
  "data": [[1.2, 0.4, 3.3]],
  "mode": "TABULAR",
  "task": "fault_diagnosis",
  "label": "demo"
}
```

---

# Supported Modes

The API accepts structured numeric data.

## EEG

Typical input:

- channels × samples
- floating point values
- optional sampling frequency metadata

---

## TABULAR

Structured feature matrices.

```json
{
  "mode": "TABULAR",
  "data": [
    [1.2, 0.5, 3.1],
    [0.7, 2.0, 1.8]
  ]
}
```

---

## FINANCE

Typical inputs include:

- OHLCV
- Technical indicators
- Sliding windows
- Feature matrices

---

## IMAGE

Structured image-derived features.

Examples include:

- flattened vectors
- embedding features
- tensor-like numeric arrays

---

# Standard Response

Every inference returns a standardized response.

```json
{
  "platform": "TQNN",
  "engine": "fault_tolerant_inference",

  "result": {
    "prediction_index": 1,
    "prediction_label": "fault",
    "confidence": 0.94,
    "decision": "accept"
  },

  "tqnn_report": {

  },

  "diagnostics": {

  }
}
```

---

# Response Sections

## result

Primary prediction returned by the platform.

Includes:

- prediction
- confidence
- operational decision

---

## tqnn_report

Provides additional context including:

- confidence assessment
- observable input integrity
- decision summary
- warning messages

---

## diagnostics

Developer-oriented information including:

- confidence metrics
- entropy
- threshold evaluation
- optional runtime metadata

---

# Common Errors

## 400

Malformed request.

---

## 401

Missing or invalid API key.

---

## 422

Request validation failed.

---

## 429

Subscription quota exhausted.

---

## 500

Unexpected server error.

---

# Security

The public API intentionally exposes only the standardized inference interface.

The following remain internal:

- Runtime implementation
- Internal orchestration
- Protected inference methods
- Proprietary optimization techniques
- Deployment architecture

---

# Versioning

Current API version:

```text
v2.0.0
```

Future versions will preserve backward compatibility whenever practical.