#!/usr/bin/env python3
"""
API Setup Verification Script
Usage: python verify_setup.py
"""

import os
import json
import sys


def check_env_file():
    """Check local .env file for API keys."""
    print("\n" + "=" * 60)
    print("1. CHECKING LOCAL .env FILE")
    print("=" * 60)

    env_path = os.path.join(os.path.dirname(__file__), "api_keys", ".env")

    if not os.path.exists(env_path):
        print(f"❌ .env file not found at: {env_path}")
        return False

    print(f"✅ Found: {env_path}")

    required_keys = [
        "NVIDIA_API_KEY",
        "GOOGLE_SHEET_ID",
        "GOOGLE_DRIVE_FOLDER_ID",
        "SERVICE_ACCOUNT_JSON",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
    ]

    with open(env_path, "r") as f:
        content = f.read()

    all_present = True
    for key in required_keys:
        if key in content:
            print(f"  ✅ {key}")
        else:
            print(f"  ❌ {key} - MISSING")
            all_present = False

    return all_present


def check_agent_code():
    """Check how agent.py loads API keys."""
    print("\n" + "=" * 60)
    print("2. CHECKING AGENT.PY CONFIGURATION")
    print("=" * 60)

    agent_path = os.path.join(os.path.dirname(__file__), "agent.py")

    if not os.path.exists(agent_path):
        print(f"❌ agent.py not found")
        return False

    with open(agent_path, "r") as f:
        content = f.read()

    checks = [
        ("load_dotenv", "Dotenv loading"),
        ("os.environ.get", "Environment variable retrieval"),
        ("NVIDIA_API_KEY", "NVIDIA API key"),
        ("TELEGRAM_BOT_TOKEN", "Telegram bot token"),
        ("SERVICE_ACCOUNT_JSON", "Google service account"),
    ]

    for pattern, desc in checks:
        if pattern in content:
            print(f"  ✅ {desc}")
        else:
            print(f"  ❌ {desc}")

    return True


def check_workflow():
    """Check GitHub workflow configuration."""
    print("\n" + "=" * 60)
    print("3. CHECKING GITHUB WORKFLOW")
    print("=" * 60)

    workflow_path = os.path.join(
        os.path.dirname(__file__), ".github", "workflows", "agent.yml"
    )

    if not os.path.exists(workflow_path):
        print(f"❌ Workflow file not found at: {workflow_path}")
        return False

    with open(workflow_path, "r") as f:
        content = f.read()

    checks = [
        ("schedule", "Scheduled trigger"),
        ("workflow_dispatch", "Manual trigger"),
        ("NVIDIA_API_KEY", "NVIDIA secret"),
        ("secrets.", "Using GitHub secrets"),
    ]

    for pattern, desc in checks:
        if pattern in content:
            print(f"  ✅ {desc}")
        else:
            print(f"  ❌ {desc}")

    if 'cron: "0 */3 * * *"' in content:
        print("  ✅ Schedule: Every 3 hours")

    return True


def check_github_secrets_via_api():
    """Check if secrets are configured in GitHub (requires token)."""
    print("\n" + "=" * 60)
    print("4. CHECKING GITHUB SECRETS (API)")
    print("=" * 60)

    import urllib.request

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("  ⚠️  GITHUB_TOKEN not set - cannot check via API")
        print(
            "  ℹ️  Manually check at: https://github.com/Vikram-Bosak/Prompt-Gen-X-Ray-Blueprint/settings/secrets/actions"
        )
        return None

    repo = "Vikram-Bosak/Prompt-Gen-X-Ray-Blueprint"
    url = f"https://api.github.com/repos/{repo}/actions/secrets"

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github+json")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            count = data.get("total_count", 0)
            if count > 0:
                print(f"  ✅ Found {count} secrets in GitHub:")
                for secret in data.get("secrets", []):
                    print(f"     - {secret['name']}")
            else:
                print(f"  ❌ NO secrets found in GitHub!")
                print(f"  ℹ️  Go to: https://github.com/{repo}/settings/secrets/actions")
            return count > 0
    except Exception as e:
        print(f"  ⚠️  Could not check secrets: {e}")
        return None


def test_local_execution():
    """Test loading API keys locally."""
    print("\n" + "=" * 60)
    print("5. TESTING LOCAL API KEY LOADING")
    print("=" * 60)

    from dotenv import load_dotenv

    env_path = os.path.join(os.path.dirname(__file__), "api_keys", ".env")
    load_dotenv(env_path)

    keys = {
        "NVIDIA_API_KEY": os.environ.get("NVIDIA_API_KEY"),
        "GOOGLE_SHEET_ID": os.environ.get("GOOGLE_SHEET_ID"),
        "TELEGRAM_BOT_TOKEN": os.environ.get("TELEGRAM_BOT_TOKEN"),
    }

    for key, value in keys.items():
        if value and len(value) > 10:
            print(f"  ✅ {key}: {value[:10]}...")
        else:
            print(f"  ❌ {key}: Not loaded or empty")

    return all(v and len(v) > 10 for v in keys.values())


def main():
    print("\n" + "=" * 60)
    print("🔍 VIDEO PROMPT AGENT - SETUP VERIFICATION")
    print("=" * 60)

    results = []

    results.append(("Local .env File", check_env_file()))
    results.append(("Agent Code", check_agent_code()))
    results.append(("GitHub Workflow", check_workflow()))
    results.append(
        (
            "GitHub Secrets",
            check_github_secrets_via_api() if os.environ.get("GITHUB_TOKEN") else None,
        )
    )
    results.append(("Local Execution", test_local_execution()))

    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)

    for name, result in results:
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"
        print(f"  {status} - {name}")

    print("\n" + "=" * 60)
    print("🚀 NEXT STEPS")
    print("=" * 60)
    print("""
If GitHub Secrets FAIL:
  1. Go to: https://github.com/Vikram-Bosak/Prompt-Gen-X-Ray-Blueprint/settings/secrets/actions
  2. Click "New repository secret"
  3. Add each key from api_keys/.env file:
     - NVIDIA_API_KEY
     - GOOGLE_SHEET_ID  
     - GOOGLE_DRIVE_FOLDER_ID
     - TELEGRAM_BOT_TOKEN
     - TELEGRAM_CHAT_ID
     - SERVICE_ACCOUNT_JSON (paste full JSON as single line)

If Local Execution PASSES:
  - Your local setup is working correctly
  - Run: python agent.py to test
""")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
