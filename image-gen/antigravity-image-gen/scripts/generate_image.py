#!/usr/bin/env python3

import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    print(
        "Error: requests library required. Install with: pip install requests",
        file=sys.stderr,
    )
    sys.exit(1)

ANTIGRAVITY_ENDPOINTS = [
    "https://daily-cloudcode-pa.sandbox.googleapis.com",
    "https://autopush-cloudcode-pa.sandbox.googleapis.com",
    "https://cloudcode-pa.googleapis.com",
]

DEFAULT_ACCOUNTS_FILE = os.path.expanduser(
    "~/.config/opencode/antigravity-accounts.json"
)

ANTIGRAVITY_CLIENT_ID = os.environ.get("ANTIGRAVITY_CLIENT_ID", "")
ANTIGRAVITY_CLIENT_SECRET = os.environ.get("ANTIGRAVITY_CLIENT_SECRET", "")


def setup_credentials():
    """Ensure credential file exists, create symlink if needed"""
    credential_dir = os.path.expanduser("~/.config/antigravity")
    credential_file = os.path.join(credential_dir, "accounts.json")
    opencode_file = os.path.expanduser("~/.config/opencode/antigravity-accounts.json")

    if os.path.exists(credential_file):
        return credential_file

    if os.path.exists(opencode_file):
        opencode_dir = os.path.dirname(opencode_file)
        os.makedirs(credential_dir, exist_ok=True)

        if os.path.islink(opencode_file):
            print(f"Symlink already exists: {opencode_file}")
            return credential_file

        try:
            import shutil

            shutil.move(opencode_file, credential_file)
        except:
            with open(opencode_file, "r") as src, open(credential_file, "w") as dst:
                dst.write(src.read())
            os.remove(opencode_file)

        os.symlink(credential_file, opencode_file)
        print(f"Created symlink: {opencode_file} -> {credential_file}")

    return credential_file


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate images using Antigravity auth credentials"
    )
    parser.add_argument("--prompt", required=True, help="Image description")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument(
        "--refresh-token", help="Direct refresh token (overrides accounts file)"
    )
    parser.add_argument(
        "--project-id", help="Direct project ID (use with --refresh-token)"
    )
    parser.add_argument("--config", help="Full imageConfig JSON object")
    return parser.parse_args()


def load_accounts(accounts_file):
    if not os.path.exists(accounts_file):
        return None

    try:
        with open(accounts_file, "r") as f:
            data = json.load(f)

        if data.get("accounts") and len(data["accounts"]) > 0:
            account = data["accounts"][0]
            return {
                "refresh_token": account.get("refreshToken"),
                "project_id": account.get("projectId")
                or account.get("managedProjectId"),
                "fingerprint": account.get("fingerprint"),
            }
    except Exception as e:
        print(f"Error loading accounts file: {e}", file=sys.stderr)

    return None


def refresh_access_token(refresh_token, project_id):
    """Exchange refresh token for access token"""
    url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": ANTIGRAVITY_CLIENT_ID,
        "client_secret": ANTIGRAVITY_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"Token refresh failed: {response.text}", file=sys.stderr)
        return None

    result = response.json()
    return result.get("access_token")


def build_fingerprint_headers(fingerprint):
    """Build Antigravity fingerprint headers from account fingerprint"""
    if not fingerprint:
        return {}

    headers = {}

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


def parse_image_config(config_str):
    """Parse imageConfig JSON string"""
    if not config_str:
        return {}

    try:
        return json.loads(config_str)
    except json.JSONDecodeError:
        print(f"Invalid imageConfig JSON: {config_str}", file=sys.stderr)
        return {}


def get_mime_type_extension(mime_type):
    """Map MIME type to file extension"""
    mime_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    return mime_map.get(mime_type, ".png")


def generate_image(
    prompt, output_path, access_token, project_id, fingerprint=None, image_config=None
):
    """Call Antigravity API to generate image"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    if fingerprint:
        headers.update(build_fingerprint_headers(fingerprint))

    request_body = {
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
        request_body["request"]["generationConfig"]["imageConfig"] = image_config

    for endpoint in ANTIGRAVITY_ENDPOINTS:
        url = f"{endpoint}/v1internal:generateContent"

        try:
            response = requests.post(
                url, headers=headers, json=request_body, timeout=30
            )

            if response.status_code == 200:
                result = response.json()

                if "response" in result and "candidates" in result["response"]:
                    candidate = result["response"]["candidates"][0]

                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            if "inlineData" in part:
                                inline_data = part["inlineData"]
                                mime_type = inline_data.get("mimeType", "image/png")
                                base64_data = inline_data.get("data", "")

                                if base64_data:
                                    import base64

                                    image_bytes = base64.b64decode(base64_data)

                                    with open(output_path, "wb") as f:
                                        f.write(image_bytes)

                                    return True

                print(f"No image data in response from {endpoint}", file=sys.stderr)
            else:
                print(
                    f"API error {response.status_code} from {endpoint}: {response.text}",
                    file=sys.stderr,
                )

        except requests.exceptions.Timeout:
            print(f"Timeout connecting to {endpoint}", file=sys.stderr)
            continue
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to {endpoint}: {e}", file=sys.stderr)
            continue

    return False


def main():
    args = parse_args()

    credential_file = setup_credentials()

    refresh_token = None
    project_id = None
    fingerprint = None

    if args.refresh_token and args.project_id:
        refresh_token = args.refresh_token
        project_id = args.project_id
    else:
        accounts = load_accounts(credential_file)
        if not accounts:
            print(
                "Error: No valid accounts found. Provide --refresh-token and --project-id.",
                file=sys.stderr,
            )
            sys.exit(1)

        refresh_token = accounts["refresh_token"]
        project_id = accounts["project_id"]
        fingerprint = accounts["fingerprint"]

    access_token = refresh_access_token(refresh_token, project_id)
    if not access_token:
        print(
            "Failed to refresh access token. Try re-authenticating with opencode auth login",
            file=sys.stderr,
        )
        sys.exit(1)

    image_config = parse_image_config(args.config)
    output_path = args.output
    success = generate_image(
        prompt=args.prompt,
        output_path=output_path,
        access_token=access_token,
        project_id=project_id,
        fingerprint=fingerprint,
        image_config=image_config,
    )

    if success:
        print(output_path)
        sys.exit(0)
    else:
        print(
            "Failed to generate image. Try again or check credentials.", file=sys.stderr
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
