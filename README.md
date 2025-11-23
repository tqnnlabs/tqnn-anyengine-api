⚠️ NOTICE — PROTECTED TRADE SECRET

The TQNN Core Engine is a protected trade secret.
This repository provides only the API interface and client utilities.
No inference substrate, internal algorithms, or architectural logic are present.

Unauthorized attempts to extract, replicate, or reverse-engineer substrate logic
will result in immediate access termination and legal action.


---

🔹 TQNN AnyEngine API

Public SaaS API for TQNN AnyEngine
Modes supported: EEG / Finance / Tabular / Image / Any-Data


---

🌐 Overview

TQNN — Tubulin Quantum Neural Network
A quantum-inspired computational substrate.

The system converts structured numeric data into high-dimensional inference embeddings
and phase-based decision outputs.

> ⚠️ The Core substrate is NOT provided in this repository.



Unlike classical ML systems:

No training loops

No gradient descent

No weights or tuning


You send structured data → the substrate returns:

inference probabilities

activation threshold (tau)

qualia embedding snapshot

intent vector

decision geometry


The engine behaves as a quantum-inspired inference oracle,
not a train-and-predict model.


---

🧠 Functional Modes

EEG

Input: (channels × samples) matrix
Output: state basins, coherence bands, intent vectors

Tabular

Input: row-wise numeric samples
Output: class basin, phase threshold, decision quality

Finance

Input: OHLCV, indicators, rolling features
Output: directional probability, phase confidence, action geometry

Image (Beta)

Input: flattened or tensor image
Output: perceptual probabilities, embedding vectors

> Any structured numeric array can be used as input.




---

🔑 Authentication

Customers receive an API key tied to a subscription tier.

Send via HTTP header:

x-api-key: YOUR_TQNN_API_KEY

Usage is tracked at runtime

Quotas are enforced

Overages are billed automatically

Core substrate logic is never exposed



---

📦 Client Installation

Official PyPI package (coming soon):

pip install tqnn-client

Until release, use the provided tqnn_client.py.


---

🚀 Quickstart Example — Tabular

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

Field meanings

probs — inference probability distribution

threshold — activation score (tau)

qualia — substrate embedding snapshot

intent — decision geometry

usage — runtime quota counter



---

📂 Repository Contents

Included:

API wrapper utilities

SDK client code

Request/response schemas

Integration examples

Public demos


Not included:

Core substrate

Inference algorithms

Architectural models

Internal runtimes



---

🛡️ Licensing

This project is dual-licensed.


---

✔️ MIT License — Open Layer

Applies to:

API wrapper

Integration libraries

SDK utilities

Example scripts

Public demos


You may freely:

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

Quantum-inspired inference substrate

Qualia & intent embeddings

Internal runtimes and training pipelines


Access requires:

Paid subscription
or

Enterprise licensing agreement


See TQNN-Core-License.md.


---

⚠️ Important Notice

This repository contains:

Public API endpoints

Client utilities

Integration examples


This repository does not contain:

Substrate logic

Inference circuits

Decision models

Architectural mechanisms


Attempts to:

reverse-engineer

simulate substrate behavior

train competitor models using embeddings

reconstruct internal logic


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

🗺 Roadmap

PyPI client package

CLI tooling

Multi-modal SDK modules

Android edge inference

Enterprise substrate clusters

GPU acceleration



---

📬 Contact

Enterprise licensing & integration:
tqnnlabs@gmail.com


---

Final Reminder

This repository provides:

API surface

Client utilities

Usage examples


It does not provide:

The substrate

The inference models

The architecture


The Core remains sealed.

---

🔗 Live Endpoint (Coming Soon)
https://api.tqnn.dev