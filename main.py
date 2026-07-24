from __future__ import annotations

from typing import Any, Dict, List, Optional

import hashlib
import os
import secrets
import time

import requests
import stripe
from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from google.cloud import firestore
from pydantic import BaseModel, Field
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# ======================================================
# ENV CONFIG — DO NOT HARDCODE SECRETS
# ======================================================

STRIPE_SECRET_KEY = os.environ.get(
    "STRIPE_SECRET_KEY",
    "",
)

STRIPE_WEBHOOK_SECRET = os.environ.get(
    "STRIPE_WEBHOOK_SECRET",
    "",
)

STRIPE_PRICE_TIER1 = os.environ.get(
    "STRIPE_PRICE_TIER1",
    "",
)

STRIPE_PRICE_TIER2 = os.environ.get(
    "STRIPE_PRICE_TIER2",
    "",
)

STRIPE_PRICE_TIER3 = os.environ.get(
    "STRIPE_PRICE_TIER3",
    "",
)

CORE_URL = os.environ.get(
    "CORE_URL",
    "",
).rstrip("/")

INTERNAL_CORE_SECRET = os.environ.get(
    "INTERNAL_CORE_SECRET",
    "",
)

SENDGRID_API_KEY = os.environ.get(
    "SENDGRID_API_KEY",
    "",
)

FROM_EMAIL = os.environ.get(
    "FROM_EMAIL",
    "tqnnlabs@gmail.com",
)

PUBLIC_SITE_URL = os.environ.get(
    "PUBLIC_SITE_URL",
    "https://tqnnlabs.com",
).rstrip("/")

SUCCESS_URL = os.environ.get(
    "SUCCESS_URL",
    (
        f"{PUBLIC_SITE_URL}/tqnn-success"
        "?session_id={{CHECKOUT_SESSION_ID}}"
    ),
)

CANCEL_URL = os.environ.get(
    "CANCEL_URL",
    f"{PUBLIC_SITE_URL}/tqnn-cancel",
)


if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY


db = firestore.Client()


# Stripe-backed paid plans only.
PRICE_BY_TIER = {
    "tier1": STRIPE_PRICE_TIER1,
    "tier2": STRIPE_PRICE_TIER2,
    "tier3": STRIPE_PRICE_TIER3,
}


# All API access plans.
TIER_LIMITS = {
    "explorer": 100,
    "tier1": 10_000,
    "tier2": 50_000,
    "tier3": 200_000,
}


TIER_LABELS = {
    "explorer": "Explorer",
    "tier1": "Starter",
    "tier2": "Builder",
    "tier3": "Scale",
}


# ======================================================
# REQUEST MODELS
# ======================================================

class RunAnyRequest(BaseModel):
    """
    Public request model for fault-tolerant inference.

    The caller supplies the intended task. TQNN does not invent the
    real-world meaning of arbitrary data.
    """

    data: Any
    mode: str = "ANY"
    task: Optional[str] = None
    label: Optional[str] = None
    sfreq: Optional[float] = None
    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )


class CheckoutRequest(BaseModel):
    customer_email: str
    tier: str = "tier1"


class ExplorerSignupRequest(BaseModel):
    customer_email: str


# ======================================================
# RESPONSE MODELS
# ======================================================

class InferenceResult(BaseModel):
    prediction_index: Optional[int] = None
    prediction_label: Optional[str] = None
    confidence: float
    decision: str


class ConfidenceReport(BaseModel):
    score: float
    label: str
    margin: float
    normalized_entropy: float


class DataIntegrityReport(BaseModel):
    score: float
    label: str
    feature_count: int
    finite_fraction: float
    missing_fraction: float
    constant_input: bool


class DecisionReport(BaseModel):
    status: str
    threshold_met: bool


class TQNNReport(BaseModel):
    primary_capability: str
    task: str
    inference_mode: str
    confidence: ConfidenceReport
    data_integrity: DataIntegrityReport
    decision: DecisionReport
    warnings: List[str] = Field(
        default_factory=list
    )


class InferenceDiagnostics(BaseModel):
    probabilities: List[float] = Field(
        default_factory=list
    )
    acceptance_threshold: float
    threshold_met: bool
    confidence_margin: float
    normalized_entropy: float
    qualia: Any = None
    intent: List[Any] = Field(
        default_factory=list
    )
    meta: Dict[str, Any] = Field(
        default_factory=dict
    )


