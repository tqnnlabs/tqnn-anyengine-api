from __future__ import annotations

from fastapi import FastAPI, HTTPException, Header, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Any, Dict, List, Optional
from google.cloud import firestore
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import hashlib
import os
import secrets
import time
import stripe
import requests


# ======================================================
# ENV CONFIG — DO NOT HARDCODE SECRETS
# ======================================================

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

STRIPE_PRICE_TIER1 = os.environ.get("STRIPE_PRICE_TIER1", "")
STRIPE_PRICE_TIER2 = os.environ.get("STRIPE_PRICE_TIER2", "")
STRIPE_PRICE_TIER3 = os.environ.get("STRIPE_PRICE_TIER3", "")

CORE_URL = os.environ.get("CORE_URL", "").rstrip("/")
INTERNAL_CORE_SECRET = os.environ.get("INTERNAL_CORE_SECRET", "")

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "tqnnlabs@gmail.com")

PUBLIC_SITE_URL = os.environ.get("PUBLIC_SITE_URL", "https://tqnnlabs.com").rstrip("/")

SUCCESS_URL = os.environ.get(
    "SUCCESS_URL",
    f"{PUBLIC_SITE_URL}/tqnn-success?session_id={{CHECKOUT_SESSION_ID}}",
)
CANCEL_URL = os.environ.get(
    "CANCEL_URL",
    f"{PUBLIC_SITE_URL}/tqnn-cancel",
)

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

db = firestore.Client()

PRICE_BY_TIER = {
    "tier1": STRIPE_PRICE_TIER1,
    "tier2": STRIPE_PRICE_TIER2,
    "tier3": STRIPE_PRICE_TIER3,
}

TIER_LIMITS = {
    "tier1": 10_000,
    "tier2": 50_000,
    "tier3": 200_000,
}


# ======================================================
# MODELS
# ======================================================

class RunAnyRequest(BaseModel):
    data: Any
    mode: Optional[str] = "ANY"
    label: Optional[str] = None
    sfreq: Optional[float] = None
    metadata: Dict[str, Any] = {}


class RunResponse(BaseModel):
    mode: str
    label: Optional[str]
    probs: List[float]
    threshold: float
    qualia: Dict[str, Any]
    intent: List[float]
    meta: Dict[str, Any]


class CheckoutRequest(BaseModel):
    customer_email: EmailStr
    tier: str = "tier1"


# ======================================================
# HELPERS
# ======================================================

def now_ts() -> float:
    return time.time()


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def generate_api_key() -> str:
    return "TQNN_" + secrets.token_urlsafe(32)


def send_api_key_email(to_email: str, api_key: str, tier: str) -> None:
    if not SENDGRID_API_KEY:
        print("SENDGRID_API_KEY missing. API key was created but email was not sent.")
        return

    subject = "Your TQNN AnyEngine API Key"

    html = f"""
    <div style="font-family:Arial,sans-serif;line-height:1.5;">
      <h2>Welcome to TQNN Labs</h2>
      <p>Your TQNN AnyEngine runtime access is active.</p>

      <p><b>Tier:</b> {tier}</p>

      <p><b>Your API key:</b></p>
      <pre style="background:#f4f4f4;padding:12px;border-radius:8px;">{api_key}</pre>

      <p>Example:</p>
      <pre style="background:#f4f4f4;padding:12px;border-radius:8px;">
curl -X POST https://api.tqnnlabs.com/run/any \\
  -H "Content-Type: application/json" \\
  -H "x-api-key: {api_key}" \\
  -d '{{"data":[1,2,3,4],"mode":"ANY","label":"test"}}'
      </pre>

      <p>Keep this key private. Do not publish it or commit it to GitHub.</p>

      <p>— TQNN Labs</p>
    </div>
    """

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html,
    )

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    sg.send(message)


def create_api_key_for_subscription(
    customer_email: str,
    customer_id: Optional[str],
    subscription_id: Optional[str],
    tier: str,
) -> str:
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)
    quota_limit = TIER_LIMITS.get(tier, 10_000)

    db.collection("api_keys").document(key_hash).set(
        {
            "key_hash": key_hash,
            "key_suffix": api_key[-8:],
            "customer_email": customer_email,
            "customer_id": customer_id,
            "subscription_id": subscription_id,
            "tier": tier,
            "used": 0,
            "quota_limit": quota_limit,
            "created_at": now_ts(),
            "last_used": now_ts(),
            "active": True,
        }
    )

    return api_key


def get_key_info(api_key: str) -> Optional[Dict[str, Any]]:
    key_hash = hash_api_key(api_key)
    doc = db.collection("api_keys").document(key_hash).get()

    if not doc.exists:
        return None

    data = doc.to_dict() or {}
    data["key_hash"] = key_hash
    return data


