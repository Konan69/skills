# Antigravity Image Generation API Reference

## OAuth Token Refresh

**Endpoint:** `https://oauth2.googleapis.com/token`

**Method:** POST

**Body (application/x-www-form-urlencoded):**
```
client_id={ANTIGRAVITY_CLIENT_ID}
&client_secret={ANTIGRAVITY_CLIENT_SECRET}
&refresh_token={refresh_token}
&grant_type=refresh_token
```

**Response:**
```json
{
  "access_token": "ya29...",
  "expires_in": 3600,
  "refresh_token": "1//..."
}
```

## Generate Content (Image)

**Endpoint:** `{base}/v1internal:generateContent`

**Base endpoints (tried in order):**
1. `https://daily-cloudcode-pa.sandbox.googleapis.com`
2. `https://autopush-cloudcode-pa.sandbox.googleapis.com`
3. `https://cloudcode-pa.googleapis.com`

**Method:** POST

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
User-Agent: {user_agent_from_fingerprint}
X-Goog-Api-Client: {api_client_from_fingerprint}
X-Goog-QuotaUser: {quota_user_from_fingerprint}
X-Client-Device-Id: {device_id_from_fingerprint}
Client-Metadata: {json_string}
```

**Request Body:**
```json
{
  "project": "{project_id}",
  "model": "gemini-3-pro-image",
  "request": {
    "contents": [
      {
        "role": "user",
        "parts": [
          { "text": "{prompt}" }
        ]
      }
    ],
    "generationConfig": {
      "candidateCount": 1,
      "imageConfig": {
        "aspectRatio": "1:1"
      }
    }
  },
  "userAgent": "antigravity",
  "requestId": "{uuid}"
}
```

**imageConfig options (optional, full JSON object):**
- `aspectRatio`: String (e.g., "1:1", "16:9", "4:3", "9:16", "3:4")

**Response:**
```json
{
  "response": {
    "candidates": [
      {
        "content": {
          "parts": [
            {
              "inlineData": {
                "mimeType": "image/png",
                "data": "{base64_image_data}"
              }
            }
          ]
        },
        "finishReason": "STOP"
      }
    ],
    "usageMetadata": {
      "promptTokenCount": 20,
      "candidatesTokenCount": 1000
    }
  }
}
```

**MIME Types:**
- `image/jpeg` → `.jpg`
- `image/png` → `.png`
- `image/webp` → `.webp`
- `image/gif` → `.gif`
