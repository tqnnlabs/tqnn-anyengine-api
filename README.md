# TQNN AnyEngine API

Commercial multimodal inference infrastructure from TQNN Labs.

Cloud-hosted multimodal inference API and official Python SDK for EEG, finance, chemistry, text, images, and structured data.

---

## Overview

TQNN AnyEngine provides unified inference across multiple data domains through a single runtime interface.

Supported modes:

- EEG
- Finance
- Chemistry
- Text
- Tabular
- Image
- Any-Data

The inference engine is fully managed and hosted by TQNN Labs.

Developers can integrate TQNN from virtually any device capable of making HTTPS requests—without managing specialized AI hardware or quantum hardware.

**ANY** mode automatically selects the appropriate inference pipeline based on the supplied data. Domain-specific modes are also available.

---

## Install

```bash
pip install tqnn
```

---

## Quick Start

```python
from tqnn import TQNNClient

client = TQNNClient(
    api_key="TQNN_xxxxxxxxxxxxxxxxx"
)

result = client.run_any(
    data=[1, 2, 3, 4],
    mode="ANY"
)

print(result)
```

---

## Get an API Key

Choose a subscription plan and receive an API key automatically after checkout.

### Starter

**CA$23.99/month**

- 10,000 API calls/month

### Builder

**CA$79.99/month**

- 50,000 API calls/month

### Scale

**CA$249.99/month**

- 200,000 API calls/month

Sign up at:

https://tqnnlabs.com

---

## REST API Example

```bash
curl -X POST \
-H "Content-Type: application/json" \
-H "x-api-key: TQNN_xxxxxxxxx" \
-d '{
  "data": [1,2,3,4],
  "mode": "ANY"
}'
```

---

## Example Response

```json
{
  "mode": "ANY",
  "label": "demo",
  "probs": [0.31, 0.22, 0.47],
  "threshold": 0.61,
  "qualia": {},
  "intent": [],
  "meta": {}
}
```

---

## Authentication

All API requests require a valid API key.

```text
x-api-key: TQNN_xxxxxxxxx
```

Usage is tracked automatically according to your subscription tier.

---

## Runtime Status

- Managed cloud runtime
- API keys active
- Hosted by TQNN Labs

Website:

https://tqnnlabs.com

---

## Official Python SDK

```bash
pip install tqnn
```

---

## Public Repository Includes

- API interface
- Python SDK
- Client utilities
- Example integrations
- Sample code
- Public documentation

---

## Proprietary Components

The following components are **not included** in this repository:

- Internal runtime implementation
- Proprietary inference substrate
- Private deployment infrastructure
- Internal orchestration services
- Production runtime assets

---

## Security

- API key authentication
- HTTPS encrypted communication
- Hosted cloud inference
- Usage metering
- Managed runtime infrastructure

---

## Licensing

The MIT License applies to:

- Python SDK
- Client libraries
- Examples
- Integration utilities

The managed TQNN AnyEngine runtime and underlying inference substrate remain proprietary intellectual property of TQNN Labs.

---

## Enterprise

For enterprise licensing, commercial partnerships, research collaborations, custom integrations, or deployment inquiries:

**tqnnlabs@gmail.com**

---

# About TQNN Labs

TQNN Labs develops cloud-hosted multimodal inference infrastructure for structured data applications.

Website:

https://tqnnlabs.com

Built in Canada 🇨🇦

---

# Vision

TQNN Labs is building a unified inference platform that enables developers to work across multiple domains through a single cloud-hosted API.

**Build once. Analyze any data.**