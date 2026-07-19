"""
TQNN Fault-Tolerant Inference Python Client

Lightweight HTTP client for the public TQNN API.

The client:
- sends structured data to the /run/any endpoint
- supports caller-defined inference tasks
- supports optional class labels and request metadata
- returns the normalized TQNN v2 response
- provides clear errors for API and network failures

Usage:

    from tqnn_client import TQNNClient

    client = TQNNClient(
        api_key="YOUR_TQNN_API_KEY",
        base_url="https://api.tqnnlabs.com",
    )

    response = client.run_any(
        data=[2, 3, 5, 7, 11, 13],
        mode="TABULAR",
        task="fault_diagnosis",
        label="example_request",
        metadata={
            "class_labels": [
                "healthy",
                "fault",
            ]
        },
    )

    print(response["result"])
    print(response["tqnn_report"])
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests


class TQNNClientError(RuntimeError):
    """Base error raised by the TQNN Python client."""


class TQNNAPIError(TQNNClientError):
    """Raised when the TQNN API returns an unsuccessful response."""

    def __init__(
        self,
        *,
        status_code: int,
        message: str,
        response_body: Any = None,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body

        super().__init__(
            f"TQNN API request failed "
            f"with status {status_code}: {message}"
        )


class TQNNClient:
    """
    HTTP client for the TQNN Fault-Tolerant Inference API.

    Parameters
    ----------
    api_key:
        Active TQNN API key.

    base_url:
        Public TQNN API URL. A trailing slash is removed automatically.

    timeout:
        Maximum number of seconds to wait for an inference response.
    """

    SUPPORTED_MODES = frozenset(
        {
            "EEG",
            "FINANCE",
            "TABULAR",
            "IMAGE",
            "ANY",
        }
    )

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.tqnnlabs.com",
        timeout: float = 120.0,
    ) -> None:
        normalized_api_key = str(api_key or "").strip()
        normalized_base_url = str(base_url or "").strip().rstrip("/")

        if not normalized_api_key:
            raise ValueError("api_key is required")

        if not normalized_base_url:
            raise ValueError("base_url is required")

        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")

        self.api_key = normalized_api_key
        self.base_url = normalized_base_url
        self.timeout = float(timeout)

        self._session = requests.Session()
        self._session.headers.update(
            {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "tqnn-python-client/2.0.0",
            }
        )

    def run_any(
        self,
        data: Any,
        mode: str = "ANY",
        task: Optional[str] = None,
        label: Optional[str] = None,
        sfreq: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run fault-tolerant inference through the public TQNN API.

        Parameters
        ----------
        data:
            Numeric structured input accepted by the selected mode.

        mode:
            Input-processing mode:

            - EEG
            - FINANCE
            - TABULAR
            - IMAGE
            - ANY

        task:
            Caller-defined purpose of the inference.

            Examples:

            - fault_diagnosis
            - fault_detection
            - anomaly_detection
            - sensor_monitoring
            - classification
            - state_estimation
            - trend_prediction
            - general_inference

        label:
            Optional caller-defined request label or subject identifier.

        sfreq:
            Sampling frequency for EEG input.

        metadata:
            Optional request metadata.

            Caller-provided class labels may be supplied to map a predicted
            class index to a meaningful response label.

            Example:

                metadata={
                    "class_labels": [
                        "healthy",
                        "sensor_bias",
                        "sensor_drift",
                    ]
                }

        Returns
        -------
        Dict[str, Any]
            TQNN v2 response containing:

            - result
            - tqnn_report
            - diagnostics
        """
        normalized_mode = self._normalize_mode(mode)
        safe_metadata = dict(metadata or {})

        if normalized_mode == "EEG":
            if sfreq is None:
                raise ValueError(
                    "sfreq is required when mode is EEG"
                )

            try:
                normalized_sfreq = float(sfreq)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "sfreq must be a positive number"
                ) from exc

            if normalized_sfreq <= 0:
                raise ValueError(
                    "sfreq must be greater than zero"
                )

        elif sfreq is not None:
            try:
                normalized_sfreq = float(sfreq)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "sfreq must be a positive number"
                ) from exc

            if normalized_sfreq <= 0:
                raise ValueError(
                    "sfreq must be greater than zero"
                )

        else:
            normalized_sfreq = None

        payload: Dict[str, Any] = {
            "data": data,
            "mode": normalized_mode,
            "task": task,
            "label": label,
            "metadata": safe_metadata,
        }

        if normalized_sfreq is not None:
            payload["sfreq"] = normalized_sfreq

        response = self._request(
            method="POST",
            path="/run/any",
            json_payload=payload,
        )

        self._validate_v2_response(response)

        return response

    def result(
        self,
        response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Return the primary normalized inference result."""
        result = response.get("result")

        if not isinstance(result, dict):
            raise TQNNClientError(
                "Response does not contain a valid result object"
            )

        return result

    def report(
        self,
        response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Return the standardized TQNN Report."""
        report = response.get("tqnn_report")

        if not isinstance(report, dict):
            raise TQNNClientError(
                "Response does not contain a valid tqnn_report object"
            )

        return report

    def diagnostics(
        self,
        response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Return advanced inference diagnostics."""
        diagnostics = response.get("diagnostics")

        if not isinstance(diagnostics, dict):
            raise TQNNClientError(
                "Response does not contain valid diagnostics"
            )

        return diagnostics

    def health(self) -> Dict[str, Any]:
        """
        Read the public API health endpoint.

        This endpoint does not require an API inference call.
        """
        return self._request(
            method="GET",
            path="/health",
        )

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> "TQNNClient":
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        self.close()

    def _request(
        self,
        *,
        method: str,
        path: str,
        json_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"

        try:
            response = self._session.request(
                method=method,
                url=url,
                json=json_payload,
                timeout=self.timeout,
            )

        except requests.Timeout as exc:
            raise TQNNClientError(
                "TQNN API request timed out"
            ) from exc

        except requests.ConnectionError as exc:
            raise TQNNClientError(
                "Could not connect to the TQNN API"
            ) from exc

        except requests.RequestException as exc:
            raise TQNNClientError(
                f"TQNN API request failed: {exc}"
            ) from exc

        try:
            response_body = response.json()
        except ValueError:
            response_body = response.text

        if not response.ok:
            message = self._extract_error_message(
                response_body
            )

            raise TQNNAPIError(
                status_code=response.status_code,
                message=message,
                response_body=response_body,
            )

        if not isinstance(response_body, dict):
            raise TQNNClientError(
                "TQNN API returned an invalid response object"
            )

        return response_body

    def _normalize_mode(self, mode: Any) -> str:
        normalized_mode = str(mode or "ANY").strip().upper()

        if normalized_mode not in self.SUPPORTED_MODES:
            supported_modes = ", ".join(
                sorted(self.SUPPORTED_MODES)
            )

            raise ValueError(
                f"Unsupported TQNN mode '{normalized_mode}'. "
                f"Supported modes: {supported_modes}."
            )

        return normalized_mode

    def _validate_v2_response(
        self,
        response: Dict[str, Any],
    ) -> None:
        required_fields = {
            "platform",
            "engine",
            "engine_version",
            "mode",
            "task",
            "result",
            "tqnn_report",
            "diagnostics",
        }

        missing_fields = sorted(
            required_fields.difference(response.keys())
        )

        if missing_fields:
            raise TQNNClientError(
                "TQNN API response does not match the v2 contract. "
                f"Missing fields: {', '.join(missing_fields)}"
            )

        if not isinstance(response.get("result"), dict):
            raise TQNNClientError(
                "TQNN API returned an invalid result object"
            )

        if not isinstance(response.get("tqnn_report"), dict):
            raise TQNNClientError(
                "TQNN API returned an invalid tqnn_report object"
            )

        if not isinstance(response.get("diagnostics"), dict):
            raise TQNNClientError(
                "TQNN API returned an invalid diagnostics object"
            )

    def _extract_error_message(
        self,
        response_body: Any,
    ) -> str:
        if isinstance(response_body, dict):
            detail = response_body.get("detail")

            if isinstance(detail, str):
                return detail

            if isinstance(detail, dict):
                message = detail.get("message")

                if message:
                    return str(message)

                return str(detail)

            if detail is not None:
                return str(detail)

            message = response_body.get("message")

            if message:
                return str(message)

        if isinstance(response_body, str):
            cleaned = response_body.strip()

            if cleaned:
                return cleaned[:1000]

        return "Unknown API error"