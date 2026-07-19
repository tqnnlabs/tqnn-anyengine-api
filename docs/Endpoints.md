# Endpoints

This document describes the public endpoints exposed by the TQNN API.

Unless otherwise noted, all endpoints return JSON responses.

---

# Base URL

```text
https://api.tqnnlabs.com
```

---

# Authentication

Protected endpoints require a valid API key.

```http
x-api-key: YOUR_TQNN_API_KEY
```

---

# GET /

Returns basic API information.

## Request

```http
GET /
```

## Example Response

```json
{
  "service": "TQNN API",
  "status": "online",
  "version": "2.0.0"
}
```

---

# GET /health

Returns the current health status of the API.

This endpoint is intended for monitoring and service verification.

## Request

```http
GET /health
```

## Example Response

```json
{
  "status": "ok"
}
```

---

# POST /run/any

Runs an inference request using the TQNN Fault-Tolerant Inference Platform.

---

## Headers

```http
Content-Type: application/json

x-api-key: YOUR_API_KEY
```

---

## Request Body

```json
{
  "data": [
    [1.2, 0.4, 3.1]
  ],
  "mode": "TABULAR",
  "task": "fault_diagnosis",
  "label": "pump_window",
  "metadata": {
    "class_labels": [
      "healthy",
      "fault"
    ]
  }
}
```

---

## Request Fields

| Field | Required | Description |
|---------|----------|-------------|
| data | Yes | Structured input data |
| mode | No | Inference mode (default: ANY) |
| task | No | Application context for the inference |
| label | No | Optional request identifier |
| metadata | No | Additional request metadata |

---

## Example Response

```json
{
  "platform": "TQNN",
  "engine": "fault_tolerant_inference",
  "engine_version": "2.0.0",

  "mode": "TABULAR",
  "task": "fault_diagnosis",

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

# GET /store

Returns information about available subscription plans.

## Request

```http
GET /store
```

## Example Response

```json
{
  "plans": [
    {
      "name": "Starter"
    },
    {
      "name": "Builder"
    },
    {
      "name": "Scale"
    }
  ]
}
```

---

# POST /billing/checkout

Creates a Stripe Checkout Session for purchasing or upgrading a subscription.

## Headers

```http
Content-Type: application/json
```

---

## Example Request

```json
{
  "price_id": "price_xxxxxxxxx"
}
```

---

## Example Response

```json
{
  "checkout_url": "https://checkout.stripe.com/..."
}
```

---

# HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Request completed successfully |
| 400 | Invalid request |
| 401 | Missing or invalid API key |
| 403 | Forbidden |
| 404 | Resource not found |
| 422 | Request validation failed |
| 429 | Rate limit or subscription limit exceeded |
| 500 | Internal server error |

---

# Versioning

Current API version:

```text
v2.0.0
```

Future API revisions will preserve compatibility whenever practical. Breaking changes will be introduced through versioned releases.