class RunResponse(BaseModel):
    platform: str
    engine: str
    engine_version: str
    mode: str
    task: str
    label: Optional[str] = None
    result: InferenceResult
    tqnn_report: TQNNReport
    diagnostics: InferenceDiagnostics


# ======================================================
# HELPERS
# ======================================================

def now_ts() -> float:
    return time.time()


def normalize_email(email: str) -> str:
    return str(
        email or ""
    ).strip().lower()


def validate_email(email: str) -> str:
    normalized = normalize_email(email)

    if not normalized:
        raise HTTPException(
            status_code=400,
            detail="Email address is required",
        )

    if "@" not in normalized:
        raise HTTPException(
            status_code=400,
            detail="Invalid email address",
        )

    local_part, domain = normalized.rsplit(
        "@",
        1,
    )

    if (
        not local_part
        or not domain
        or "." not in domain
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid email address",
        )

    return normalized


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(
        api_key.encode("utf-8")
    ).hexdigest()


def hash_email(email: str) -> str:
    normalized = normalize_email(email)

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def generate_api_key() -> str:
    return (
        "TQNN_"
        + secrets.token_urlsafe(32)
    )


def send_api_key_email(
    to_email: str,
    api_key: str,
    tier: str,
) -> None:
    if not SENDGRID_API_KEY:
        raise RuntimeError(
            "SENDGRID_API_KEY is not configured"
        )

    normalized_tier = str(
        tier or ""
    ).strip().lower()

    tier_label = TIER_LABELS.get(
        normalized_tier,
        normalized_tier.title(),
    )

    quota_limit = TIER_LIMITS.get(
        normalized_tier,
        0,
    )

    subject = (
        f"Your TQNN {tier_label} API Key"
    )

    html = f"""
    <div style="
      font-family:Arial,sans-serif;
      line-height:1.5;
      color:#111827;
    ">
      <h2>Welcome to TQNN Labs</h2>

      <p>
        Your access to the TQNN Fault-Tolerant
        Inference Platform is active.
      </p>

      <p>
        <b>Plan:</b> {tier_label}
      </p>

      <p>
        <b>Included API calls:</b>
        {quota_limit:,}
      </p>

      <p><b>Your API key:</b></p>

      <pre style="
        background:#f4f4f4;
        padding:12px;
        border-radius:8px;
        overflow-wrap:anywhere;
        white-space:pre-wrap;
      ">{api_key}</pre>

      <p>Example:</p>

      <pre style="
        background:#f4f4f4;
        padding:12px;
        border-radius:8px;
        white-space:pre-wrap;
        overflow-x:auto;
      ">curl -X POST https://api.tqnnlabs.com/run/any \\
  -H "Content-Type: application/json" \\
  -H "x-api-key: {api_key}" \\
  -d '{{
    "data": [1, 2, 3, 4],
    "mode": "TABULAR",
    "task": "fault_diagnosis",
    "label": "example",
    "metadata": {{
      "class_labels": [
        "healthy",
        "fault"
      ]
    }}
  }}'</pre>

      <p>
        Keep this key private. Do not publish it or
        commit it to GitHub.
      </p>

      <p>
        Learn more at
        <a href="{PUBLIC_SITE_URL}">
          {PUBLIC_SITE_URL}
        </a>.
      </p>

      <p>— TQNN Labs</p>
    </div>
    """

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html,
    )

    sg = SendGridAPIClient(
        SENDGRID_API_KEY
    )

    sg.send(message)


def create_api_key(
    customer_email: str,
    tier: str,
    customer_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
) -> str:
    normalized_email = validate_email(
        customer_email
    )

    normalized_tier = str(
        tier or ""
    ).strip().lower()

    if normalized_tier not in TIER_LIMITS:
        raise ValueError(
            "Unsupported API tier: "
            f"{normalized_tier}"
        )

    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)

    quota_limit = TIER_LIMITS[
        normalized_tier
    ]

    access_type = (
        "free"
        if normalized_tier == "explorer"
        else "subscription"
    )

    db.collection(
        "api_keys"
    ).document(
        key_hash
    ).set(
        {
            "key_hash": key_hash,
            "key_suffix": api_key[-8:],
            "customer_email": normalized_email,
            "customer_id": customer_id,
            "subscription_id": subscription_id,
            "tier": normalized_tier,
            "access_type": access_type,
            "used": 0,
            "quota_limit": quota_limit,
            "created_at": now_ts(),
            "last_used": None,
            "active": True,
        }
    )

    return api_key


