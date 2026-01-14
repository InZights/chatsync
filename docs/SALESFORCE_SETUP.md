# Salesforce Data Cloud Integration Guide

## Overview

Load your migrated conversation data into Salesforce Data Cloud for advanced analytics, AI insights, and CRM integration.

## Use Cases

- **Customer 360**: Enrich customer profiles with conversation history
- **Sentiment Analysis**: Track customer satisfaction and sentiment trends
- **Lead Scoring**: Score leads based on engagement patterns
- **Support Analytics**: Analyze support conversation quality and response times
- **Einstein AI**: Use conversation data for predictive insights
- **Churn Prediction**: Identify at-risk customers from conversation patterns

---

## Prerequisites

### 1. Salesforce Edition
- Salesforce Data Cloud license
- OR Enterprise/Unlimited Edition with Bulk API access
- API-enabled user profile

### 2. Connected App Setup

#### Step 1: Create Connected App
1. In Salesforce, go to **Setup** → **App Manager**
2. Click **New Connected App**
3. Fill in basic information:
   - **Connected App Name**: `Teams Migration Integration`
   - **API Name**: `Teams_Migration_Integration`
   - **Contact Email**: your_email@company.com

#### Step 2: Enable OAuth Settings
4. Check **Enable OAuth Settings**
5. **Callback URL**: `https://localhost:1717/callback` (can be placeholder)
6. **Selected OAuth Scopes**:
   - `api` - Access and manage your data
   - `refresh_token, offline_access` - Perform requests on your behalf at any time
   - `cdp_ingest_api` - Access Data Cloud Ingestion API (if using Data Cloud)

7. Click **Save**
8. Click **Continue**

#### Step 3: Get Credentials
9. Click **Manage Consumer Details**
10. Copy your **Consumer Key** (Client ID)
11. Copy your **Consumer Secret** (Client Secret)

#### Step 4: Enable Password Flow (Required)
12. From the Connected App detail page, click **Edit Policies**
13. In **OAuth Policies**:
    - **Permitted Users**: All users may self-authorize
    - **IP Relaxation**: Relax IP restrictions
14. Click **Save**

### 3. User Security Token
1. Go to **Settings** → **My Personal Information** → **Reset My Security Token**
2. Click **Reset Security Token**
3. Check your email for the new token
4. Your password for API calls = `your_password` + `security_token`

---

## Configuration

### 1. Update `.env` File

```bash
# Copy example
cp .env.example .env

# Edit .env
```

Add these credentials to your `.env` file:

```dotenv
# Salesforce Configuration
SALESFORCE_INSTANCE_URL=https://login.salesforce.com
SALESFORCE_CLIENT_ID=3MVG9...your_client_id
SALESFORCE_CLIENT_SECRET=ABC123...your_client_secret
SALESFORCE_USERNAME=your.email@company.com
SALESFORCE_PASSWORD=YourPassword123
SALESFORCE_SECURITY_TOKEN=Abc123XYZ456

# Optional: Data Cloud Ingestion API
DATA_CLOUD_INGESTION_API=https://yourinstance.my.salesforce.com/services/data/v59.0/connect/ingest
DATA_CLOUD_SOURCE_API_NAME=Teams_Conversations
```

**⚠️ Security Note**: Never commit `.env` to version control. It's already in `.gitignore`.

---

## Data Model

### Option A: Use Standard Objects (Quick Start)

Create a custom object called `Conversation_Message__c`:

#### Fields:
```
Message_ID__c (Text, 255, Unique, External ID)
Timestamp__c (DateTime)
Text__c (Long Text Area, 4000)
User_ID__c (Text, 50)
Thread_TS__c (Text, 50)
Channel__c (Text, 100)
Source_System__c (Text, 50)
Has_Attachments__c (Checkbox)
Is_Threaded__c (Checkbox)
```

### Option B: Use Data Cloud (Recommended)

#### Create Data Stream:
1. Go to **Data Cloud** → **Data Streams**
2. Click **New** → **Other Connectors**
3. Select **Ingestion API**
4. Configure:
   - **Source Name**: `Teams_Conversations`
   - **API Name**: `Teams_Conversations`
   
5. Define schema matching the transformed data:
   - `message_id` (Text)
   - `timestamp` (DateTime)
   - `text` (Text)
   - `user_id` (Text)
   - `thread_ts` (Text)
   - `channel` (Text)
   - And other fields from the script...

---

## Usage

### Basic Upload (Bulk API)

```bash
# Set environment variables
$env:SALESFORCE_CLIENT_ID = "your_client_id"
$env:SALESFORCE_CLIENT_SECRET = "your_secret"
$env:SALESFORCE_USERNAME = "your_email@company.com"
$env:SALESFORCE_PASSWORD = "YourPasswordAndToken"

# Run the script
python scripts/load_to_salesforce.py
```

### Interactive Mode

The script will:
1. Authenticate with Salesforce
2. Ask which upload method to use:
   - **Bulk API 2.0** (recommended for large datasets)
   - **Data Cloud Ingestion API** (streaming)
