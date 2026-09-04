# Vehicle Info API — Part A

A thin, well-separated wrapper around the insurance company's vehicle registry stub,
shaped for use as an **API node** in the Insait conversation flow.

## Layout

```
app/
├── main.py                        FastAPI app, mounts routers, exception handlers
├── routers/vehicle.py             POST /vehicle-info, GET /health
├── controllers/vehicle_controller.py   calls the service, shapes the response
├── services/vehicle_service.py    validates the plate, calls the registry
├── schemas/vehicle.py             pydantic models
└── exceptions.py                  VehicleNotFoundError, InvalidPlateError, ...
```

## Endpoints

`GET /health` → `{"status": "ok"}`
`GET /docs` → Swagger UI

`POST /vehicle-info` with `{"license_plate": "12345678"}`

Success (200):
```json
{
  "success": true,
  "vehicle": {
    "license_plate": "12345678",
    "manufacturer": "טויוטה",
    "model": "קורולה",
    "year": 2020,
    "color": "לבן"
  },
  "summary": "טויוטה קורולה 2020, לבן (12345678)"
}
```

Failure:
```json
{"success": false, "error_code": "VEHICLE_NOT_FOUND", "message": "No vehicle found for license plate 99999999."}
```

| error_code | HTTP | When |
|---|---|---|
| `INVALID_PLATE` | 200 | Not 7–8 digits |
| `INVALID_REQUEST` | 200 | Malformed or missing body |
| `VEHICLE_NOT_FOUND` | 200 | Upstream 404 |
| `UPSTREAM_TIMEOUT` | 504 | No answer within `UPSTREAM_TIMEOUT` seconds |
| `UPSTREAM_UNAVAILABLE` | 502 | Connection failure |
| `UPSTREAM_ERROR` | 502 | Unexpected upstream status or payload |

## Design decisions

- **Business outcomes return 200, infrastructure failures return 5xx.** A bad plate or an
  unknown vehicle is a normal conversational outcome — the flow reads `success` / `error_code`
  from the payload and re-asks. Only a genuinely broken upstream takes the API node's error
  path, so "vehicle not found" and "the registry is down" never get the same handling.
- **One response shape, always** — including malformed bodies, which FastAPI would otherwise
  answer with a pydantic error array. The flow parses one structure, never two.
- **Validate before the network call.** Saves a round trip and gives one consistent English
  message instead of the upstream's Hebrew pydantic error.
- **Plate normalization.** `12-345-678` and `12 345 678` are accepted; separators are stripped
  before validation, so a naturally typed plate isn't rejected.
- **Vehicle data passes through in Hebrew** — that's what the registry returns; no invented
  translation layer. `summary` is a pre-formatted line the flow's confirmation step can speak.

## Run locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8080
```

## Deploy to Cloud Run

```bash
gcloud run deploy vehicle-info-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

Env vars: `VEHICLE_SERVICE_URL`, `UPSTREAM_TIMEOUT` (seconds, default 10).