def create_api_key_for_subscription(
    customer_email: str,
    customer_id: Optional[str],
    subscription_id: Optional[str],
    tier: str,
) -> str:
    """
    Compatibility wrapper used by the Stripe webhook.
    """
    return create_api_key(
        customer_email=customer_email,
        tier=tier,
        customer_id=customer_id,
        subscription_id=subscription_id,
    )


def create_explorer_api_key(
    customer_email: str,
) -> str:
    """
    Create one Explorer key per normalized email address.

    The explorer_signups collection uses a deterministic email hash
    as the document ID, preventing duplicate free registrations.
    """
    normalized_email = validate_email(
        customer_email
    )

    signup_id = hash_email(
        normalized_email
    )

    signup_reference = (
        db.collection("explorer_signups")
        .document(signup_id)
    )

    transaction = db.transaction()

    @firestore.transactional
    def reserve_signup(
        txn: firestore.Transaction,
    ) -> str:
        signup_snapshot = signup_reference.get(
            transaction=txn
        )

        if signup_snapshot.exists:
            raise HTTPException(
                status_code=409,
                detail=(
                    "An Explorer key has already "
                    "been issued for this email"
                ),
            )

        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)

        key_reference = (
            db.collection("api_keys")
            .document(key_hash)
        )

        txn.set(
            key_reference,
            {
                "key_hash": key_hash,
                "key_suffix": api_key[-8:],
                "customer_email": normalized_email,
                "customer_id": None,
                "subscription_id": None,
                "tier": "explorer",
                "access_type": "free",
                "used": 0,
                "quota_limit": (
                    TIER_LIMITS["explorer"]
                ),
                "created_at": now_ts(),
                "last_used": None,
                "active": True,
            },
        )

        txn.set(
            signup_reference,
            {
                "customer_email": normalized_email,
                "email_hash": signup_id,
                "key_hash": key_hash,
                "key_suffix": api_key[-8:],
                "tier": "explorer",
                "created_at": now_ts(),
                "email_sent": False,
            },
        )

        return api_key

    return reserve_signup(
        transaction
    )


def delete_failed_explorer_signup(
    customer_email: str,
    api_key: str,
) -> None:
    """
    Remove the reserved Explorer signup when email delivery fails.

    This allows the user to try signing up again instead of becoming
    permanently locked out without receiving the key.
    """
    normalized_email = normalize_email(
        customer_email
    )

    signup_id = hash_email(
        normalized_email
    )

    key_hash = hash_api_key(
        api_key
    )

    batch = db.batch()

    batch.delete(
        db.collection("api_keys")
        .document(key_hash)
    )

    batch.delete(
        db.collection("explorer_signups")
        .document(signup_id)
    )

    batch.commit()


def mark_explorer_email_sent(
    customer_email: str,
) -> None:
    signup_id = hash_email(
        customer_email
    )

    db.collection(
        "explorer_signups"
    ).document(
        signup_id
    ).update(
        {
            "email_sent": True,
            "email_sent_at": now_ts(),
        }
    )


def get_key_info(
    api_key: str,
) -> Optional[Dict[str, Any]]:
    key_hash = hash_api_key(api_key)

    doc = (
        db.collection("api_keys")
        .document(key_hash)
        .get()
    )

    if not doc.exists:
        return None

    data = doc.to_dict() or {}
    data["key_hash"] = key_hash

    return data


def increment_usage(
    key_hash: str,
) -> None:
    db.collection(
        "api_keys"
    ).document(
        key_hash
    ).update(
        {
            "used": firestore.Increment(1),
            "last_used": now_ts(),
        }
    )


def deactivate_key_hash(
    key_hash: str,
) -> None:
    db.collection(
        "api_keys"
    ).document(
        key_hash
    ).update(
        {
            "active": False,
        }
    )


def deactivate_keys_for_subscription(
    subscription_id: Optional[str],
    customer_id: Optional[str],
) -> None:
    query = None

    if subscription_id:
        query = db.collection(
            "api_keys"
        ).where(
            "subscription_id",
            "==",
            subscription_id,
        )

    elif customer_id:
        query = db.collection(
            "api_keys"
        ).where(
            "customer_id",
            "==",
            customer_id,
        )

    if query is None:
        return

    for doc in query.stream():
        doc.reference.update(
            {
                "active": False,
            }
        )


