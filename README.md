<div align="center">

# 🌉 ConvoHub

### **Enterprise Conversation Data Platform**

*Transform, migrate, and analyze conversations across Microsoft Teams, Slack, and Salesforce Data Cloud*

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Use Cases](#-use-cases)

</div>

---

## 📋 Overview

**ConvoHub** is a production-grade data pipeline that extracts conversation data from Microsoft Teams, transforms it into standardized formats, and loads it into multiple destinations including Slack and Salesforce Data Cloud. Built for enterprise scale (1K to 10M+ messages), it enables conversation analytics, customer 360 views, and AI-powered insights.


### What It Does

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Microsoft  │      │              │      │              │      │  Salesforce  │
│    Teams     │ ───> │   ConvoHub   │ ───> │    Slack     │      │ Data Cloud   │
│              │      │  (Transform) │      │              │      │  (Analytics) │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
   Messages                  │                   Messages            AI/ML Models
   Threads                   │                   Channels            Reports
   Files                     └────────────────────────────────>      Insights
```

**Perfect for:**
- 🏢 **Enterprise Migration**: Moving from Teams to Slack with full history
- 📊 **Conversation Analytics**: Build dashboards and reports in Salesforce
- 🤖 **AI/ML Training**: Feed conversation data to sentiment analysis, lead scoring, churn prediction
- 📚 **Knowledge Management**: Archive and search historical conversations
- 🎯 **Customer 360**: Enrich CRM with conversation context

---

## ✨ Features

### 🚀 Production-Ready Pipeline
- **Streaming Processing**: Memory-efficient JSON parsing for massive datasets
- **Batch Operations**: Process 1000+ messages per batch
- **Error Recovery**: Comprehensive error handling and retry logic
- **Audit Trail**: Full logging with timestamps and statistics

### 🔄 Data Transformation
- ✅ **Format Conversion**: Teams JSON → Slack JSON → Salesforce format
- ✅ **Thread Preservation**: Maintains parent-child conversation relationships
- ✅ **User Mapping**: Automatic ID mapping between platforms
- ✅ **Deduplication**: SHA-256 hash-based duplicate detection
- ✅ **Content Sanitization**: HTML → Markdown conversion
- ✅ **Timestamp Normalization**: ISO 8601 and epoch timestamp handling

### 🔗 Multi-Platform Integration

#### Microsoft Teams
- Microsoft Graph API integration
- Device code authentication
- Multi-channel export
- Reply/thread fetching

#### Slack
- Slack SDK integration
- Direct API upload
- Channel creation/discovery
- Rate limiting & retry

#### Salesforce Data Cloud ⭐
- OAuth 2.0 authentication
- Bulk API 2.0 support (high volume)
- Ingestion API support (streaming)
- Custom object mapping
- Batch upload with progress tracking

### 📊 Monitoring & Alerts
- Real-time Slack notifications
- Migration progress tracking
- Error rate monitoring
- Success/failure reporting
- Comprehensive statistics

---

## 🎯 Use Cases

<table>
<tr>
<td width="50%">

### 📈 Analytics & Insights
- Track conversation volume trends
- Measure response times
- Identify top contributors
- Analyze engagement patterns
- Build custom dashboards

</td>
<td width="50%">

### 🤖 AI & Machine Learning
- **Sentiment Analysis**: Track team/customer sentiment
- **Topic Modeling**: Auto-categorize conversations
- **Lead Scoring**: Score based on engagement
- **Churn Prediction**: Identify at-risk users
- **Intent Classification**: Route conversations

</td>
</tr>
<tr>
<td width="50%">

### 🏢 Enterprise Operations
- Platform migration (Teams → Slack)
- Compliance & archival
- Knowledge base creation
- Audit trail maintenance
- Cross-platform search

</td>
<td width="50%">

### 🎯 CRM Enhancement
- Customer 360 views
- Enrich contact records
- Support ticket context
- Sales conversation history
- Einstein AI integration

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Microsoft Teams account (for data fetching)
- Slack workspace (optional - for upload)
- Salesforce org (optional - for analytics)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/convohub.git
cd convohub

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Basic Usage

#### Option 1: Fetch from Teams & Migrate
```bash
# Set Azure credentials
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant-id"

# Run interactive workflow
python scripts/fetch_and_migrate.py
```

#### Option 2: Migrate Existing Data
```bash
# Place Teams export in data/input/teams_convo.json
python migrate.py
```

#### Option 3: Load to Salesforce
```bash
# Configure Salesforce credentials in .env
python scripts/load_to_salesforce.py
```


---

## 📖 Documentation

### Getting Started
- **[Installation Guide](docs/guides/README.md)** - Detailed setup instructions
- **[Configuration](config/settings.json)** - Runtime configuration options
- **[User Mapping](config/user_mapping.json)** - ID mapping between platforms

### Platform Setup
- **[Microsoft Teams API Setup](docs/TEAMS_API_SETUP.md)** - Azure AD app registration & permissions
- **[Slack Integration](docs/NOTIFICATIONS_SETUP.md)** - Bot setup & webhooks
- **[Salesforce Data Cloud Setup](docs/SALESFORCE_SETUP.md)** - Connected app & authentication

### Architecture
- **[Project Structure](docs/STRUCTURE.md)** - Code organization & design patterns
- **[System Flow](SOLUTION_SUMMARY.md)** - Data flow diagrams
- **[API Documentation](docs/api/API.md)** - Class & method references

### Deployment
- **[Production Checklist](PRODUCTIONIZATION_CHECKLIST.md)** - Pre-deployment validation
- **[Deployment Guide](DEPLOYMENT.md)** - Server setup & automation

---

## 🏗️ Architecture

### Project Structure

```
convohub/
├── 📂 src/teams_to_slack/         # Core library
│   ├── migration.py               # Main migration engine
│   ├── teams_fetcher.py           # Microsoft Teams API client
│   ├── slack_notifier.py          # Notification system
│   └── utils.py                   # Helper functions
│
├── 📂 scripts/                    # Executable tools
│   ├── fetch_and_migrate.py       # Interactive workflow
│   ├── load_to_salesforce.py      # Salesforce uploader
│   ├── test_notifications.py      # Test alerts
│   └── validate_solution.py       # System validation
│
├── 📂 config/                     # Configuration
│   ├── settings.json              # Runtime config
│   └── user_mapping.json          # User ID mappings
│
├── 📂 data/                       # Data storage
│   ├── input/                     # Source files
│   └── output/                    # Transformed files
│       └── attachments/           # Downloaded files
│
├── 📂 docs/                       # Documentation
│   ├── TEAMS_API_SETUP.md
│   ├── SALESFORCE_SETUP.md
│   └── NOTIFICATIONS_SETUP.md
│
├── 📂 tests/                      # Test suite
│   ├── unit/                      # Unit tests
│   └── integration/               # Integration tests
│
├── migrate.py                     # Main entry point
└── requirements.txt               # Dependencies
```

### System Flow

```
Stage 1: DATA ACQUISITION (Microsoft Teams)
┌────────────────────────────────────────────┐
│  teams_fetcher.py                          │
│  ├─ Microsoft Graph API                    │
│  ├─ Device code authentication             │
│  └─ Multi-channel export                   │
└────────────┬───────────────────────────────┘
             │
             ↓ data/input/teams_convo.json
             
Stage 2: TRANSFORMATION & MIGRATION
┌────────────────────────────────────────────┐
│  migrate.py → SlackMigrationTool           │
│  ├─ Streaming JSON parser                  │
│  ├─ Teams → Slack format                   │
│  ├─ SHA-256 deduplication                  │
│  ├─ Thread preservation                    │
│  └─ User ID mapping                        │
└────────────┬───────────────────────────────┘
             │
             ↓ data/output/YYYY-MM-DD.json
             
Stage 3: SLACK UPLOAD (Optional)
┌────────────────────────────────────────────┐
│  Slack API Integration                     │
│  ├─ Channel creation                       │
│  ├─ Message posting                        │
│  └─ Rate limiting                          │
└────────────┬───────────────────────────────┘
             │
             ↓ Slack Workspace
             
Stage 4: SALESFORCE DATA CLOUD ⭐
┌────────────────────────────────────────────┐
│  load_to_salesforce.py                     │
│  ├─ OAuth 2.0 authentication               │
│  ├─ Slack → Salesforce format              │
│  ├─ Bulk API 2.0 / Ingestion API          │
│  └─ Batch upload (1000 records/batch)     │
└────────────┬───────────────────────────────┘
             │
             ↓ Salesforce Data Cloud
             
Stage 5: ANALYTICS & AI (Future)
┌────────────────────────────────────────────┐
│  ├─ Sentiment Analysis                     │
│  ├─ Topic Modeling                         │
│  ├─ Lead Scoring                           │
│  └─ Churn Prediction                       │
└────────────────────────────────────────────┘
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following:

```bash
# ============================================================================
# MICROSOFT TEAMS
# ============================================================================
AZURE_CLIENT_ID=your-azure-client-id
AZURE_TENANT_ID=common

# ============================================================================
# SLACK
# ============================================================================
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_CHANNEL=migrated-teams
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# ============================================================================
# SALESFORCE DATA CLOUD
# ============================================================================
SALESFORCE_INSTANCE_URL=https://login.salesforce.com
SALESFORCE_CLIENT_ID=your_client_id
SALESFORCE_CLIENT_SECRET=your_client_secret
SALESFORCE_USERNAME=user@company.com
SALESFORCE_PASSWORD=password
SALESFORCE_SECURITY_TOKEN=token
DATA_CLOUD_INGESTION_API=https://your-instance.my.salesforce.com/services/data/v59.0/connect/ingest
```

### Runtime Configuration

Edit `config/settings.json`:

```json
{
  "migration": {
    "dry_run": false,
    "batch_size": 1000,
    "input_file": "data/input/teams_convo.json",
    "output_dir": "data/output"
  },
  "slack": {
    "channel_name": "migrated-teams",
    "upload_enabled": false,
    "api_rate_limit_per_second": 50
  },
  "features": {
    "deduplication": true,
    "attachment_processing": true
  },
  "notifications": {
    "enabled": true,
    "notification_channel": "#migration-alerts"
  }
}
```

---

## 🔍 Examples

### Example 1: Migrate Single Channel

```python
from teams_to_slack import SlackMigrationTool

# Initialize tool
tool = SlackMigrationTool(
    user_map={'teams-user-1': 'slack-user-1'},
    channel_name='migrated-channel',
    dry_run=False
)

# Process Teams export
tool.process_export_streaming('data/input/teams_convo.json')

# Export to Slack format
tool.export_to_slack_format('data/output')

# Print report
tool.print_migration_report()
```

### Example 2: Load to Salesforce

```python
from scripts.load_to_salesforce import SalesforceDataCloudLoader

# Initialize loader
loader = SalesforceDataCloudLoader(
    instance_url='https://yourinstance.my.salesforce.com',
    client_id='your_client_id',
    client_secret='your_secret',
    username='user@company.com',
    password='password+token'
)

# Load all output files
loader.load_from_output_directory(
    output_dir='data/output',
    batch_size=1000,
    use_bulk_api=True
)

# Show summary
loader.print_summary()
```

### Example 3: Batch Processing with Notifications

```python
from teams_to_slack import SlackMigrationTool
from teams_to_slack.slack_notifier import SlackNotifier

# Setup notifications
notifier = SlackNotifier(
    webhook_url='https://hooks.slack.com/services/YOUR/WEBHOOK',
    notification_channel='#migration-alerts',
    enabled=True
)

# Run migration with monitoring
tool = SlackMigrationTool(
    user_map={},
    notifier=notifier,
    batch_size=5000
)

tool.process_export_streaming('data/input/teams_convo.json')
tool.export_to_slack_format('data/output')
```

---

## 📊 Performance

### Benchmarks

| Dataset Size | Processing Time | Memory Usage | Output Size |
|--------------|----------------|--------------|-------------|
| 1K messages  | 5 seconds      | 50 MB        | 2 MB        |
| 10K messages | 45 seconds     | 120 MB       | 18 MB       |
| 100K messages| 7 minutes      | 250 MB       | 180 MB      |
| 1M messages  | 65 minutes     | 400 MB       | 1.8 GB      |

*Tested on: Intel i7, 16GB RAM, SSD*

### Optimization Features

- ✅ Streaming JSON parser (constant memory)
- ✅ Batch processing (configurable batch size)
- ✅ Lazy loading (process on-demand)
- ✅ Chunked file uploads
- ✅ Connection pooling
- ✅ Rate limiting & backoff

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/

# Validate installation
python scripts/validate_solution.py

# Test notifications
python scripts/test_notifications.py
```

---

## 🛡️ Security

- 🔒 **Credentials**: Store in `.env` (never commit)
- 🔒 **OAuth 2.0**: Secure authentication flows
- 🔒 **API Keys**: Environment variables only
- 🔒 **Data**: Local processing, no external storage
- 🔒 **Audit**: Comprehensive logging
- 🔒 **Compliance**: GDPR-ready data handling

**Best Practices:**
- Rotate tokens regularly
- Use service accounts for production
- Enable IP restrictions on Connected Apps
- Review logs for suspicious activity
- Implement data retention policies

---

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><b>Authentication Failed</b></summary>

```bash
❌ Error: Authentication failed
```

**Solution:**
- Verify credentials in `.env`
- Check API permissions
- Ensure security token is appended to password (Salesforce)
- Try resetting tokens
</details>

<details>
<summary><b>Memory Error with Large Datasets</b></summary>

```bash
❌ MemoryError: Unable to allocate array
```

**Solution:**
- Reduce batch size in `config/settings.json`
- Use streaming mode (enabled by default)
- Process in smaller chunks
- Increase available RAM
</details>

<details>
<summary><b>Rate Limit Exceeded</b></summary>

```bash
❌ Error 429: Rate limit exceeded
```

**Solution:**
- Reduce `api_rate_limit_per_second` in config
- Add delays between batches
- Use Bulk API instead of real-time API
- Check platform rate limits
</details>

**More help:** [Open an issue](https://github.com/yourusername/convohub/issues)

---

## 🗺️ Roadmap

### ✅ Completed
- [x] Teams to Slack migration
- [x] Salesforce Data Cloud integration
- [x] Slack notifications
- [x] Bulk API support
- [x] Comprehensive documentation

### 🚧 In Progress
- [ ] Sentiment analysis module
- [ ] Topic modeling (BERTopic)
- [ ] Web dashboard
- [ ] REST API

### 📋 Planned
- [ ] Lead scoring model
- [ ] Churn prediction
- [ ] Google Chat integration
- [ ] Discord support
- [ ] Real-time streaming mode
- [ ] GraphQL API
- [ ] Docker containerization
- [ ] Kubernetes deployment

**Have a feature request?** [Open an issue](https://github.com/yourusername/convohub/issues/new)

---

## 🤝 Contributing

We welcome contributions! To contribute:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone repo
git clone https://github.com/yourusername/convohub.git
cd convohub

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black src/ scripts/

# Lint
flake8 src/ scripts/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 ConvoHub

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 🙏 Acknowledgments

- **Microsoft Graph API** - Teams data access
- **Slack SDK** - Slack integration
- **Salesforce APIs** - Data Cloud integration
- **Python Community** - Amazing libraries and tools

---

## 📞 Support

<div align="center">

**Need Help?**

[📖 Documentation](docs/) • [💬 Discussions](https://github.com/yourusername/convohub/discussions) • [🐛 Issues](https://github.com/yourusername/convohub/issues)

---

**Made with ❤️ by the ConvoHub Team**

⭐ **Star this repo** if you find it useful!

</div>
