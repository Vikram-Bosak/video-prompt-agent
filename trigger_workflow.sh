#!/bin/bash
# Cron-Job.org Trigger Script
# This script triggers the GitHub workflow with API keys from the local .env file

# Load environment variables
source "$(dirname "$0")/api_keys/.env"

# GitHub repository details
REPO="Vikram-Bosak/Prompt-Gen-X-Ray-Blueprint"
TOKEN="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"

# Create JSON payload with environment variables
PAYLOAD=$(cat <<EOF
{
  "event_type": "run-agent",
  "client_payload": {
    "NVIDIA_API_KEY": "$NVIDIA_API_KEY",
    "GOOGLE_SHEET_ID": "$GOOGLE_SHEET_ID",
    "GOOGLE_DRIVE_FOLDER_ID": "$GOOGLE_DRIVE_FOLDER_ID",
    "TELEGRAM_BOT_TOKEN": "$TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID": "$TELEGRAM_CHAT_ID",
    "SERVICE_ACCOUNT_JSON": $(echo "$SERVICE_ACCOUNT_JSON" | jq -Rs .)
  }
}
EOF
)

# Trigger GitHub workflow
curl -s -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO/dispatches" \
  -d "$PAYLOAD"

echo ""
echo "✅ Workflow triggered!"