def is_subscription_active(
    subscription_id: Optional[str],
    customer_id: Optional[str],
    tier: Optional[str] = None,
) -> bool:
    normalized_tier = str(
        tier or ""
    ).strip().lower()

    # Explorer access is not managed by Stripe.
    if normalized_tier == "explorer":
        return True

    if not STRIPE_SECRET_KEY:
        return True

    try:
        if subscription_id:
            subscription = (
                stripe.Subscription.retrieve(
                    subscription_id
                )
            )

            status = subscription["status"]

        elif customer_id:
            subscriptions = (
                stripe.Subscription.list(
                    customer=customer_id,
                    limit=1,
                ).data
            )

            if not subscriptions:
                return False

            status = subscriptions[0][
                "status"
            ]

        else:
            return False

    except Exception as exc:
        print(
            "Stripe subscription check failed:",
            exc,
        )

        return False

    return status in {
        "active",
        "trialing",
        "past_due",
    }


def require_api_key(
    api_key: str,
) -> Dict[str, Any]:
    info = get_key_info(api_key)

    if not info or not info.get("active"):
        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid or inactive API key"
            ),
        )

    used = int(
        info.get("used", 0)
    )

    limit = int(
        info.get("quota_limit", 0)
    )

    if limit <= 0:
        raise HTTPException(
            status_code=403,
            detail=(
                "API key has no configured quota"
            ),
        )

    if used >= limit:
        raise HTTPException(
            status_code=429,
            detail={
                "message": (
                    "API quota exceeded"
                ),
                "tier": info.get("tier"),
                "quota_limit": limit,
                "used": used,
                "remaining": 0,
                "upgrade_url": (
                    f"{PUBLIC_SITE_URL}/pricing"
                ),
            },
        )

    if not is_subscription_active(
        subscription_id=info.get(
            "subscription_id"
        ),
        customer_id=info.get(
            "customer_id"
        ),
        tier=info.get("tier"),
    ):
        deactivate_key_hash(
            info["key_hash"]
        )

        raise HTTPException(
            status_code=402,
            detail="Subscription inactive",
        )

    info["used"] = used
    info["quota_limit"] = limit
    info["quota_remaining"] = max(
        limit - used,
        0,
    )

    return info


def create_stripe_checkout_session(
    req: CheckoutRequest,
) -> str:
    if not STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=500,
            detail="Stripe not configured",
        )

    customer_email = validate_email(
        req.customer_email
    )

    tier = str(
        req.tier or ""
    ).strip().lower()

    if tier not in PRICE_BY_TIER:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown tier: {tier}",
        )

    price_id = PRICE_BY_TIER.get(tier)

    if not price_id:
        raise HTTPException(
            status_code=500,
            detail=(
                "Stripe price ID not configured "
                f"for {tier}"
            ),
        )

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            success_url=SUCCESS_URL,
            cancel_url=CANCEL_URL,
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            customer_email=customer_email,
            metadata={
                "tqnn_tier": tier,
            },
            subscription_data={
                "metadata": {
                    "tqnn_tier": tier,
                    "customer_email": (
                        customer_email
                    ),
                }
            },
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Stripe error: {exc}",
        ) from exc

    if not session.url:
        raise HTTPException(
            status_code=500,
            detail=(
                "Stripe did not return "
                "a checkout URL"
            ),
        )

    return session.url


def normalize_mode(
    mode: Optional[str],
) -> str:
    normalized = str(
        mode or "ANY"
    ).strip().upper()

    allowed_modes = {
        "EEG",
        "FINANCE",
        "TABULAR",
        "IMAGE",
        "ANY",
    }

    if normalized not in allowed_modes:
        supported = ", ".join(
            sorted(allowed_modes)
        )

        raise HTTPException(
            status_code=422,
            detail=(
                f"Unsupported mode '{normalized}'. "
                f"Supported modes: {supported}."
            ),
        )

    return normalized


def build_core_payload(
    req: RunAnyRequest,
) -> Dict[str, Any]:
    metadata = dict(
        req.metadata or {}
    )

    if req.sfreq is not None:
        metadata["sfreq"] = req.sfreq

    return {
        "data": req.data,
        "mode": normalize_mode(
            req.mode
        ),
        "task": req.task,
        "label": req.label,
        "metadata": metadata,
    }


