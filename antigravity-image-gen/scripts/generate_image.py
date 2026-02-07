#!/usr/bin/env python3
"""
Generate images via the Antigravity API.
Credentials are read from ~/.config/antigravity/accounts.json.
Run auth.py first if no credentials exist.
"""

import argparse
import base64
import json
import os
import random
import secrets
import sys
import time
import uuid

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

ACCOUNTS_FILE = os.path.expanduser("~/.config/antigravity/accounts.json")

CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
CLIENT_SECRET = "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"

ENDPOINTS = [
    "https://daily-cloudcode-pa.sandbox.googleapis.com",
    "https://autopush-cloudcode-pa.sandbox.googleapis.com",
    "https://cloudcode-pa.googleapis.com",
]

VERSION = "1.15.8"

MIME_EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}


def find_accounts_file():
    if os.path.exists(ACCOUNTS_FILE):
        return ACCOUNTS_FILE
    return None


def load_account(path):
    """Load the active account from accounts file."""
    with open(path) as f:
        data = json.load(f)
    accounts = data.get("accounts", [])
    idx = data.get("activeIndex", 0)
    if not accounts:
        return None
    account = accounts[min(idx, len(accounts) - 1)]
    if not account.get("refreshToken"):
        return None
    return account


def generate_fingerprint():
    """Generate a randomized device fingerprint."""
    plat = random.choice(["darwin", "win32", "linux"])
    arch = random.choice(["x64", "arm64"])
    os_versions = {
        "darwin": ["12.6.3", "13.5.2", "14.2.1", "14.5"],
        "win32": ["10.0.22000", "10.0.22621", "10.0.22631"],
        "linux": ["6.1.0", "6.2.0", "6.5.0"],
    }
    ide_types = ["VSCODE", "INTELLIJ", "CLOUD_SHELL_EDITOR"]
    api_clients = [
        "google-cloud-sdk vscode_cloudshelleditor/0.1",
        "google-cloud-sdk intellij/0.1",
    ]
    plat_map = {"darwin": "MACOS", "win32": "WINDOWS", "linux": "LINUX"}
    return {
        "deviceId": str(uuid.uuid4()),
        "sessionToken": secrets.token_hex(16),
        "userAgent": f"antigravity/{VERSION} {plat}/{arch}",
        "apiClient": random.choice(api_clients),
        "clientMetadata": {
            "ideType": random.choice(ide_types),
            "platform": plat_map.get(plat, "PLATFORM_UNSPECIFIED"),
            "pluginType": "GEMINI",
            "osVersion": random.choice(os_versions[plat]),
            "arch": arch,
            "sqmId": "{" + str(uuid.uuid4()).upper() + "}",
        },
        "quotaUser": f"device-{secrets.token_hex(8)}",
        "createdAt": int(time.time() * 1000),
    }


def refresh_access_token(refresh_token):
    """Exchange refresh token for a fresh access token."""
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    })
    if resp.status_code != 200:
        print(f"Token refresh failed: {resp.text}", file=sys.stderr)
        return None
    return resp.json().get("access_token")


def build_headers(access_token, fingerprint):
    """Build request headers including fingerprint."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    if fingerprint:
        if "userAgent" in fingerprint:
            headers["User-Agent"] = fingerprint["userAgent"]
        if "quotaUser" in fingerprint:
            headers["X-Goog-QuotaUser"] = fingerprint["quotaUser"]
        if "deviceId" in fingerprint:
            headers["X-Client-Device-Id"] = fingerprint["deviceId"]
        if "apiClient" in fingerprint:
            headers["X-Goog-Api-Client"] = fingerprint["apiClient"]
        if "clientMetadata" in fingerprint:
            headers["Client-Metadata"] = json.dumps(fingerprint["clientMetadata"])
    return headers


def generate_image(prompt, output_path, access_token, project_id, fingerprint, image_config=None):
    """Call the Antigravity image generation API."""
    headers = build_headers(access_token, fingerprint)
    body = {
        "project": project_id,
        "model": "gemini-3-pro-image",
        "request": {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"candidateCount": 1},
        },
        "userAgent": "antigravity",
        "requestId": str(uuid.uuid4()),
    }
    if image_config:
        body["request"]["generationConfig"]["imageConfig"] = image_config

    for endpoint in ENDPOINTS:
        url = f"{endpoint}/v1internal:generateContent"
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                candidates = result.get("response", {}).get("candidates", [])
                if candidates:
                    for part in candidates[0].get("content", {}).get("parts", []):
                        inline = part.get("inlineData")
                        if inline and inline.get("data"):
                            img_bytes = base64.b64decode(inline["data"])
                            with open(output_path, "wb") as f:
                                f.write(img_bytes)
                            return True
                print(f"No image data from {endpoint}", file=sys.stderr)
            else:
                print(f"API error {resp.status_code} from {endpoint}: {resp.text}", file=sys.stderr)
        except requests.exceptions.Timeout:
            print(f"Timeout: {endpoint}", file=sys.stderr)
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {endpoint}: {e}", file=sys.stderr)
    return False


def main():
    parser = argparse.ArgumentParser(description="Generate images via Antigravity API")
    parser.add_argument("--prompt", required=True, help="Image description")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--config", help="imageConfig JSON (e.g. '{\"aspectRatio\":\"16:9\"}')")
    args = parser.parse_args()

    acct_path = find_accounts_file()
    if not acct_path:
        print("No credentials found. Run auth.py first to sign in.", file=sys.stderr)
        sys.exit(1)

    account = load_account(acct_path)
    if not account:
        print("No valid account in credentials file. Run auth.py to re-authenticate.", file=sys.stderr)
        sys.exit(1)

    refresh_token = account["refreshToken"]
    project_id = account.get("projectId") or account.get("managedProjectId") or "rising-fact-p41fc"
    fingerprint = account.get("fingerprint") or generate_fingerprint()

    access_token = refresh_access_token(refresh_token)
    if not access_token:
        print("Failed to get access token. Run auth.py to re-authenticate.", file=sys.stderr)
        sys.exit(1)

    image_config = None
    if args.config:
        try:
            image_config = json.loads(args.config)
        except json.JSONDecodeError:
            print(f"Invalid --config JSON: {args.config}", file=sys.stderr)
            sys.exit(1)

    if generate_image(args.prompt, args.output, access_token, project_id, fingerprint, image_config):
        print(args.output)
    else:
        print("Failed to generate image.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
