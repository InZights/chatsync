# Slack Notification Setup Guide

## Overview

The migration pipeline includes automatic Slack notifications to alert you about:
- ✅ Migration start/completion
- ⚠️ High error rates or duplicates
- ❌ System failures or crashes
- 🚨 Critical anomalies during processing

## Quick Start

### Option 1: Incoming Webhooks (Recommended)

**Step 1:** Create a Slack Incoming Webhook

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name it "Migration Monitor" and select your workspace
4. Navigate to "Incoming Webhooks" and activate it
5. Click "Add New Webhook to Workspace"
6. Select the channel for alerts (e.g., `#migration-alerts`)
7. Copy the webhook URL (looks like: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`)

**Step 2:** Set environment variable

```powershell
# Windows PowerShell
$env:SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Linux/Mac
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

**Step 3:** Enable notifications in settings

Edit `config/settings.json`:
```json
{
  "notifications": {
    "enabled": true,
    "webhook_url_env": "SLACK_WEBHOOK_URL",
    "notification_channel": "#migration-alerts"
  }
}
```

**Step 4:** Run migration

```powershell
python migrate.py
```

You'll receive notifications automatically!

---

### Option 2: Bot Token (Advanced)

Use this if you want more control or already have a bot token.

**Step 1:** Create/Use Slack Bot

1. Go to https://api.slack.com/apps
2. Create a new app or use existing
3. Navigate to "OAuth & Permissions"
4. Add Bot Token Scopes:
   - `chat:write` - Post messages
   - `channels:read` - Find channels
5. Install app to workspace
6. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

**Step 2:** Set environment variable

```powershell
# Windows PowerShell
$env:SLACK_BOT_TOKEN = "xoxb-your-token-here"

# Linux/Mac
export SLACK_BOT_TOKEN="xoxb-your-token-here"
```

**Step 3:** Enable notifications in settings

Edit `config/settings.json`:
```json
{
  "notifications": {
    "enabled": true,
    "notification_channel": "#migration-alerts"
  }
}
```

---

## Configuration Reference

### Alert Thresholds

Customize when alerts are triggered:

```json
{
  "notifications": {
    "enabled": true,
    "alert_thresholds": {
      "error_rate": 0.05,                  // Alert if >5% messages fail
      "duplicate_rate": 0.30,              // Alert if >30% are duplicates
      "processing_time_minutes": 60,       // Alert if processing >60 min
      "critical_error_count": 10           // Alert after 10 errors
    }
  }
}
```

### Notification Types

| Type | When Triggered | Severity |
|------|----------------|----------|
| **Migration Started** | When processing begins | ℹ️ INFO |
| **Migration Complete** | Successful completion | ✅ INFO |
| **High Error Rate** | Error rate exceeds threshold | ❌ ERROR |
| **High Duplicate Rate** | Duplicate rate exceeds threshold | ⚠️ WARNING |
| **API Upload Failures** | Slack upload failures >10% | ❌ ERROR |
| **Error Threshold Exceeded** | Critical error count reached | 🚨 ERROR |
| **Migration Failed** | System crash or fatal error | 🚨 CRITICAL |

---

## Example Notifications

### Migration Started
```
🚀 Migration Started
Teams to Slack migration has begun

Input File: data/input/teams_convo.json
Total Messages: 1,245
```

### Migration Complete
```
✅ Migration Complete
🎉 Migration finished successfully! Processed 1,245 messages in 3.2 minutes.

Total Processed: 1,245
Successful: 1,240
Failed: 5
Duration: 3.2 minutes
Uploaded to Slack: 1,240
```

### High Error Rate Alert
```
⚠️ High Error Rate Detected
Error rate is 8.5% (threshold: 5.0%)

Failed Messages: 106
Total Processed: 1,245
Error Rate: 8.52%
```

### Critical Failure
```
🚨 Migration Failed ❌
CRITICAL: Migration process has failed!

InvalidJSONError: Unexpected token at line 452

Processed Before Failure: 451
Error Count: 12
```

---

## Testing Notifications

Test your notification setup:

```python
# test_notifications.py
import os
import sys
sys.path.insert(0, 'src')

from teams_to_slack.slack_notifier import SlackNotifier, AlertLevel

# Initialize notifier
notifier = SlackNotifier(
    webhook_url=os.getenv('SLACK_WEBHOOK_URL'),
    notification_channel='#migration-alerts',
    enabled=True
)

# Send test notification
notifier.send_notification(
    title="Test Notification",
    message="🧪 If you see this, notifications are working correctly!",
    level=AlertLevel.INFO
)

print("✅ Test notification sent!")
```

Run it:
```powershell
python test_notifications.py
```

---

## Disabling Notifications

### Temporarily Disable

```json
{
  "notifications": {
    "enabled": false
  }
}
```

### Or remove environment variable

```powershell
# Windows
Remove-Item Env:SLACK_WEBHOOK_URL

# Linux/Mac
unset SLACK_WEBHOOK_URL
```

---

## Troubleshooting

### "Notifications enabled but no webhook URL or bot token found"

**Solution:** Set the environment variable before running:
```powershell
$env:SLACK_WEBHOOK_URL = "your-webhook-url"
python migrate.py
```

### "Failed to send webhook notification: 404"

**Cause:** Webhook URL is invalid or expired.

**Solution:** Generate a new webhook URL from https://api.slack.com/apps

### "Slack API error: invalid_auth"

**Cause:** Bot token is invalid or doesn't have required permissions.

**Solution:** 
1. Check token starts with `xoxb-`
2. Verify bot has `chat:write` permission
3. Reinstall app to workspace if needed

### No notifications received

**Checklist:**
- [ ] `enabled: true` in settings.json
- [ ] Environment variable is set in same terminal session
- [ ] Channel name matches (include `#` prefix)
- [ ] Bot is invited to the channel (for bot tokens)
- [ ] Check `logs/migration.log` for error messages

---

## Advanced: Custom Alerting

Create custom alert logic:

```python
from teams_to_slack.slack_notifier import SlackNotifier, AlertLevel

notifier = SlackNotifier(
    webhook_url=os.getenv('SLACK_WEBHOOK_URL'),
    enabled=True
)

# Custom alert
if my_custom_condition:
    notifier.send_notification(
        title="Custom Alert",
        message="Something important happened!",
        level=AlertLevel.WARNING,
        fields=[
            {'title': 'Metric 1', 'value': '42'},
            {'title': 'Metric 2', 'value': '100%'}
        ]
    )
```

---

## Security Best Practices

1. **Never commit tokens/webhooks to git**
   - Use environment variables only
   - Add `.env` to `.gitignore`

2. **Rotate tokens periodically**
   - Regenerate webhook URLs every 90 days
   - Update bot tokens on security events

3. **Limit bot permissions**
   - Only grant `chat:write` (minimum required)
   - Don't grant admin or channel management

4. **Use private channels**
   - Send alerts to private channels with restricted access
   - Don't expose sensitive migration data in public channels

---

## Support

For issues or questions:
- Check `logs/migration.log` for detailed errors
- Review Slack API documentation: https://api.slack.com/messaging/webhooks
- File an issue with reproduction steps
