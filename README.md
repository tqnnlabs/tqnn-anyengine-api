TQNN AnyEngine API

Commercial multi-domain inference API from TQNN Labs.

Process structured data through a unified runtime interface using either the official Python SDK or direct REST API access.

---

What is TQNN?

TQNN AnyEngine is designed to process multiple forms of structured data through a single runtime.

Supported modes:

- EEG & Neural Signals
- Finance & Market Data
- Chemistry & Molecular Data
- Text & Language Statistics
- Tabular Datasets
- Image Features
- Custom Signal Analysis

Any data in. TQNN inference out.

---

Get API Access

API keys are available through TQNN Labs.

Website:

https://tqnnlabs.com

After successful checkout, API keys are delivered automatically.

Tier 1 — Starter

- CA$23.99/month
- 10,000 API calls

Tier 2 — Builder

- CA$79.99/month
- 50,000 API calls

Tier 3 — Scale

- CA$249.99/month
- 200,000 API calls

---

Install the SDK

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

All requests require an API key.

x-api-key: TQNN_xxxxxxxxx

Usage is tracked automatically based on subscription tier.

---

Documentation

Interactive API Documentation:

https://api.tqnnlabs.com/docs

Health Endpoint:

https://api.tqnnlabs.com/health

---

Repository Contents

Included:

- Public API interface
- Python SDK integration
- Example clients
- Documentation
- Integration samples

Not Included:

- Proprietary runtime internals
- Private infrastructure
- Internal deployment assets
- TQNN core substrate implementation

---

Licensing

MIT License applies to:

- SDK
- Client libraries
- Examples
- Integration utilities

The managed TQNN runtime service remains proprietary intellectual property of TQNN Labs.

---

Enterprise & Commercial Access

For enterprise licensing, custom integrations, partnerships, or deployment inquiries:

tqnnlabs@gmail.com

---

About TQNN Labs

TQNN Labs develops multi-domain inference infrastructure and runtime services.

Website:
https://tqnnlabs.com

Contact:
tqnnlabs@gmail.com

Built in Canada.

Beyond Prediction. Toward Understanding.