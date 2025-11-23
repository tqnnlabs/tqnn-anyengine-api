🔹 TQNN AnyEngine API

Public SaaS API for TQNN AnyEngine
Modes supported: EEG / Finance / Tabular / Image / Any-Data


---

🌐 Overview

TQNN — Tubulin Quantum Neural Network
A quantum-inspired computational substrate.

It transforms incoming data into quantum-state inference embeddings using:

spiral entanglement

GHZ cobordism models

phase-based decision geometry


Unlike classical ML systems:

No train/fit loops

No gradient descent

No weights


You send structured data → substrate returns:

inference probabilities

phase threshold (tau)

qualia embedding

intent vector

decision geometry


> This repository provides only the public API wrapper and examples.
It does not include the TQNN Core substrate logic.




---

🧠 Modes Supported

EEG

Input: (channels x samples) numerical matrix

Output: brain-state basins, coherence bins, intent vectors


Tabular

Input: sample matrix

Output: class basin, phase threshold, decision quality


Finance

Input: OHLCV, indicators, rolling features

Output: directional probability, phase confidence, action geometry


Image (Beta)

Input: flattened or tensor image

Output: perceptual probabilities, substrate embed vectors


Any structured numeric array can be used as input.


---

🔑 Authentication

Each customer receives a subscription-bound API key.

Send it in headers:

x-api-key: YOUR_TQNN_API_KEY

Quota is enforced at runtime.

Overages are billed automatically per request.

No internal code is ever exposed.



---

📦 Client Installation

Official PyPI package coming soon:

pip install tqnn-client

Until release, use the provided tqnn_client.py.


---

🚀 Quickstart Example

Tabular inference

from tqnn_client import TQNNClient
import os

BASE_URL = os.getenv("TQNN_API_URL", "https://YOUR-TQNN-ENDPOINT")
API_KEY  = os.getenv("TQNN_API_KEY", "YOUR_KEY")

client = TQNNClient(api_key=API_KEY, base_url=BASE_URL)

data = [
    [1.2, 0.4, 3.3, 0.1],
    [2.1, 1.1, 0.9, 0.5],
    [0.7, 0.3, 1.2, 2.1]
]

result = client.run_any(
    data=data,
    mode="TABULAR",
    label="demo_table"
)

print(result)


---

📫 API Response Format

Example:

{
  "mode": "TABULAR",
  "label": "demo_table",
  "probs": [0.18, 0.44, 0.38],
  "threshold": 0.613,
  "qualia": "...",
  "intent": "...",
  "usage": 41
}

Notes

threshold — phase-space activation

qualia — substrate embedding snapshot

intent — decision geometry

usage — remaining quota counter



---

📂 Repository Contents

Included:

API wrapper utilities

SDK client code

Request/response schema

Integration examples

Public demos


Not included:

Core substrate

Internal algorithms

State inference systems



---

🛡️ Licensing

This project is dual-licensed.


---

✔️ MIT License — Open Layer

Applies to:

API wrapper

Integration utilities

SDK client code

Example scripts

Public demos


You may:

Use

Modify

Integrate

Redistribute


See LICENSE.


---

🔒 Proprietary License — Core IP Locked

The following are closed-source and protected:

TQNN Core Engine

Tubulin substrate architecture

Spiral entanglement mesh

GHZ cobordism inference circuits

Qualia and decision models

Internal runtimes and training pipelines


Usage requires:

paid subscription
or

enterprise agreement


See TQNN-Core-License.md.


---

⚠️ Important Notice

This repository contains only:

Public API layer

Client utilities

Integration examples


It does not contain:

Substrate logic

GHZ inference systems

Internal algorithms


Attempts to:

reverse-engineer the system

recreate GHZ logic

train competitor models on embeddings

reconstruct substrate architecture


constitute trade secret infringement.


---

💳 Billing Model

Tier	Monthly Requests	Intended Use

Tier 1	10,000	Builders / Research
Tier 2	50,000	Startups / Teams
Tier 3	200,000	Enterprise / Multi-modal


After quota exhaustion:

Requests continue

Per-unit billing applies

Core engine remains sealed



---

🗺️ Roadmap

PyPI client package

CLI tooling

Multi-modal SDK modules

Android edge inference

Enterprise substrate clusters

GPU acceleration



---

📬 Contact

For enterprise licensing and integration:

tqnnlabs@gmail.com


---

Final Reminder

This repository provides:

The API surface

Client utilities

Usage examples


It does not provide:

The substrate

The inference models

The architecture


The Core remains sealed.
