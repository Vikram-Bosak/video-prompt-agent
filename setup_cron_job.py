#!/usr/bin/env python3
"""
Cron-Job.org Setup Script for Video Prompt Agent

This script helps you set up cron-job.org to trigger your GitHub workflow
every 3 hours reliably.

Usage:
    python setup_cron_job.py
"""

import os
import json
import urllib.request
import urllib.parse

REPO_OWNER = "Vikram-Bosak"
REPO_NAME = "Prompt-Gen-X-Ray-Blueprint"
GITHUB_TOKEN = "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"  # From git remote


def check_github_connection():
    """Verify GitHub token works."""
    print("\n" + "=" * 60)
    print("1. CHECKING GITHUB CONNECTION")
    print("=" * 60)

    url = "https://api.github.com/user"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"token {GITHUB_TOKEN}")

    try:
        with urllib.request.urlopen(req) as response:
            user = json.loads(response.read())
            print(f"✅ Connected as: {user['login']}")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def get_workflow_info():
    """Get workflow details."""
    print("\n" + "=" * 60)
    print("2. GETTING WORKFLOW INFO")
    print("=" * 60)

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"token {GITHUB_TOKEN}")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            for wf in data["workflows"]:
                if "agent.yml" in wf["path"]:
                    print(f"✅ Workflow: {wf['name']}")
                    print(f"   ID: {wf['id']}")
                    print(f"   State: {wf['state']}")
                    return wf["id"]
    except Exception as e:
        print(f"❌ Error: {e}")
    return None


def test_workflow_dispatch(workflow_id):
    """Test triggering workflow via repository_dispatch."""
    print("\n" + "=" * 60)
    print("3. TESTING WORKFLOW TRIGGER")
    print("=" * 60)

    # Try repository_dispatch
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/dispatches"
    data = {
        "event_type": "run-agent",
        "client_payload": {"triggered_by": "setup-script"},
    }

    req = urllib.request.Request(url, data=json.dumps(data).encode())
    req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as response:
            print("✅ Repository dispatch triggered successfully!")
            print(
                "   Check: https://github.com/{}/{}/actions".format(
                    REPO_OWNER, REPO_NAME
                )
            )
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"❌ HTTP {e.code}: {error_body[:200]}")
        return False


def generate_cron_urls():
    """Generate URLs for cron-job.org."""
    print("\n" + "=" * 60)
    print("4. CRON-JOB.ORG SETUP")
    print("=" * 60)

    print("\n📋 CRON-JOB.ORG CONFIGURATION:")
    print("-" * 60)
    print(
        """
1. Go to: https://cron-job.org/en/jobs/
2. Click "Create cron job"

3. Fill in these details:
   - Title: Video Prompt Agent (Every 3 Hours)
   - URL: https://api.github.com/repos/{}/{}/dispatches
   - Method: POST
   - Authorization: Bearer token
   - Token: {} 
   - Body (JSON):
     {{"event_type": "run-agent"}}
   - Schedule: Every 3 hours (0 */3 * * *)

4. Click "Create cron job"
""".format(REPO_OWNER, REPO_NAME, GITHUB_TOKEN)
    )

    print("\n" + "=" * 60)
    print("5. ALTERNATIVE - SIMPLE URL METHOD")
    print("=" * 60)
    print(
        """
If you prefer, you can also use these free services:

A) GitHub Scheduler (already configured!):
   - The workflow already has: cron: "0 */3 * * *"
   - Just add secrets to GitHub and it will work automatically
   
B) EasyCron (https://www.easycron.com):
   - URL: https://api.github.com/repos/{}/{}/dispatches
   - Method: POST
   - Body: {{"event_type": "run-agent"}}
   - Headers: 
     Authorization: token {}
     Content-Type: application/json

C) If you have a server, add to crontab:
   0 */3 * * * curl -X POST -H "Accept: application/vnd.github+json" \\
     -H "Authorization: token {}" \\
     -H "Content-Type: application/json" \\
     https://api.github.com/repos/{}/{}/dispatches \\
     -d '{{"event_type": "run-agent"}}'
""".format(REPO_OWNER, REPO_NAME, GITHUB_TOKEN, GITHUB_TOKEN, REPO_OWNER, REPO_NAME)
    )


def show_status():
    """Show current workflow runs."""
    print("\n" + "=" * 60)
    print("6. CHECK WORKFLOW STATUS")
    print("=" * 60)

    url = (
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs?per_page=5"
    )
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"token {GITHUB_TOKEN}")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            print(f"Recent workflow runs:")
            for run in data.get("workflow_runs", [])[:3]:
                status = (
                    "✅"
                    if run["conclusion"] == "success"
                    else "❌"
                    if run["conclusion"] == "failure"
                    else "⏳"
                )
                print(
                    f"  {status} {run['event']} - {run['display_title'][:40]} ({run.get('conclusion', 'running')})"
                )
    except Exception as e:
        print(f"Error: {e}")


def main():
    print("\n" + "=" * 60)
    print("🚀 CRON-JOB.ORG SETUP FOR VIDEO PROMPT AGENT")
    print("=" * 60)

    # Step 1: Check connection
    if not check_github_connection():
        print("\n❌ GitHub token is invalid or expired!")
        print("   Please update GITHUB_TOKEN in this script.")
        return

    # Step 2: Get workflow info
    workflow_id = get_workflow_info()
    if not workflow_id:
        print("\n❌ Could not find workflow!")
        return

    # Step 3: Test trigger
    test_workflow_dispatch(workflow_id)

    # Step 4: Show cron-job.org setup
    generate_cron_urls()

    # Step 5: Show status
    show_status()

    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print(
        """
NEXT STEPS:

OPTION A - Use cron-job.org (Recommended):
  1. Go to https://cron-job.org/en/jobs/
  2. Create new job with the URL and settings above
  3. Job will run every 3 hours

OPTION B - Fix GitHub Actions (If you add secrets):
  1. Add secrets at: https://github.com/{}/{}/settings/secrets/actions
  2. The built-in schedule will work automatically

To trigger manually:
  curl -X POST -H "Accept: application/vnd.github+json" \\
    -H "Authorization: token {}" \\
    https://api.github.com/repos/{}/{}/dispatches \\
    -d '{{"event_type": "run-agent"}}'
""".format(REPO_OWNER, REPO_NAME, GITHUB_TOKEN, REPO_OWNER, REPO_NAME)
    )


if __name__ == "__main__":
    main()
