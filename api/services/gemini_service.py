"""
Centralized Gemini AI Service for CareerPath Ghana.
Handles GCP Vertex AI authentication, fallback to Gemini Developer API,
markdown fence stripping, and JSON parsing.
"""

import os
import json
import re
import urllib.request
import urllib.error
from django.conf import settings

try:
    from google.oauth2 import service_account
    import google.auth.transport.requests
    HAS_GOOGLE_AUTH = True
except ImportError:
    HAS_GOOGLE_AUTH = False
    service_account = None


def get_gcp_credentials():
    """
    Attempts to load Google Cloud Service Account credentials from
    environment variable GCP_KEY_JSON or fallback to local gcp-key.json.
    """
    if not HAS_GOOGLE_AUTH:
        return None

    gcp_json_str = os.getenv('GCP_KEY_JSON')
    key_path = os.path.join(settings.BASE_DIR, 'gcp-key.json')

    creds = None
    if gcp_json_str:
        try:
            info = json.loads(gcp_json_str)
            scopes = ["https://www.googleapis.com/auth/cloud-platform"]
            creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        except Exception as e:
            print(f"DEBUG: Failed to parse GCP_KEY_JSON env var: {e}")

    if not creds and os.path.exists(key_path):
        try:
            scopes = ["https://www.googleapis.com/auth/cloud-platform"]
            creds = service_account.Credentials.from_service_account_file(key_path, scopes=scopes)
        except Exception as e:
            print(f"DEBUG: Failed to load gcp-key.json file: {e}")

    return creds


def clean_markdown_fences(text: str) -> str:
    """Strips markdown code block wrappers (e.g. ```json ... ```)."""
    text = (text or "").strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def call_gemini(
    payload: dict,
    timeout: int = 10,
    developer_models: list = None,
    expect_json: bool = False,
    *args,
    **kwargs
):
    """
    Dispatches a prompt/payload directly to Gemini Developer API using GEMINI_API_KEY.
    Uses the latest high-performance Gemini models.
    Accepts *args and **kwargs for backward compatibility with legacy caller signatures.

    Returns:
        dict/list if expect_json=True and parsing succeeds,
        str if expect_json=False and raw text returned,
        None if all attempts fail.
    """
    if developer_models is None:
        developer_models = [
            "gemini-flash-lite-latest",
            "gemini-3-flash-preview",
            "gemini-flash-latest",
            "gemini-3.1-flash-lite-preview",
            "gemini-3.8-flash"
        ]

    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("DEBUG: GEMINI_API_KEY is not set.")
        return None

    for model_name in developer_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
        try:
            req_obj = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req_obj, timeout=timeout) as response:
                res_data = json.loads(response.read().decode())
                candidates = res_data.get("candidates", [])
                if candidates:
                    raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                    if raw_text:
                        if expect_json:
                            cleaned = clean_markdown_fences(raw_text)
                            return json.loads(cleaned)
                        return raw_text
        except urllib.error.HTTPError as e:
            print(f"DEBUG: Gemini Developer API call for {model_name} failed: HTTP {e.code} ({e.reason})")
            continue
        except Exception as e:
            print(f"DEBUG: Gemini Developer API call for {model_name} failed: {e}")
            continue

    return None