def increment_usage(key_hash: str) -> None:
    db.collection("api_keys").document(key_hash).update(
        {
            "used": firestore.Increment(1),
            "last_used": now_ts(),
        }
    )


def deactivate_key_hash(key_hash: str) -> None:
    db.collection("api_keys").document(key_hash).update({"active": False})


def deactivate_keys_for_subscription(
    subscription_id: Optional[str],
    customer_id: Optional[str],
) -> None:
    query = None

    if subscription_id:
        query = db.collection("api_keys").where("subscription_id", "==", subscription_id)
    elif customer_id:
        query = db.collection("api_keys").where("customer_id", "==", customer_id)

    if not query:
        return

    for doc in query.stream():
        doc.reference.update({"active": False})


def is_subscription_active(
    subscription_id: Optional[str],
    customer_id: Optional[str],
) -> bool:
    if not STRIPE_SECRET_KEY:
        return True

    try:
        if subscription_id:
            sub = stripe.Subscription.retrieve(subscription_id)
            status = sub["status"]
        elif customer_id:
            subs = stripe.Subscription.list(customer=customer_id, limit=1).data
            if not subs:
                return False
            status = subs[0]["status"]
        else:
            return False
    except Exception as e:
        print("Stripe subscription check failed:", e)
        return False

    return status in ("active", "trialing", "past_due")


def require_api_key(api_key: str) -> Dict[str, Any]:
    info = get_key_info(api_key)

    if not info or not info.get("active"):
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")

    used = int(info.get("used", 0))
    limit = int(info.get("quota_limit", 0))

    if used >= limit:
        raise HTTPException(status_code=402, detail="API quota exceeded")

    if not is_subscription_active(
        info.get("subscription_id"),
        info.get("customer_id"),
    ):
        deactivate_key_hash(info["key_hash"])
        raise HTTPException(status_code=402, detail="Subscription inactive")

    return info


def create_stripe_checkout_session(req: CheckoutRequest) -> str:
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    tier = req.tier.lower().strip()
    price_id = PRICE_BY_TIER.get(tier)

    if tier not in PRICE_BY_TIER:
        raise HTTPException(status_code=400, detail=f"Unknown tier: {tier}")

    if not price_id:
        raise HTTPException(status_code=500, detail=f"Stripe price ID not configured for {tier}")

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            success_url=SUCCESS_URL,
            cancel_url=CANCEL_URL,
            line_items=[{"price": price_id, "quantity": 1}],
            customer_email=str(req.customer_email),
            metadata={"tqnn_tier": tier},
            subscription_data={
                "metadata": {
                    "tqnn_tier": tier,
                    "customer_email": str(req.customer_email),
                }
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {e}")

    if not session.url:
        raise HTTPException(status_code=500, detail="Stripe did not return a checkout URL")

    return session.url


# ======================================================
# FASTAPI
# ======================================================

app = FastAPI(title="TQNN AnyEngine API", version="1.0.1")

# CORS is useful for the JS checkout version and future browser sandbox.
# The GET redirect checkout route below works even without CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tqnnlabs.com",
        "https://www.tqnnlabs.com",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "x-api-key", "Stripe-Signature"],
)


@app.get("/")
def root():
    return {
        "message": "TQNN AnyEngine API is online",
        "docs": "/docs",
        "health": "/health",
        "store": "/store",
        "checkout_get": "/billing/checkout/{tier}?customer_email=you@example.com",
        "checkout_post": "/billing/checkout",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "TQNN AnyEngine API",
        "core_configured": bool(CORE_URL),
        "firestore": "enabled",
        "email": bool(SENDGRID_API_KEY),
        "stripe": bool(STRIPE_SECRET_KEY),
        "tier1_price": bool(STRIPE_PRICE_TIER1),
        "tier2_price": bool(STRIPE_PRICE_TIER2),
        "tier3_price": bool(STRIPE_PRICE_TIER3),
    }


