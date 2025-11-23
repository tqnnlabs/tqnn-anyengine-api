# TQNN AnyEngine API — Developer Guide

This guide explains how to consume the TQNN AnyEngine API using:
- Python client
- direct HTTP requests
- mode-specific payload formats

⚠️ **Important**
The TQNN Core Engine is a protected trade secret.  
This guide describes the API surface only.  
It does not reveal or imply internal substrate mechanisms.

---

## 🔑 Authentication

Every request must include:

```
x-api-key: YOUR_TQNN_API_KEY
```

Keys are subscription-bound.  
Usage is metered at runtime.

---

## 🔗 API Endpoint

Example:

```
https://YOUR-TQNN-ENDPOINT/run_any
```

---

# 📦 Python Client Setup

Install (PyPI — coming soon):

```
pip install tqnn-client
```

Until release, use `tqnn_client.py` from this repo.

---

## 🧠 Core Client Example

```python
from tqnn_client import TQNNClient
import os

BASE_URL = os.getenv("TQNN_API_URL", "https://YOUR-ENDPOINT")
API_KEY  = os.getenv("TQNN_API_KEY")

client = TQNNClient(api_key=API_KEY, base_url=BASE_URL)

result = client.run_any(
    data=[[1,2,3]],
    mode="TABULAR",
    label="demo"
)

print(result)
```

---

# 🚀 Supported Modes

The API accepts structured numeric arrays.

## 1. EEG Mode

### Input
- shape: `(channels x samples)`
- values: floats

### Example EEG payload
```json
{
  "mode": "EEG",
  "label": "subject_A",
  "sfreq": 250.0,
  "data": [
    [0.12, -0.33, 0.88, ...],
    [0.01,  0.45, -0.55, ...],
    ...
  ]
}
```

### Output fields
- `probs`: inference distribution
- `threshold`: activation tau
- `qualia`: substrate embedding snapshot
- `intent`: decision vector

---

## 2. Tabular Mode

### Input
- 2D matrix of samples → `[rows][features]`

Example:
```json
{
  "mode": "TABULAR",
  "label": "demo_table",
  "data": [
    [1.2, 0.4, 3.3, 0.1],
    [2.1, 1.1, 0.9, 0.5]
  ]
}
```

---

## 3. Finance Mode

### Input
OHLCV or indicator matrices.
Typical:
- RSI
- MACD
- trend slope
- volatility
- price windows

Example:
```json
{
  "mode": "FINANCE",
  "label": "TSLA",
  "data": [
    [open, high, low, close, volume, rsi, macd, signal, trend_slope]
  ]
}
```

---

## 4. Image Mode (Beta)

Accepts:
- flattened arrays
- tensor-like lists

Example:
```json
{
  "mode": "IMAGE",
  "label": "mnist",
  "data": [[0.1, 0.3, 0.0, ...]]
}
```

---

# 📫 Typical Response

Example (all modes return comparable structure):

```json
{
  "mode": "TABULAR",
  "label": "demo_table",
  "probs": [0.18, 0.44, 0.38],
  "threshold": 0.613,
  "qualia": "...",
  "intent": "...",
  "usage": 41
}
```

### Field meanings
- **probs** → inference distribution
- **threshold (tau)** → substrate activation
- **qualia** → internal embedding snapshot
- **intent** → decision / phase geometry
- **usage** → runtime quota balance

---

# 🔥 Errors

### 401
Invalid key / missing key

### 429
Quota exhausted

### 400
Malformed payload

---

# 🚫 What is NOT exposed

- substrate models
- GHZ cobordism logic
- phase routing
- internal training
- embedding reconstruction

The API returns inference; not substrate internals.

---