3. Transform and upload all messages
4. Show progress and summary

### Command Options

```python
# In your own script
from scripts.load_to_salesforce import SalesforceDataCloudLoader

loader = SalesforceDataCloudLoader(
    instance_url='https://yourinstance.my.salesforce.com',
    client_id='your_client_id',
    client_secret='your_secret',
    username='user@company.com',
    password='password+token'
)

# Upload with custom settings
loader.load_from_output_directory(
    output_dir='data/output',
    batch_size=1000,
    use_bulk_api=True
)

loader.print_summary()
```

---

## Data Transformation

The script automatically transforms Slack-formatted messages to Salesforce-compatible format:

### Input (Slack Format):
```json
{
  "type": "message",
  "user": "U01ABC",
  "text": "Hello team!",
  "ts": "1704672000.123456",
  "thread_ts": "1704672000.123456",
  "channel": "migrated-teams"
}
```

### Output (Salesforce Format):
```json
{
  "message_id": "U01ABC_1704672000.123456",
  "timestamp": "2024-01-08T00:00:00",
  "text": "Hello team!",
  "user_id": "U01ABC",
  "thread_ts": "1704672000.123456",
  "is_threaded": true,
  "channel": "migrated-teams",
  "source_system": "teams"
}
```

---

## Upload Methods

### 1. Bulk API 2.0 (Recommended)

**Best for**: Large datasets (100K+ records)

**Advantages**:
- Asynchronous processing
- High throughput
- Automatic retry
- No API call limits

**Process**:
1. Creates bulk job
2. Uploads data in batches
3. Monitors job status in Salesforce

**Check Status**:
- Go to **Setup** → **Bulk Data Load Jobs**
- Find your job by timestamp
- View success/failure details

### 2. Data Cloud Ingestion API

**Best for**: Real-time streaming, smaller batches

**Advantages**:
- Real-time ingestion
- Direct to Data Cloud
- No object creation needed

**Requirements**:
- Data Cloud license
- Pre-configured Data Stream

---

## Monitoring & Troubleshooting

### Check Upload Status

#### For Bulk API:
```
Setup → Bulk Data Load Jobs
→ Find your job
→ View results
```

#### For Data Cloud:
```
Data Cloud → Data Streams
→ Teams_Conversations
→ View Ingestion Status
```

### Common Issues

#### Authentication Failed
```
❌ Error: Authentication failed: 400 Client Error
```
**Solution**: 
- Verify CLIENT_ID and CLIENT_SECRET
- Ensure password includes security token
- Check IP restrictions on Connected App

#### Invalid Grant
```
❌ invalid_grant: authentication failure
```
**Solution**:
- Reset security token
- Update password in `.env`
- Format: `SALESFORCE_PASSWORD=yourpasswordYOURSECURITYTOKEN`

#### Object Not Found
```
❌ sObject type 'Conversation_Message__c' is not supported
```
**Solution**: Create the custom object first (see Data Model section)

#### Data Cloud API Not Found
```
❌ Error: Data Cloud Ingestion API URL not configured
```
**Solution**: 
- Set `DATA_CLOUD_INGESTION_API` in `.env`
- OR use Bulk API instead (option 1)

---

## Analytics & Insights

Once data is loaded, you can:

### 1. Create Reports
- Conversation volume by date
- Top active users
- Thread depth analysis
- Response time metrics

### 2. Build Dashboards
- Real-time conversation analytics
- Sentiment trends (after sentiment analysis)
- User engagement scores

### 3. Einstein Analytics
- Predictive lead scoring
- Churn risk prediction
- Conversation topic clustering

### 4. Data Cloud Insights
- Unified customer profiles
- Cross-channel engagement
- Journey orchestration

---

## Next Steps

1. **✅ Load conversation data** using this script
2. **📊 Create custom reports** in Salesforce
3. **🤖 Build AI/ML models** (sentiment, lead scoring, churn)
4. **🔄 Automate periodic sync** with scheduled jobs
5. **📈 Visualize insights** in dashboards

---

## Best Practices

### Security
- Use environment variables for credentials
- Enable IP restrictions on Connected App
- Use OAuth 2.0 JWT flow for production (instead of password flow)
- Rotate security tokens regularly

### Performance
- Use Bulk API for large datasets (>10K records)
- Batch size: 1000-5000 records optimal
- Run during off-peak hours for large loads
- Monitor API usage limits

### Data Quality
- Validate data before upload
- Handle duplicates (use External ID)
- Archive old conversation data
- Set up data retention policies

---

## Support

### Salesforce Resources
- [Bulk API 2.0 Documentation](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/)
- [Data Cloud Ingestion API](https://developer.salesforce.com/docs/atlas.en-us.c360a_api.meta/c360a_api/)
- [Connected Apps Setup](https://help.salesforce.com/s/articleView?id=sf.connected_app_create.htm)

### Project Issues
- GitHub Issues: [Report a bug]
- Documentation: See [docs/README.md](README.md)

---

**Ready to load your data?**

```bash
python scripts/load_to_salesforce.py
```
