import asyncio
import json
import os

import httpx
from dotenv import load_dotenv

load_dotenv(".env")

START_UTC = "2026-05-18T00:00:00Z"
END_UTC = "2026-06-17T23:59:59Z"


def event_summary(event):
    venue = (((event.get("_embedded") or {}).get("venues") or [{}])[0]).get("name")
    start = (event.get("dates") or {}).get("start") or {}
    return {
        "name": event.get("name"),
        "date": start.get("dateTime") or start.get("localDate"),
        "venue": venue,
    }


def feature_name(feature):
    props = feature.get("properties") or {}
    return props.get("name") or props.get("formatted") or props.get("city")


async def main():
    out = {"ticketmaster": [], "eventbrite": {}, "geoapify": {}, "openweather": {}, "watsonx": {}}

    async with httpx.AsyncClient(timeout=20.0) as client:
        tm_key = os.getenv("TICKETMASTER_API_KEY")
        tm_base = os.getenv("TICKETMASTER_BASE_URL", "https://app.ticketmaster.com/discovery/v2")
        tm_cases = [
            ("electronic music in Berlin", {"keyword": "electronic music", "city": "Berlin", "countryCode": "DE"}),
            ("football in London", {"keyword": "football", "city": "London", "countryCode": "GB"}),
            ("concerts in New York", {"keyword": "concerts", "city": "New York", "countryCode": "US"}),
        ]
        for label, params in tm_cases:
            safe_params = {
                **params,
                "source": "ticketmaster",
                "size": 10,
                "sort": "date,asc",
                "startDateTime": START_UTC,
                "endDateTime": END_UTC,
            }
            try:
                response = await client.get(
                    f"{tm_base}/events.json",
                    params={**safe_params, "apikey": tm_key},
                )
                data = response.json() if response.content else {}
                events = ((data.get("_embedded") or {}).get("events") or [])
                out["ticketmaster"].append({
                    "label": label,
                    "status": response.status_code,
                    "params": safe_params,
                    "count": len(events),
                    "first3": [event_summary(event) for event in events[:3]],
                })
            except Exception as exc:
                out["ticketmaster"].append({"label": label, "error": type(exc).__name__})

        eb_key = os.getenv("EVENTBRITE_API_KEY")
        eb_enabled = os.getenv("EVENTBRITE_ENABLED", "").lower() in {"1", "true", "yes", "on"}
        eb_headers = {"Authorization": f"Bearer {eb_key}"} if eb_key else {}
        out["eventbrite"]["enabled"] = eb_enabled
        out["eventbrite"]["generic_search"] = (
            "skipped: public Search Events is deprecated; generic runtime discovery uses Ticketmaster"
        )
        if eb_enabled and eb_key:
            for name, url in [
                ("me", "https://www.eventbriteapi.com/v3/users/me/"),
                ("organizations", "https://www.eventbriteapi.com/v3/users/me/organizations/"),
            ]:
                try:
                    response = await client.get(url, headers=eb_headers)
                    body = response.json() if response.content else {}
                    out["eventbrite"][name] = {
                        "status": response.status_code,
                        "count": len(body.get("organizations") or []) if name == "organizations" else None,
                        "id_present": bool(body.get("id")) if name == "me" else None,
                    }
                except Exception as exc:
                    out["eventbrite"][name] = {"error": type(exc).__name__}

            org_id = os.getenv("EVENTBRITE_ORG_ID")
            venue_id = os.getenv("EVENTBRITE_VENUE_ID")
            out["eventbrite"]["org_id_present"] = bool(org_id)
            out["eventbrite"]["venue_id_present"] = bool(venue_id)
            if org_id:
                try:
                    response = await client.get(
                        f"https://www.eventbriteapi.com/v3/organizations/{org_id}/events/",
                        headers=eb_headers,
                        params={"status": "live", "page_size": 50},
                    )
                    body = response.json() if response.content else {}
                    events = body.get("events") or []
                    filtered = [
                        event for event in events
                        if START_UTC <= (event.get("start") or {}).get("utc", "") <= END_UTC
                    ]
                    out["eventbrite"]["org_events"] = {
                        "status": response.status_code,
                        "count": len(filtered),
                        "first3": [
                            {
                                "name": (event.get("name") or {}).get("text"),
                                "date": (event.get("start") or {}).get("utc"),
                                "venue_id": event.get("venue_id"),
                            }
                            for event in filtered[:3]
                        ],
                    }
                except Exception as exc:
                    out["eventbrite"]["org_events"] = {"error": type(exc).__name__}
            if venue_id:
                out["eventbrite"]["venue_events"] = {
                    "status": "skipped",
                    "note": "Use org events and local venue_id filtering when org scope is available.",
                }
        else:
            out["eventbrite"]["auth"] = "skipped: Eventbrite disabled or key missing"

        geo_key = os.getenv("GEOAPIFY_API_KEY")
        try:
            response = await client.get(
                "https://api.geoapify.com/v1/geocode/search",
                params={"apiKey": geo_key, "text": "Berlin", "type": "city", "filter": "countrycode:de", "limit": 1},
            )
            body = response.json() if response.content else {}
            features = body.get("features") or []
            out["geoapify"]["geocode_berlin"] = {
                "status": response.status_code,
                "count": len(features),
                "samples": [feature_name(feature) for feature in features[:3]],
            }
            coords = (features[0].get("geometry") or {}).get("coordinates") if features else [13.405, 52.52]
            lon, lat = coords[0], coords[1]
            response = await client.get(
                "https://api.geoapify.com/v2/places",
                params={
                    "apiKey": geo_key,
                    "categories": "catering.restaurant,entertainment,public_transport,parking",
                    "filter": f"circle:{lon},{lat},3000",
                    "bias": f"proximity:{lon},{lat}",
                    "limit": 10,
                },
            )
            body = response.json() if response.content else {}
            places = body.get("features") or []
            out["geoapify"]["places_berlin"] = {
                "status": response.status_code,
                "count": len(places),
                "samples": [feature_name(feature) for feature in places[:5]],
            }
        except Exception as exc:
            out["geoapify"]["error"] = type(exc).__name__

        ow_key = os.getenv("OPENWEATHER_API_KEY")
        try:
            response = await client.get(
                "https://api.openweathermap.org/data/2.5/forecast",
                params={"appid": ow_key, "lat": 52.52, "lon": 13.405, "units": "metric"},
            )
            body = response.json() if response.content else {}
            items = body.get("list") or []
            first = items[0] if items else {}
            last = items[-1] if items else {}
            out["openweather"]["berlin_forecast"] = {
                "status": response.status_code,
                "count": len(items),
                "first": {
                    "dt_txt": first.get("dt_txt"),
                    "temp": (first.get("main") or {}).get("temp"),
                    "condition": ((first.get("weather") or [{}])[0]).get("main"),
                },
                "last_dt_txt": last.get("dt_txt"),
                "horizon_note": "5-day / 3-hour forecast only; full month is not covered",
            }
        except Exception as exc:
            out["openweather"]["error"] = type(exc).__name__

        wx_key = os.getenv("WATSONX_API_KEY")
        wx_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com").rstrip("/")
        project_id = os.getenv("WATSONX_PROJECT_ID")
        token = None
        try:
            response = await client.post(
                "https://iam.cloud.ibm.com/identity/token",
                data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": wx_key},
                headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
            )
            body = response.json() if response.content else {}
            token = body.get("access_token")
            out["watsonx"]["token_status"] = response.status_code
            out["watsonx"]["token_success"] = bool(token)
        except Exception as exc:
            out["watsonx"]["token_error"] = type(exc).__name__

        if token:
            headers = {"Authorization": f"Bearer {token}", "Accept": "application/json", "Content-Type": "application/json"}
            try:
                response = await client.get(
                    f"{wx_url}/ml/v1/foundation_model_specs",
                    headers=headers,
                    params={"version": "2024-10-10", "filters": "function_text_chat"},
                )
                body = response.json() if response.content else {}
                resources = body.get("resources") or []
                chat_models = [model.get("model_id") for model in resources if model.get("model_id")]
                preferred = [model for model in chat_models if "granite" in model and ("instruct" in model or "chat" in model)]
                selected = preferred[0] if preferred else (chat_models[0] if chat_models else os.getenv("WATSONX_MODEL"))
                out["watsonx"]["model_status"] = response.status_code
                out["watsonx"]["chat_model_count"] = len(chat_models)
                out["watsonx"]["sample_models"] = chat_models[:5]
                out["watsonx"]["selected_model_id"] = selected

                payload = {
                    "model_id": selected,
                    "project_id": project_id,
                    "messages": [
                        {"role": "system", "content": "You extract event search intent as strict JSON only."},
                        {
                            "role": "user",
                            "content": (
                                "Today is 2026-05-17. Return ONLY JSON with keys "
                                "city,country,category,keyword,date_from,date_to,budget_max,currency,preferences. "
                                "Query: Find electronic music events in Berlin this weekend under $100"
                            ),
                        },
                    ],
                    "parameters": {"temperature": 0, "max_tokens": 300},
                }
                response = await client.post(
                    f"{wx_url}/ml/v1/text/chat",
                    headers=headers,
                    params={"version": "2024-10-10"},
                    json=payload,
                )
                body = response.json() if response.content else {}
                choices = body.get("choices") or []
                content = (choices[0].get("message") or {}).get("content") if choices else None
                out["watsonx"]["chat_status"] = response.status_code
                out["watsonx"]["intent_output"] = content or body
            except Exception as exc:
                out["watsonx"]["error"] = type(exc).__name__

    print(json.dumps(out, indent=2, default=str))


asyncio.run(main())
