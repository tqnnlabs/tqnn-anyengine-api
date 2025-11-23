# pip install tqnn-client
"""
EEG demo for the TQNN AnyEngine API.

This example shows how to send an EEG segment to the API.
You are expected to replace the synthetic data below with a real
(channels x samples) EEG matrix from your own loader (e.g., MNE).
"""

import os
import numpy as np
from tqnn_client import TQNNClient


# Recommended: configure via environment variables
BASE_URL = os.getenv("TQNN_API_URL", "https://YOUR-TQNN-ENDPOINT")
API_KEY  = os.getenv("TQNN_API_KEY", "YOUR_TQNN_API_KEY")


def main():
    # Create client
    client = TQNNClient(api_key=API_KEY, base_url=BASE_URL)

    # ------------------------------------------------------------------
    # Fake EEG data example
    #   - 3 channels
    #   - 250 samples (1 second at 250 Hz)
    # Replace this with your real EEG array.
    # ------------------------------------------------------------------
    sfreq = 250.0  # sampling frequency in Hz

    eeg_array = np.random.randn(3, 250).tolist()

    result = client.run_any(
        data=eeg_array,
        mode="EEG",
        label="eeg_demo_subject",
        metadata={
            "sfreq": sfreq,
            "note": "synthetic EEG example – replace with real data",
        },
    )

    print("=== TQNN AnyEngine EEG demo ===")
    print("Mode:      ", result.get("mode"))
    print("Label:     ", result.get("label"))
    print("Probs:     ", result.get("probs"))
    print("Threshold: ", result.get("threshold"))
    print("Qualia:    ", result.get("qualia"))
    print("Intent:    ", result.get("intent"))
    print("Usage:     ", result.get("usage"))


if __name__ == "__main__":
    main()