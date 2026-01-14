# Microsoft Teams API Setup Guide

## Overview

To fetch data directly from Microsoft Teams, you need to use the **Microsoft Graph API**. This requires Azure AD app registration and proper permissions.

## Prerequisites

1. **Microsoft 365 Account** with Teams access
2. **Azure AD Tenant** (usually included with M365)
3. **Admin Consent** for Graph API permissions (or self-consent if allowed)

## Setup Steps

### 1. Register Azure AD Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Configure:
   - **Name**: `Teams to Slack Migration`
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI**: Leave empty for device code flow
5. Click **Register**

### 2. Configure API Permissions

1. In your app, go to **API permissions**
2. Click **Add a permission** → **Microsoft Graph** → **Delegated permissions**
3. Add these permissions:
   - `Channel.ReadBasic.All` - Read channel metadata
   - `ChannelMessage.Read.All` - Read channel messages
   - `Team.ReadBasic.All` - Read team info
   - `User.Read` - Read user profile
4. Click **Add permissions**
5. Click **Grant admin consent** (requires admin role)

### 3. Get Application (Client) ID

1. Go to **Overview** page of your app
2. Copy the **Application (client) ID**
3. Copy the **Directory (tenant) ID**

### 4. Set Environment Variables

```powershell
# Windows PowerShell
$env:AZURE_CLIENT_ID = "your-client-id-here"
$env:AZURE_TENANT_ID = "your-tenant-id-here"
```

```bash
# Linux/Mac
export AZURE_CLIENT_ID="your-client-id-here"
export AZURE_TENANT_ID="your-tenant-id-here"
```

## Usage

### Option 1: Interactive Mode

```powershell
python -m teams_to_slack.teams_fetcher
```

This will:
1. Prompt you to authenticate via device code
2. Show list of your Teams
3. Let you select which team to export
4. Export all channels to `data/input/teams_export/`

### Option 2: Programmatic Usage

```python
from teams_to_slack.teams_fetcher import TeamsFetcher, get_access_token_device_flow

# Get access token
client_id = "your-client-id"
access_token = get_access_token_device_flow(client_id)

# Initialize fetcher
fetcher = TeamsFetcher(access_token)

# Get teams
teams = fetcher.get_teams()
print(f"Found {len(teams)} teams")

# Export specific team
team_id = teams[0]['id']
results = fetcher.export_team_to_json(
    team_id, 
    output_dir="data/input",
    include_replies=True
)
```

### Option 3: Export Single Channel

```python
fetcher.export_channel_to_json(
    team_id="team-id-here",
    channel_id="channel-id-here", 
    output_file="data/input/teams_convo.json",
    include_replies=True
)
```

## Authentication Flow

### Device Code Flow (User Interactive)

1. Script displays a URL and code
2. User visits `https://microsoft.com/devicelogin`
3. User enters the code shown
4. User signs in with Microsoft account
5. Script receives access token

**Example Output:**
```
============================================================
MICROSOFT AUTHENTICATION REQUIRED
============================================================

To sign in, use a web browser to open the page:
https://microsoft.com/devicelogin
And enter the code: A1B2C3D4

URL: https://microsoft.com/devicelogin
Code: A1B2C3D4

Waiting for authentication...
============================================================
```

## API Rate Limits

Microsoft Graph API has rate limits:
- **Per app per tenant**: 2,000 requests per second
- **Per user**: Varies by API endpoint
- **Messages endpoint**: ~50 messages per request, pagination required

The `TeamsFetcher` handles pagination automatically.

## Permissions Scope

### Delegated Permissions (User Context)
Used when fetching data as a specific user:
- `Channel.ReadBasic.All`
- `ChannelMessage.Read.All`
- `Team.ReadBasic.All`

### Application Permissions (App Context)
For background services (requires admin consent):
- `Channel.ReadBasic.All`
- `ChannelMessage.Read.All`
- `Team.ReadBasic.All`

## Data Format

The fetcher exports data in the same format expected by the migration tool:

```json
[
  {
    "id": "MSG_001",
    "createdDateTime": "2026-01-08T14:00:00Z",
    "from": {
      "user": {
        "id": "user-id",
        "displayName": "John Doe"
      }
    },
    "body": {
      "contentType": "html",
      "content": "<div>Message text</div>"
    },
    "attachments": [],
    "replies": []
  }
]
```

## Complete Workflow

```powershell
# 1. Fetch from Teams
$env:AZURE_CLIENT_ID = "your-client-id"
python -m teams_to_slack.teams_fetcher

# 2. Run migration
python migrate.py

# Output in data/output/
```

## Troubleshooting

### "Error: Insufficient privileges"
- Ensure API permissions are granted
- Admin consent may be required

### "Authentication timeout"
- User didn't complete authentication in time
- Re-run the script

### "Channel not found"
- Verify channel ID is correct
- Ensure user has access to the channel

### "Too many requests"
- Rate limit hit
- Add delays between requests
- Reduce batch size

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Rotate access tokens** regularly
4. **Use least-privilege permissions** only what's needed
5. **Audit API usage** via Azure AD logs

## Additional Resources

- [Microsoft Graph API Docs](https://docs.microsoft.com/graph)
- [Teams Messages API](https://docs.microsoft.com/graph/api/channel-list-messages)
- [Azure AD App Registration](https://docs.microsoft.com/azure/active-directory/develop/quickstart-register-app)
- [Device Code Flow](https://docs.microsoft.com/azure/active-directory/develop/v2-oauth2-device-code)
