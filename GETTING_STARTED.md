# Getting Started with ConvoHub

Welcome to ConvoHub! This guide will help you set up and run your first conversation migration in under 10 minutes.

## 🎯 What You'll Achieve

By the end of this guide, you'll be able to:
- ✅ Fetch conversation data from Microsoft Teams
- ✅ Transform it into Slack-compatible format
- ✅ Optionally upload to Salesforce Data Cloud for analytics

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** installed
- **Git** for cloning the repository
- Access to one or more platforms:
  - Microsoft Teams (for data extraction)
  - Slack workspace (for upload - optional)
  - Salesforce org (for analytics - optional)

## 🚀 Installation (5 minutes)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/convohub.git
cd convohub
```

### Step 2: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env with your credentials (use any text editor)
notepad .env  # Windows
nano .env     # macOS/Linux
```

**Minimum configuration for testing (without credentials):**
```dotenv
# Leave as-is for testing with sample data
DRY_RUN=true
```

---

## 🏃 Quick Start - Three Ways to Use ConvoHub

### Option 1: Test with Sample Data (30 seconds)

The quickest way to see ConvoHub in action:

```bash
# Run migration with included sample data
python migrate.py
```

**What happens:**
- Reads sample Teams data from `data/input/teams_convo.json`
- Transforms to Slack format
- Outputs to `data/output/YYYY-MM-DD.json`
- Shows comprehensive report

**Expected output:**
```
============================================================
                MIGRATION REPORT
============================================================
✓ Total messages processed:      42
✓ Successfully transformed:       42
✓ Threads preserved:              8
...
```

### Option 2: Fetch from Microsoft Teams (5 minutes)

To fetch real data from your Teams workspace:

#### a. Set up Azure AD App (one-time)

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
   - Name: `ConvoHub Teams Fetcher`
   - Supported account types: **Accounts in this organizational directory only**
   - Click **Register**

4. Note your **Application (client) ID** and **Directory (tenant) ID**

5. Go to **API permissions** → **Add a permission** → **Microsoft Graph**
   - Select **Delegated permissions**
   - Add these permissions:
     - `Channel.ReadBasic.All`
     - `ChannelMessage.Read.All`
     - `Team.ReadBasic.All`
   - Click **Grant admin consent**

6. Go to **Authentication** → **Add a platform** → **Mobile and desktop applications**
   - Check: `https://login.microsoftonline.com/common/oauth2/nativeclient`
   - Click **Configure**

📖 **Detailed guide:** [docs/TEAMS_API_SETUP.md](docs/TEAMS_API_SETUP.md)

#### b. Configure credentials

Add to your `.env` file:
```dotenv
AZURE_CLIENT_ID=your-application-client-id
AZURE_TENANT_ID=your-tenant-id
```

#### c. Run the interactive workflow

```bash
python scripts/fetch_and_migrate.py
```

**What happens:**
1. Opens browser for device code authentication
2. Shows list of your Teams
3. Lets you select team and channel(s)
4. Downloads messages to `data/input/`
5. Runs migration automatically
6. Outputs to `data/output/`

### Option 3: Load to Salesforce Data Cloud (10 minutes)

To load conversation data into Salesforce for analytics:

#### a. Set up Salesforce Connected App (one-time)

1. Log into Salesforce
2. Go to **Setup** → **Apps** → **App Manager**
3. Click **New Connected App**
   - Connected App Name: `ConvoHub Integration`
   - API Name: `ConvoHub_Integration`
   - Contact Email: your-email@company.com
   - Enable OAuth Settings: ✓
   - Callback URL: `https://localhost:1717/callback`
   - OAuth Scopes:
     - `api` - Access and manage your data
     - `refresh_token, offline_access`

4. Click **Save** → **Continue**
5. Click **Manage Consumer Details** to get:
   - Consumer Key (Client ID)
   - Consumer Secret

6. Go to **Setup** → **My Personal Information** → **Reset Security Token**
   - Check email for security token

📖 **Detailed guide:** [docs/SALESFORCE_SETUP.md](docs/SALESFORCE_SETUP.md)

#### b. Configure credentials

Add to your `.env` file:
```dotenv
SALESFORCE_INSTANCE_URL=https://login.salesforce.com
SALESFORCE_CLIENT_ID=your_consumer_key
SALESFORCE_CLIENT_SECRET=your_consumer_secret
SALESFORCE_USERNAME=your_email@company.com
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_security_token
```

**Note:** Your password for API = `your_actual_password` + `security_token` (no space)

#### c. Load data to Salesforce

```bash
python scripts/load_to_salesforce.py
```

**What happens:**
1. Authenticates with Salesforce
2. Asks: Use Bulk API or Ingestion API?
3. Transforms Slack format → Salesforce format
4. Uploads in batches (1000 records each)
5. Shows progress and summary

