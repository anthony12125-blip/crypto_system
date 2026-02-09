#!/bin/bash
# Auto-update script for crypto bot dashboard
# Run this via cron every 5 minutes

cd /Users/HaleyApple/.openclaw/workspace/crypto_bot

# Set environment variables
export DASHBOARD_URL="https://crypto-bot-409495160162.us-central1.run.app"
export DASHBOARD_API_KEY="crypto-bot-2026"

# Run the updater
python3 dashboard_updater_multi.py >> logs/dashboard_updates.log 2>&1
