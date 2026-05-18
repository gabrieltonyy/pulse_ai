import asyncio
import json
import os
import time

import httpx

BASE = os.getenv("PULSE_BASE_URL", "http://localhost:8000")


def event_name(ranked_event):
    return (ranked_event.get("event") or {}).get("title")


async def post_json(client, path, payload):
    start = time.perf_counter()
    response = await client.post(f"{BASE}{path}", json=payload)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    body = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
    events = body.get("events") or []
    return {
        "path": path,
        "status": response.status_code,
        "content_type": response.headers.get("content-type"),
        "elapsed_ms": elapsed_ms,
        "event_count": len(events),
        "first3": [event_name(event) for event in events[:3]],
        "workflow_trace": bool(body.get("workflow_trace")),
        "provider": next((step.get("provider") for step in body.get("workflow_trace", []) if step.get("node_name") == "search_events"), None),
    }


async def main():
    out = {}
    async with httpx.AsyncClient(timeout=90.0) as client:
        start = time.perf_counter()
        response = await client.get(f"{BASE}/health")
        out["health"] = {
            "status": response.status_code,
            "content_type": response.headers.get("content-type"),
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 2),
            "body": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text[:120],
        }

        live_payloads = [
            {
                "label": "live Berlin electronic music",
                "payload": {
                    "query": "Find electronic music events in Berlin this weekend under $100",
                    "city": "Berlin",
                    "country": "DE",
                    "category": "Music",
                    "date_from": "2026-05-18",
                    "date_to": "2026-06-17",
                    "budget_max": 100,
                    "use_demo": False,
                },
            },
            {
                "label": "live concerts New York",
                "payload": {
                    "query": "concerts in New York this month",
                    "city": "New York",
                    "country": "US",
                    "category": "Music",
                    "date_from": "2026-05-18",
                    "date_to": "2026-06-17",
                    "use_demo": False,
                },
            },
            {
                "label": "live football London",
                "payload": {
                    "query": "football matches in London this weekend",
                    "city": "London",
                    "country": "GB",
                    "category": "Sports",
                    "date_from": "2026-05-18",
                    "date_to": "2026-06-17",
                    "use_demo": False,
                },
            },
        ]
        out["json_searches"] = []
        for item in live_payloads:
            result = await post_json(client, "/api/search/", item["payload"])
            result["label"] = item["label"]
            out["json_searches"].append(result)

        demo = await post_json(client, "/api/search/", {
            "query": "Find electronic music events in Berlin this weekend under $100",
            "city": "Berlin",
            "country": "DE",
            "category": "Music",
            "date_from": "2026-05-18",
            "date_to": "2026-06-17",
            "budget_max": 100,
            "use_demo": True,
        })
        demo["label"] = "demo Berlin electronic music"
        out["json_searches"].append(demo)

        start = time.perf_counter()
        response = await client.post(
            f"{BASE}/api/search/htmx",
            headers={"HX-Request": "true", "Accept": "text/html"},
            data={
                "query": "Find electronic music events in Berlin this weekend under $100",
                "city": "Berlin",
                "category": "Music",
                "date_from": "2026-05-18",
                "date_to": "2026-06-17",
            },
        )
        text = response.text
        out["htmx"] = {
            "status": response.status_code,
            "content_type": response.headers.get("content-type"),
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 2),
            "looks_like_html": "<" in text[:80],
            "starts_raw_json": text.lstrip().startswith(("{", "[")),
            "contains_pre": "<pre" in text.lower(),
            "snippet": text[:160],
        }

    print(json.dumps(out, indent=2, default=str))


asyncio.run(main())
