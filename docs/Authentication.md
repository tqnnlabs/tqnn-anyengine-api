# Authentication

The TQNN API uses API key authentication for all protected endpoints.

Every inference request must include a valid API key in the request headers.

---

# API Key Header

Include your API key using the following header:

```http
x-api-key: YOUR_TQNN_API_KEY
```

Example:

```http
POST /run/any HTTP/1.1
Host: api.tqnnlabs.com

Content-Type: application/json
x-api-key: TQNN_xxxxxxxxxxxxxxxxx
```

---

# Obtaining an API Key

API keys are issued automatically after purchasing an active subscription through the TQNN Labs billing portal.

Each subscription is associated with a unique API key.

---

# API Key Scope

An API key grants access according to the associated subscription plan.

Depending on the plan, limits may include:

- Monthly inference requests
- Rate limits
- Feature availability

Usage is tracked automatically by the platform.

---

# Protecting Your API Key

Treat your API key like a password.

Recommended practices:

- Store keys in environment variables.
- Never commit keys to source control.
- Never embed keys in public client-side applications.
- Rotate keys if you suspect they have been exposed.

Example:

```python
import os

API_KEY = os.getenv("TQNN_API_KEY")
```

---

# Example Request

```bash
curl -X POST https://api.tqnnlabs.com/run/any \
-H "Content-Type: application/json" \
-H "x-api-key: YOUR_API_KEY" \
-d '{
  "data":[[1.2,0.5,3.1]],
  "mode":"TABULAR",
  "task":"fault_diagnosis"
}'
```

---

# Authentication Errors

## 401 Unauthorized

Returned when:

- The API key is missing.
- The API key is invalid.
- The API key has been revoked.

Example response:

```json
{
  "detail": "Invalid API key"
}
```

---

## 403 Forbidden

Returned when:

- The API key does not have permission to access the requested resource.

---

## 429 Too Many Requests

Returned when:

- Subscription limits or rate limits have been exceeded.

---

# Environment Variables

For local development, store credentials in environment variables.

Example:

```bash
export TQNN_API_KEY="YOUR_API_KEY"
```

Python:

```python
import os

API_KEY = os.getenv("TQNN_API_KEY")
```

---

# Security Best Practices

- Keep API keys private.
- Use HTTPS for all requests.
- Rotate compromised keys immediately.
- Store secrets using your deployment platform's secret manager or environment variables.
- Never share API keys publicly.

---

# Internal Authentication

The public TQNN API authenticates client requests using `x-api-key`.

Communication between the public API and the private TQNN Core uses a separate internal secret that is never exposed to API users.