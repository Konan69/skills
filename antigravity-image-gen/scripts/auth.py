#!/usr/bin/env python3
"""
OAuth login for Antigravity API.
Opens browser for Google sign-in, captures callback, stores credentials
to ~/.config/antigravity/accounts.json (never inside a project directory).
"""

import base64
import hashlib
import http.server
import json
import os
import platform
import random
import secrets
import socket
import sys
import threading
import time
import uuid
import webbrowser
from urllib.parse import parse_qs, urlencode, urlparse

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

ACCOUNTS_FILE = os.path.expanduser("~/.config/antigravity/accounts.json")
CALLBACK_PORT = 51121
REDIRECT_URI = f"http://localhost:{CALLBACK_PORT}/oauth-callback"

CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
CLIENT_SECRET = "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"

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/cclog",
    "https://www.googleapis.com/auth/experimentsandconfigs",
]

LOAD_CODE_ASSIST_ENDPOINTS = [
    "https://cloudcode-pa.googleapis.com/v1internal:loadCodeAssist",
    "https://daily-cloudcode-pa.sandbox.googleapis.com/v1internal:loadCodeAssist",
    "https://autopush-cloudcode-pa.sandbox.googleapis.com/v1internal:loadCodeAssist",
]

VERSION = "1.15.8"
DEFAULT_PROJECT = "rising-fact-p41fc"


def generate_pkce():
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def generate_fingerprint():
    plat = random.choice(["darwin", "win32", "linux"])
    arch = random.choice(["x64", "arm64"])
    os_versions = {
        "darwin": ["10.15.7", "11.6.8", "12.6.3", "13.5.2", "14.2.1", "14.5"],
        "win32": ["10.0.19041", "10.0.19042", "10.0.22000", "10.0.22621", "10.0.22631"],
        "linux": ["5.15.0", "5.19.0", "6.1.0", "6.2.0", "6.5.0", "6.6.0"],
    }
    ide_types = ["IDE_UNSPECIFIED", "VSCODE", "INTELLIJ", "ANDROID_STUDIO", "CLOUD_SHELL_EDITOR"]
    api_clients = [
        "google-cloud-sdk vscode_cloudshelleditor/0.1",
        "google-cloud-sdk intellij/0.1",
        "google-cloud-sdk android-studio/0.1",
        "google-cloud-sdk cloud-shell-editor/0.1",
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


def discover_project(access_token):
    for endpoint in LOAD_CODE_ASSIST_ENDPOINTS:
        try:
            resp = requests.post(
                endpoint,
                headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
                json={},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                pid = data.get("projectId") or data.get("managedProjectId")
                mpid = data.get("managedProjectId", "")
                if pid:
                    return pid, mpid
        except Exception:
            continue
    return DEFAULT_PROJECT, ""


def get_user_email(access_token):
    try:
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo?alt=json",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("email", "unknown")
    except Exception:
        pass
    return "unknown"


def save_account(refresh_token, project_id, managed_project_id, email, fingerprint):
    os.makedirs(os.path.dirname(ACCOUNTS_FILE), exist_ok=True)

    data = {"version": 3, "accounts": [], "activeIndex": 0}
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE) as f:
                data = json.load(f)
        except Exception:
            pass

    now = int(time.time() * 1000)
    # Remove existing account with same email
    data["accounts"] = [a for a in data.get("accounts", []) if a.get("email") != email]

    data["accounts"].insert(0, {
        "email": email,
        "refreshToken": refresh_token,
        "projectId": project_id,
        "managedProjectId": managed_project_id,
        "addedAt": now,
        "lastUsed": now,
        "enabled": True,
        "fingerprint": fingerprint,
    })
    data["activeIndex"] = 0

    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(ACCOUNTS_FILE, 0o600)

    # Gitignore protection
    gitignore = os.path.join(os.path.dirname(ACCOUNTS_FILE), ".gitignore")
    if not os.path.exists(gitignore):
        with open(gitignore, "w") as f:
            f.write("antigravity-accounts.json\n*.tmp\n")


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    auth_code = None
    auth_state = None
    error = None

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/oauth-callback":
            self.send_response(404)
            self.end_headers()
            return

        params = parse_qs(parsed.query)
        if "error" in params:
            CallbackHandler.error = params["error"][0]
            self._respond("Authentication failed. You can close this tab.")
            return

        CallbackHandler.auth_code = params.get("code", [None])[0]
        CallbackHandler.auth_state = params.get("state", [None])[0]
        self._respond("Authentication successful! You can close this tab.")

    def _respond(self, msg):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(f"<html><body><h2>{msg}</h2></body></html>".encode())

    def log_message(self, format, *args):
        pass  # silence logs


def wait_for_callback(server, timeout=120):
    server.timeout = 1
    deadline = time.time() + timeout
    while time.time() < deadline:
        server.handle_request()
        if CallbackHandler.auth_code or CallbackHandler.error:
            return
    CallbackHandler.error = "Timed out waiting for authentication"


def main():
    # Check if port is available
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", CALLBACK_PORT))
        sock.close()
    except OSError:
        print(f"Error: Port {CALLBACK_PORT} is in use", file=sys.stderr)
        sys.exit(1)

    verifier, challenge = generate_pkce()

    state = base64.urlsafe_b64encode(json.dumps({"verifier": verifier}).encode()).decode()

    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    })

    server = http.server.HTTPServer(("localhost", CALLBACK_PORT), CallbackHandler)

    print("Opening browser for Google sign-in...")
    webbrowser.open(auth_url)
    print(f"If browser didn't open, visit:\n{auth_url}\n")
    print("Waiting for authentication...")

    wait_for_callback(server)
    server.server_close()

    if CallbackHandler.error:
        print(f"Error: {CallbackHandler.error}", file=sys.stderr)
        sys.exit(1)

    code = CallbackHandler.auth_code
    received_state = CallbackHandler.auth_state

    # Decode state to get verifier
    try:
        state_data = json.loads(base64.urlsafe_b64decode(received_state + "=="))
        verifier = state_data["verifier"]
    except Exception:
        pass  # use original verifier

    # Exchange code for tokens
    print("Exchanging authorization code...")
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier,
    })

    if resp.status_code != 200:
        print(f"Token exchange failed: {resp.text}", file=sys.stderr)
        sys.exit(1)

    tokens = resp.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Get user info and project
    email = get_user_email(access_token)
    project_id, managed_project_id = discover_project(access_token)
    fingerprint = generate_fingerprint()

    save_account(refresh_token, project_id, managed_project_id, email, fingerprint)

    print(f"\nAuthenticated as: {email}")
    print(f"Project: {project_id}")
    print(f"Credentials saved to: {ACCOUNTS_FILE}")
    sys.exit(0)


if __name__ == "__main__":
    main()