@app.post("/run/any", response_model=RunResponse)
def run_any(
    req: RunAnyRequest,
    x_api_key: str = Header(..., alias="x-api-key"),
):
    key_info = require_api_key(x_api_key)

    if not CORE_URL:
        raise HTTPException(status_code=500, detail="CORE_URL not configured")

    mode = (req.mode or "ANY").upper()

    metadata = dict(req.metadata or {})
    if req.sfreq is not None:
        metadata["sfreq"] = req.sfreq

    payload = {
        "data": req.data,
        "mode": mode,
        "label": req.label,
        "metadata": metadata,
    }

    try:
        core_res = requests.post(
            f"{CORE_URL}/run-core",
            json=payload,
            headers={
                "x-internal-secret": INTERNAL_CORE_SECRET,
                "Content-Type": "application/json",
            },
            timeout=120,
        )
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Private core timed out")
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Private core unreachable: {e}")

    if core_res.status_code == 401:
        raise HTTPException(status_code=502, detail="Private core rejected internal secret")

    if core_res.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Private core returned an error",
                "status_code": core_res.status_code,
                "body": core_res.text,
            },
        )

    try:
        result = core_res.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Private core returned invalid JSON")

    increment_usage(key_info["key_hash"])

    return RunResponse(
        mode=str(result.get("mode", mode)),
        label=result.get("label", req.label),
        probs=list(result.get("probs", [])),
        threshold=float(result.get("threshold", 0.0)),
        qualia=dict(result.get("qualia", {})),
        intent=list(result.get("intent", [])),
        meta=dict(result.get("meta", {})),
    )


@app.get("/store", response_class=HTMLResponse)
def tqnn_store():
    return HTMLResponse(
        """
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8" />
          <title>TQNN Market</title>
        </head>
        <body style="font-family:system-ui;background:#050816;color:#f9fafb;padding:2rem;">
          <h1>TQNN Market</h1>
          <p>Choose a runtime access tier.</p>

          <input id="email" placeholder="you@example.com" style="padding:10px;min-width:260px;">
          <br><br>

          <button onclick="startCheckout('tier1')">Starter - $23.99/month</button>
          <button onclick="startCheckout('tier2')">Builder - $79.99/month</button>
          <button onclick="startCheckout('tier3')">Scale - $249.99/month</button>

          <p id="status"></p>

          <script>
            function startCheckout(tier) {
              const email = document.getElementById("email").value.trim();
              if (!email) {
                alert("Enter your email first.");
                return;
              }

              window.location.href =
                "/billing/checkout/" + encodeURIComponent(tier) +
                "?customer_email=" + encodeURIComponent(email);
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
def create_checkout(req: CheckoutRequest):
    """
    JSON checkout endpoint.

    Body:
    {
      "customer_email": "dev@example.com",
      "tier": "tier1"
    }

    Returns:
    {
      "checkout_url": "https://checkout.stripe.com/..."
    }
    """
    checkout_url = create_stripe_checkout_session(req)
    return {"checkout_url": checkout_url}


@app.get("/billing/checkout/{tier}")
def checkout_redirect(
    tier: str,
    customer_email: EmailStr = Query(...),
):
    """
    Browser-friendly checkout endpoint.

    This avoids frontend CORS/fetch issues:
    https://.../billing/checkout/tier1?customer_email=dev@example.com

    It redirects the browser straight to Stripe Checkout.
    """
    checkout_url = create_stripe_checkout_session(
        CheckoutRequest(
            tier=tier,
            customer_email=customer_email,
        )
    )
    return RedirectResponse(url=checkout_url, status_code=303)


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    payload = await request.body()
    sig = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        print("Webhook signature verification failed:", e)
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_id = event.get("id")
    event_ref = db.collection("stripe_events").document(event_id)

    if event_ref.get().exists:
        return {"received": True, "duplicate": True}

    event_ref.set({"received_at": now_ts(), "type": event["type"]})

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        customer_id = data.get("customer")
        customer_email = (data.get("customer_details", {}) or {}).get("email", "unknown")
        tier = (data.get("metadata") or {}).get("tqnn_tier", "tier1")
        subscription_id = data.get("subscription")

        api_key = create_api_key_for_subscription(
            customer_email=customer_email,
            customer_id=customer_id,
            subscription_id=subscription_id,
            tier=tier,
        )

        print("Payment complete:", customer_email, tier)
        print("NEW TQNN KEY ISSUED:", api_key[-8:])

        try:
            send_api_key_email(customer_email, api_key, tier)
        except Exception as e:
            print("Email send failed:", e)

        if customer_id:
            try:
                stripe.Customer.modify(
                    customer_id,
                    metadata={
                        "tqnn_tier": tier,
                        "tqnn_api_key_suffix": api_key[-8:],
                    },
                )
            except Exception as e:
                print("Could not update Stripe customer metadata:", e)

    if event_type in ("customer.subscription.deleted", "customer.subscription.updated"):
        sub_id = data.get("id")
        customer_id = data.get("customer")
        status = data.get("status")

        if status in ("canceled", "unpaid", "incomplete_expired"):
            deactivate_keys_for_subscription(sub_id, customer_id)

    return {"received": True}
    