---

## 🎓 Learning Path

### Beginner
1. ✅ Run with sample data (Option 1)
2. ✅ Review output in `data/output/`
3. ✅ Read [README.md](README.md) for features overview
4. ✅ Explore configuration in `config/settings.json`

### Intermediate
1. ✅ Set up Teams API access (Option 2)
2. ✅ Fetch real conversation data
3. ✅ Customize user mappings in `config/user_mapping.json`
4. ✅ Set up Slack notifications (see [docs/NOTIFICATIONS_SETUP.md](docs/NOTIFICATIONS_SETUP.md))

### Advanced
1. ✅ Set up Salesforce integration (Option 3)
2. ✅ Build Salesforce reports on conversation data
3. ✅ Implement sentiment analysis (coming soon)
4. ✅ Contribute to the project (see [CONTRIBUTING.md](CONTRIBUTING.md))

---

## 🔧 Configuration Deep Dive

### Runtime Configuration (`config/settings.json`)

```json
{
  "migration": {
    "dry_run": false,          // Set true to test without side effects
    "batch_size": 1000,        // Messages per batch (tune for performance)
    "input_file": "data/input/teams_convo.json",
    "output_dir": "data/output"
  },
  "slack": {
    "channel_name": "migrated-teams",
    "upload_enabled": false,   // Set true to upload to Slack
    "api_rate_limit_per_second": 50
  },
  "features": {
    "deduplication": true,     // Remove duplicate messages
    "attachment_processing": true
  },
  "notifications": {
    "enabled": true,           // Slack notifications
    "notification_channel": "#migration-alerts"
  }
}
```

### User Mapping (`config/user_mapping.json`)

Map Teams user IDs to Slack user IDs:

```json
{
  "teams-user-id-1": "slack-user-id-1",
  "teams-user-id-2": "slack-user-id-2"
}
```

**Tip:** Leave empty `{}` to auto-map unknown users to `U_GHOST`

---

## 📊 Understanding the Output

### Slack Format (`data/output/YYYY-MM-DD.json`)

Messages are organized by date:

```json
[
  {
    "type": "message",
    "user": "U01ABC",
    "text": "Hello team!",
    "ts": "1704672000.123456",
    "thread_ts": "1704672000.123456",
    "team": "T001BRYD"
  }
]
```

### Logs (`logs/migration.log`)

Detailed execution logs:

```
2026-01-15 10:30:00 - INFO - Starting migration...
2026-01-15 10:30:01 - INFO - Processing 1000 messages...
2026-01-15 10:30:05 - INFO - Batch 1/5 completed
```

---

## 🐛 Troubleshooting

### Common Issues

#### Problem: "Module not found"
```bash
ModuleNotFoundError: No module named 'teams_to_slack'
```
**Solution:**
```bash
# Make sure you're in the project root
cd convohub

# Reinstall dependencies
pip install -r requirements.txt
```

#### Problem: "Permission denied" errors
**Solution:** Make sure you've granted admin consent for Azure AD permissions

#### Problem: "Authentication failed" with Salesforce
**Solution:** 
- Verify your security token is appended to password
- Check that Connected App is configured correctly
- Ensure IP restrictions are relaxed

### Getting Help

- 📖 Read the [full documentation](README.md)
- 🔍 Search [existing issues](https://github.com/yourusername/convohub/issues)
- 💬 Ask in [discussions](https://github.com/yourusername/convohub/discussions)
- 🐛 [Report a bug](https://github.com/yourusername/convohub/issues/new)

---

## 🎉 Next Steps

Now that you're up and running:

1. **Explore the data**
   - Open output files in `data/output/`
   - View migration report

2. **Customize for your needs**
   - Modify `config/settings.json`
   - Set up user mappings
   - Enable notifications

3. **Integrate with your workflow**
   - Schedule regular migrations
   - Load data to Salesforce
   - Build analytics dashboards

4. **Contribute back**
   - Share your use case
   - Report bugs
   - Submit pull requests

---

## 📚 Additional Resources

### Documentation
- [README.md](README.md) - Main documentation
- [docs/STRUCTURE.md](docs/STRUCTURE.md) - Architecture overview
- [SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md) - Technical details

### Guides
- [Teams API Setup](docs/TEAMS_API_SETUP.md)
- [Salesforce Setup](docs/SALESFORCE_SETUP.md)
- [Notification Setup](docs/NOTIFICATIONS_SETUP.md)

### Examples
- See [README.md Examples section](README.md#-examples)
- Check `data/input/` for sample data

---

**Happy migrating! 🚀**

*Questions? Open an issue or start a discussion on GitHub.*
