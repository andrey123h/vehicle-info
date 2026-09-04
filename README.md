# Vehicle Info

A small FastAPI service that looks up vehicle details by license plate from an
upstream vehicle registry and returns them with a human-readable summary.

## Table of Contents

- [API Exploration](#api-exploration)
- [Live Deployment](#live-deployment)
- [Running Locally](#running-locally)
  - [Requirements](#requirements)
  - [From source](#from-source)
  - [With Docker](#with-docker)
- [API Reference](#api-reference)
  - [`POST /vehicle-info`](#post-vehicle-info)
  - [`GET /health`](#get-health)
- [Project Structure](#project-structure)

## API Exploration

Before building, I explored the upstream vehicle-info API to understand its contract:

1. **Reviewed the API docs** — went through the Swagger UI at
   [`/docs`](https://insurance-webhook-945894769129.us-central1.run.app/docs#/) to understand
   the available endpoint, request schema, and expected response format.
2. **Tested with curl** — sent requests directly against `/vehicle-info` with a few
   different inputs (valid plates, malformed payloads, missing fields) to observe the
   actual behavior of the API.

## Live Deployment

| | |
| --- | --- |
| Base URL | https://vehicle-info-hc14.onrender.com |
| Interactive docs | [/docs](https://vehicle-info-hc14.onrender.com/docs) |
| Hosting | Render |

```bash
curl -X POST https://vehicle-info-hc14.onrender.com/vehicle-info \
  -H "Content-Type: application/json" \
  -d '{"license_plate": "12345678"}'
```

> **Note:** deployed on Render's free tier, so there's a cold start — the first
> request after some idle time might take 30–60s to wake up.

## Running Locally

### Requirements

- Python 3.12+
- Docker (optional)


```bash
git clone https://github.com/andrey123h/vehicle-info
cd vehicle-info
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is then available at `http://localhost:8000`, with docs at
`http://localhost:8000/docs`.

### Docker

```bash
docker build -t vehicle-info .
docker run -p 8080:8080 vehicle-info
```

The API is then available at `http://localhost:8080`.

## API Reference

### `POST /vehicle-info`

Request:

```json
{ "license_plate": "12345678" }
```

Plates may include spaces, hyphens or periods; they are stripped before validation.
A valid plate is 7 or 8 digits.

Response:

```json
{
  "success": true,
  "vehicle": {
    "license_plate": "12345678",
    "manufacturer": "Toyota",
    "model": "Corolla",
    "year": 2020,
    "color": "White"
  },
  "summary": "Toyota Corolla 2020, White (12345678)"
}
```

Errors return `success: false` with an `error_code` and `message`:

| `error_code`           | HTTP | Meaning                                      |
| ---------------------- | ---- | -------------------------------------------- |
| `INVALID_REQUEST`      | 200  | Body is not valid JSON with `license_plate`. |
| `INVALID_PLATE`        | 200  | Plate is not 7 or 8 digits.                  |
| `VEHICLE_NOT_FOUND`    | 200  | Registry has no vehicle for the plate.       |
| `UPSTREAM_TIMEOUT`     | 504  | Registry did not respond in time.            |
| `UPSTREAM_UNAVAILABLE` | 502  | Registry could not be reached.               |
| `UPSTREAM_ERROR`       | 502  | Registry returned an unexpected response.    |

### `GET /health`

Returns `{ "status": "ok" }`.

## Project Structure

```
app/
├── main.py          # App setup and exception handlers
├── routers/         # HTTP routes
├── controllers/     # Request orchestration and response shaping
├── services/        # Upstream registry client and plate validation
├── schemas/         # Pydantic request/response models
└── exceptions.py    # Domain errors mapped to error codes
```