def validate_core_response(
    result: Any,
) -> Dict[str, Any]:
    """
    Confirm that the private core returned the v2 contract before
    exposing it through the public API.
    """
    if not isinstance(result, dict):
        raise HTTPException(
            status_code=502,
            detail=(
                "Private core returned an invalid "
                "response object"
            ),
        )

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
        required_fields.difference(
            result.keys()
        )
    )

    if missing_fields:
        raise HTTPException(
            status_code=502,
            detail={
                "message": (
                    "Private core response does not "
                    "match the TQNN v2 contract"
                ),
                "missing_fields": (
                    missing_fields
                ),
            },
        )

    return result


# ======================================================
# FASTAPI
# ======================================================

app = FastAPI(
    title=(
        "TQNN Fault-Tolerant "
        "Inference API"
    ),
    description=(
        "Confidence-aware inference for structured data "
        "under noisy, incomplete, or degraded conditions."
    ),
    version="2.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tqnnlabs.com",
        "https://www.tqnnlabs.com",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "OPTIONS",
    ],
    allow_headers=[
        "Content-Type",
        "x-api-key",
        "Stripe-Signature",
    ],
)


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "message": (
            "TQNN Fault-Tolerant "
            "Inference API is online"
        ),
        "platform": "TQNN",
        "api_version": "2.0.0",
        "inference_endpoint": "/run/any",
        "explorer_signup": (
            "/signup/explorer"
        ),
        "docs": "/docs",
        "health": "/health",
        "store": "/store",
        "checkout_get": (
            "/billing/checkout/{tier}"
            "?customer_email=you@example.com"
        ),
        "checkout_post": (
            "/billing/checkout"
        ),
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": (
            "TQNN Fault-Tolerant "
            "Inference API"
        ),
        "api_version": "2.0.0",
        "core_configured": bool(
            CORE_URL
        ),
        "internal_core_secret": bool(
            INTERNAL_CORE_SECRET
        ),
        "firestore": "enabled",
        "email": bool(
            SENDGRID_API_KEY
        ),
        "stripe": bool(
            STRIPE_SECRET_KEY
        ),
        "explorer_enabled": True,
        "explorer_quota": (
            TIER_LIMITS["explorer"]
        ),
        "tier1_price": bool(
            STRIPE_PRICE_TIER1
        ),
        "tier2_price": bool(
            STRIPE_PRICE_TIER2
        ),
        "tier3_price": bool(
            STRIPE_PRICE_TIER3
        ),
    }


# ======================================================
# EXPLORER SIGNUP
# ======================================================

@app.post(
    "/signup/explorer",
    status_code=201,
)
def signup_explorer(
    req: ExplorerSignupRequest,
) -> Dict[str, Any]:
    """
    Issue one free Explorer API key per email address.

    The raw API key is delivered by email and is never returned in
    the HTTP response.
    """
    if not SENDGRID_API_KEY:
        raise HTTPException(
            status_code=503,
            detail=(
                "Explorer signup is temporarily "
                "unavailable because email delivery "
                "is not configured"
            ),
        )

    customer_email = validate_email(
        req.customer_email
    )

    api_key = create_explorer_api_key(
        customer_email
    )

    try:
        send_api_key_email(
            to_email=customer_email,
            api_key=api_key,
            tier="explorer",
        )

        mark_explorer_email_sent(
            customer_email
        )

    except Exception as exc:
        print(
            "Explorer email delivery failed:",
            exc,
        )

        try:
            delete_failed_explorer_signup(
                customer_email=customer_email,
                api_key=api_key,
            )

        except Exception as cleanup_exc:
            print(
                "Explorer signup cleanup failed:",
                cleanup_exc,
            )

        raise HTTPException(
            status_code=503,
            detail=(
                "The Explorer key could not be "
                "delivered. Please try again."
            ),
        ) from exc

    print(
        "Explorer key issued:",
        customer_email,
        api_key[-8:],
    )

    return {
        "created": True,
        "tier": "explorer",
        "quota_limit": (
            TIER_LIMITS["explorer"]
        ),
        "message": (
            "Your TQNN Explorer API key "
            "has been sent by email."
        ),
    }


# ======================================================
# INFERENCE
# ======================================================

