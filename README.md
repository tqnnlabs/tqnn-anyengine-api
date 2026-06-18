TQNN AnyEngine API

Commercial multimodal inference API from TQNN Labs.

Process structured data through the TQNN AnyEngine runtime using a simple REST API or the official Python SDK.

---

Overview

TQNN AnyEngine provides API-accessible inference across multiple data domains through a unified runtime interface.

Supported modes:

- EEG
- Finance
- Chemistry
- Text
- Tabular
- Image
- Any-Data

The runtime is delivered as a managed cloud service.

---

Install

pip install tqnn

---

Quick Start

from tqnn import TQNNClient

client = TQNNClient(
    api_key="TQNN_xxxxxxxxxxxxxxxxx"
)

result = client.run_any(
    data=[1, 2, 3, 4],
    mode="ANY"
)

print(result)

---

Get an API Key

Choose a subscription plan and receive an API key automatically after successful checkout.

Tier 1 — Starter

- CA$23.99/month
- 10,000 API calls

Tier 2 — Builder

- CA$79.99/month
- 50,000 API calls

Tier 3 — Scale

- CA$249.99/month
- 200,000 API calls

Sign up:

https://tqnnlabs.com

---

REST API Example

curl -X POST https://api.tqnnlabs.com/run/any \
  -H "Content-Type: application/json" \
  -H "x-api-key: TQNN_xxxxxxxxx" \
  -d '{
    "data": [1,2,3,4],
    "mode": "ANY"
  }'

---

Example Response

{
  "mode": "ANY",
  "label": "demo",
  "probs": [0.31, 0.22, 0.47],
  "threshold": 0.61,
  "qualia": {},
  "intent": [],
  "meta": {}
}

---

Authentication

All API requests require an API key:

x-api-key: TQNN_xxxxxxxxx

Usage is tracked automatically.

---

API Documentation

Interactive API Docs:

https://api.tqnnlabs.com/docs

Health Endpoint:

https://api.tqnnlabs.com/health

---

SDK

Official Python SDK:

pip install tqnn

Example:

from tqnn import TQNNClient

client = TQNNClient(api_key="TQNN_xxxxxxxxx")

result = client.run_any(
    data=[1, 2, 3, 4],
    mode="TABULAR"
)

---

Repository Contents

Included:

- API interface
- SDK utilities
- Client examples
- Integration samples
- Public documentation

Not Included:

- Internal runtime implementation
- Proprietary infrastructure
- Private deployment assets

---

Licensing

MIT License applies to:

- SDK
- Client libraries
- Examples
- Integration utilities

See LICENSE for details.

The managed TQNN runtime service remains proprietary intellectual property of TQNN Labs.

---

Enterprise Access

For enterprise deployment, custom integrations, licensing, or commercial partnerships:

tqnnlabs@gmail.com

---

About TQNN Labs

TQNN Labs develops multimodal inference infrastructure and runtime services for structured data applications.

Website:
https://tqnnlabs.com

Contact:
tqnnlabs@gmail.com

Built in Canada.
