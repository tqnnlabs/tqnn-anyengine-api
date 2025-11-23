# pip install tqnn-client

"""
Tabular demo for the TQNN AnyEngine API.

This example shows how to send numeric or structured data to the API.
You can replace the sample rows with your own real dataset.

This file is SAFE and PUBLIC — no proprietary code is exposed.
"""

import os
from tqnn_client import TQNNClient


# =============================
# 🔐 Recommended: environment variables
#   - NEVER paste keys into code
#   - Users should do:
#         export TQNN_API_KEY="xxxxx"
#         export TQNN_API_URL="https://..."
# =============================

BASE_URL = os.getenv("TQNN_API_URL", "https://YOUR-TQNN-ENDPOINT")
API_KEY  = os.getenv("TQNN_API_KEY", "YOUR_API_KEY_HERE")


def main():
    # Authenticate with the public API wrapper
    client = TQNNClient(api_key=API_KEY, base_url=BASE_URL)

    # Example input: 5 samples x 4 features
    #
    # NOTE:
    #   - Raw Python lists
    #   - No numpy objects
    #
    tabular_data = [
        [1.2, 0.4, 3.3, 0.1],
        [2.1, 1.1, 0.9, 0.5],
        [0.7, 0.3, 1.2, 2.1],
        [1.8, 0.9, 2.5, 0.4],
        [3.0, 1.0, 0.2, 0.6],
    ]

    # Call the AnyEngine
    result = client.run_any(
        data=tabular_data,
        mode="TABULAR",
        label="demo_table",
    )

    print("=== TQNN AnyEngine TABULAR demo ===")
    print("Mode:        ", result.get("mode"))
    print("Label:       ", result.get("label"))
    print("Probs:       ", result.get("probs"))
    print("Threshold:   ", result.get("threshold"))
    print("Qualia:      ", result.get("qualia"))
    print("Intent:      ", result.get("intent"))


if __name__ == "__main__":
    main()