@app.post(
    "/run/any",
    response_model=RunResponse,
)
def run_any(
    req: RunAnyRequest,
    x_api_key: str = Header(
        ...,
        alias="x-api-key",
    ),
) -> Dict[str, Any]:
    """
    Run an inference request through the private TQNN core.

    Usage is counted only after the core returns a valid v2 response.
    """
    key_info = require_api_key(
        x_api_key
    )

    if not CORE_URL:
        raise HTTPException(
            status_code=500,
            detail=(
                "CORE_URL not configured"
            ),
        )

    if not INTERNAL_CORE_SECRET:
        raise HTTPException(
            status_code=500,
            detail=(
                "INTERNAL_CORE_SECRET "
                "not configured"
            ),
        )

    payload = build_core_payload(
        req
    )

    try:
        core_response = requests.post(
            f"{CORE_URL}/run-core",
            json=payload,
            headers={
                "x-internal-secret": (
                    INTERNAL_CORE_SECRET
                ),
                "Content-Type": (
                    "application/json"
                ),
            },
            timeout=120,
        )

    except requests.Timeout as exc:
        raise HTTPException(
            status_code=504,
            detail=(
                "Private core timed out"
            ),
        ) from exc

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Private core unreachable: "
                f"{exc}"
            ),
        ) from exc

    if core_response.status_code == 401:
        raise HTTPException(
            status_code=502,
            detail=(
                "Private core rejected "
                "the internal secret"
            ),
        )

    if core_response.status_code == 422:
        try:
            core_error = (
                core_response.json()
            )

        except ValueError:
            core_error = (
                core_response.text
            )

        raise HTTPException(
            status_code=422,
            detail={
                "message": (
                    "Private core rejected "
                    "the inference request"
                ),
                "core_error": core_error,
            },
        )

    if core_response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail={
                "message": (
                    "Private core returned "
                    "an error"
                ),
                "status_code": (
                    core_response.status_code
                ),
                "body": (
                    core_response.text[:2000]
                ),
            },
        )

    try:
        core_result = (
            core_response.json()
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Private core returned "
                "invalid JSON"
            ),
        ) from exc

    result = validate_core_response(
        core_result
    )

    increment_usage(
        key_info["key_hash"]
    )

    return result


# ======================================================
# STORE
# ======================================================

@app.get(
    "/store",
    response_class=HTMLResponse,
)
def tqnn_store() -> HTMLResponse:
    return HTMLResponse(
        """
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8" />
          <meta
            name="viewport"
            content="width=device-width,initial-scale=1"
          />

          <title>TQNN Market</title>
        </head>

        <body style="
          font-family:system-ui;
          background:#050816;
          color:#f9fafb;
          padding:2rem;
        ">
          <h1>TQNN Market</h1>

          <p>
            Choose a Fault-Tolerant
            Inference Platform access tier.
          </p>

          <input
            id="email"
            type="email"
            placeholder="you@example.com"
            style="
              padding:10px;
              min-width:260px;
            "
          />

          <br><br>

          <button onclick="startExplorer()">
            Explorer - 100 free calls
          </button>

          <button onclick="startCheckout('tier1')">
            Starter - $23.99/month
          </button>

          <button onclick="startCheckout('tier2')">
            Builder - $79.99/month
          </button>

          <button onclick="startCheckout('tier3')">
            Scale - $249.99/month
          </button>

          <p id="status"></p>

          <script>
            function getEmail() {
              return document
                .getElementById("email")
                .value
                .trim();
            }

            function setStatus(message) {
              document
                .getElementById("status")
                .textContent = message;
            }

            async function startExplorer() {
              const email = getEmail();

              if (!email) {
                alert("Enter your email first.");
                return;
              }

              setStatus(
                "Creating your Explorer key..."
              );

              try {
                const response = await fetch(
                  "/signup/explorer",
                  {
                    method: "POST",
                    headers: {
                      "Content-Type":
                        "application/json"
                    },
                    body: JSON.stringify({
                      customer_email: email
                    })
                  }
                );

                const data = await response.json();

                if (!response.ok) {
                  const detail = data.detail;

                  if (
                    typeof detail === "string"
                  ) {
                    throw new Error(detail);
                  }

                  throw new Error(
                    detail?.message ||
                    "Explorer signup failed"
                  );
                }

                setStatus(
                  "Success. Check your email " +
                  "for your TQNN API key."
                );

              } catch (error) {
                setStatus(
                  error.message ||
                  "Explorer signup failed."
                );
              }
            }

            function startCheckout(tier) {
              const email = getEmail();

              if (!email) {
                alert("Enter your email first.");
                return;
              }

              window.location.href =
                "/billing/checkout/" +
                encodeURIComponent(tier) +
                "?customer_email=" +
                encodeURIComponent(email);
            }
          </script>
        </body>
        </html>
        """
    )


# ======================================================
# BILLING
# ======================================================

@app.post("/billing/checkout")
def create_checkout(
    req: CheckoutRequest,
) -> Dict[str, str]:
    """
    Create a Stripe Checkout session through JSON.
    """
    checkout_url = (
        create_stripe_checkout_session(
            req
        )
    )

    return {
        "checkout_url": checkout_url,
    }


@app.get("/billing/checkout/{tier}")
def checkout_redirect(
    tier: str,
    customer_email: str = Query(...),
) -> RedirectResponse:
    """
    Browser-friendly Stripe Checkout endpoint.
    """
    checkout_url = (
        create_stripe_checkout_session(
            CheckoutRequest(
                tier=tier,
                customer_email=customer_email,
            )
        )
    )

    return RedirectResponse(
        url=checkout_url,
        status_code=303,
    )


@app.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
) -> Dict[str, Any]:
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=500,
            detail=(
                "Webhook secret "
                "not configured"
            ),
        )

    payload = await request.body()

    signature = request.headers.get(
        "Stripe-Signature",
        "",
    )

    try:
        event = (
            stripe.Webhook.construct_event(
                payload,
                signature,
                STRIPE_WEBHOOK_SECRET,
            )
        )

    except Exception as exc:
        print(
            "Webhook signature verification failed:",
            exc,
        )

        raise HTTPException(
            status_code=400,
            detail="Invalid signature",
        ) from exc

    event_id = event.get("id")

    if not event_id:
        raise HTTPException(
            status_code=400,
            detail="Stripe event ID missing",
        )

    event_reference = (
        db.collection("stripe_events")
        .document(event_id)
    )

    if event_reference.get().exists:
        return {
            "received": True,
            "duplicate": True,
        }

    event_reference.set(
        {
            "received_at": now_ts(),
            "type": event["type"],
        }
    )

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == (
        "checkout.session.completed"
    ):
        customer_id = data.get(
            "customer"
        )

        customer_details = (
            data.get("customer_details")
            or {}
        )

        customer_email = (
            customer_details.get("email")
            or data.get("customer_email")
        )

        if not customer_email:
            print(
                "Stripe checkout completed "
                "without a customer email"
            )

            raise HTTPException(
                status_code=400,
                detail=(
                    "Stripe checkout did not "
                    "include a customer email"
                ),
            )

        customer_email = validate_email(
            customer_email
        )

        tier = (
            data.get("metadata")
            or {}
        ).get(
            "tqnn_tier",
            "tier1",
        )

        tier = str(
            tier
        ).strip().lower()

        if tier not in PRICE_BY_TIER:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Stripe checkout contained "
                    f"an invalid tier: {tier}"
                ),
            )

        subscription_id = data.get(
            "subscription"
        )

        api_key = (
            create_api_key_for_subscription(
                customer_email=customer_email,
                customer_id=customer_id,
                subscription_id=subscription_id,
                tier=tier,
            )
        )

        print(
            "Payment complete:",
            customer_email,
            tier,
        )

        print(
            "NEW TQNN KEY ISSUED:",
            api_key[-8:],
        )

        try:
            send_api_key_email(
                customer_email,
                api_key,
                tier,
            )

        except Exception as exc:
            print(
                "Email send failed:",
                exc,
            )

        if customer_id:
            try:
                stripe.Customer.modify(
                    customer_id,
                    metadata={
                        "tqnn_tier": tier,
                        "tqnn_api_key_suffix": (
                            api_key[-8:]
                        ),
                    },
                )

            except Exception as exc:
                print(
                    (
                        "Could not update Stripe "
                        "customer metadata:"
                    ),
                    exc,
                )

    if event_type in {
        "customer.subscription.deleted",
        "customer.subscription.updated",
    }:
        subscription_id = data.get(
            "id"
        )

        customer_id = data.get(
            "customer"
        )

        status = data.get(
            "status"
        )

        if status in {
            "canceled",
            "unpaid",
            "incomplete_expired",
        }:
            deactivate_keys_for_subscription(
                subscription_id,
                customer_id,
            )

    return {
        "received": True,
    }