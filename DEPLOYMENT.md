# Production Deployment Guide

## Overview
This document covers deploying the Teams-to-Slack migration pipeline in production environments.

---

## Pre-Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Slack Bot Token generated and stored securely
- [ ] Teams export data available and validated
- [ ] User mapping CSV prepared (if 1000+ users)
- [ ] Target Slack workspace ready
- [ ] Monitoring and alerting configured

---

## Deployment Scenarios

### Scenario 1: Small Migration (< 10K messages)
**Estimated time**: 1-5 minutes

```bash
# 1. Prepare data
cp data/teams_convo.json data/teams_export.json

# 2. Run migration
python pipeline/script.py

# 3. Import to Slack
# Use Slack UI: Settings → Workspace → Import Data

# 4. Verify
# Check slack_export/*.json for output
```

### Scenario 2: Large Migration (10K - 1M messages)
**Estimated time**: 30 min - 2 hours

```bash
# 1. Run in dry-run mode first
python pipeline/script.py --dry-run

# 2. Verify output
ls -lh slack_export/

# 3. Full migration with API upload
export SLACK_BOT_TOKEN="xoxb-..."
python pipeline/script.py

# 4. Monitor
tail -f migration.log
```

### Scenario 3: Enterprise Migration (1M+ messages)
**Estimated time**: 2-12 hours

```bash
# 1. Split dataset by date range
python scripts/split_by_date.py data/teams_export.json

# 2. Run in parallel (if infrastructure supports)
for file in data/split_*.json; do
    python pipeline/script.py --input "$file" &
done
wait

# 3. Combine results
python scripts/merge_outputs.py slack_export/

# 4. Upload in batches
python scripts/batch_upload.py --channel migrated-teams

# 5. Final verification
python scripts/verify_migration.py
```

---

## Configuration

### Environment Variables
```bash
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export DRY_RUN="false"
export LOG_LEVEL="INFO"
export BATCH_SIZE="1000"
```

### config.json Customization
```json
{
  "migration": {
    "batch_size": 5000,           # Increase for better throughput
    "max_message_length": 4000    # Slack's limit
  },
  "slack": {
    "api_rate_limit_per_second": 100  # Adjust based on tier
  }
}
```

---

## Monitoring & Logging

### Real-time Monitoring
```bash
# Watch migration in real-time
tail -f migration.log | grep -i "error\|warning"

# Stats
grep "Total Messages" migration.log
```

### Health Checks
```bash
# Verify all messages were processed
python scripts/validation.py slack_export/

# Compare counts
echo "Teams messages: $(grep -c '"id"' data/teams_export.json)"
echo "Slack messages: $(grep -c '"ts"' slack_export/*.json)"
```

### Performance Profiling
```bash
# Time the migration
time python pipeline/script.py

# Memory usage
python -m memory_profiler pipeline/script.py
```

---

## Error Handling & Recovery

### Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Invalid input path | Check config.json input_file |
| `SlackApiError: invalid_auth` | Bad token | Verify SLACK_BOT_TOKEN |
| `MemoryError` | Dataset too large | Increase batch_size or split data |
| `JSONDecodeError` | Corrupted Teams export | Re-download export |

### Recovery Procedures

**Partial Failure - Restart Migration**
```bash
# Script is idempotent for file exports
# Run again - will skip already processed messages
python pipeline/script.py

# Check migration.log for failed message IDs
grep "failed" migration.log > failed_ids.txt
```

**API Upload Failure - Retry**
```bash
# Upload only failed messages
python scripts/retry_upload.py failed_ids.txt
```

---

## Performance Optimization

### For 1M+ Messages

**1. Increase Batch Size**
```json
{
  "migration": {
    "batch_size": 5000
  }
}
```

**2. Parallel Processing**
```bash
# Split by time range and process in parallel
python pipeline/script.py --split-by-week &
python pipeline/script.py --split-by-week &
```

**3. Use Slack Import API (Faster)**
```bash
# Instead of posting messages one-by-one
# Use native import tool with bulk_import.py
python scripts/bulk_import.py slack_export/
```

**4. Disable Unnecessary Features**
```json
{
  "features": {
    "attachment_processing": false,
    "deduplication": false
  }
}
```

### Expected Performance

| Dataset Size | Processing Time | API Upload Time | Total |
|---|---|---|---|
| 10K | 5 sec | 30 sec | 35 sec |
| 100K | 45 sec | 5 min | 5:45 |
| 1M | 8 min | 45 min | 53 min |
| 10M | 80 min | 8 hours | 9 hours |

---

## Post-Migration Verification

### Checklist
```bash
# 1. Count verification
TEAMS_COUNT=$(grep -c '"id"' data/teams_export.json)
SLACK_COUNT=$(grep -c '"ts"' slack_export/*.json | awk -F: '{sum+=$2} END {print sum}')
echo "Teams: $TEAMS_COUNT, Slack: $SLACK_COUNT"

# 2. Sample message verification
head -1 slack_export/*.json | grep -o '"ts"'

# 3. Thread integrity check
python scripts/verify_threads.py slack_export/

# 4. User mapping validation
python scripts/validate_users.py slack_export/
```

### Sign-Off
- [ ] Message counts match
- [ ] All threads preserved
- [ ] User mappings correct
- [ ] No orphaned replies
- [ ] Attachments (if enabled) accessible
- [ ] Migration log reviewed for errors

---

## Rollback Plan

If issues occur in Slack workspace:

```bash
# 1. Export affected conversation
python scripts/export_channel.py migrated-teams

# 2. Delete migrated messages (if needed)
python scripts/cleanup_channel.py migrated-teams

# 3. Fix Teams data
# Edit data/teams_export.json
# Re-run migration

# 4. Re-import to Slack
python pipeline/script.py
```

---

## Support & Maintenance

### Logs Location
- **Migration log**: `migration.log`
- **Detailed errors**: `error_details.json`
- **Performance metrics**: `metrics.json`

### Troubleshooting Commands
```bash
# View all errors
grep ERROR migration.log

# Extract failed message IDs
grep "Failed to transform" migration.log | grep -o 'MSG_[0-9]*'

# Show statistics
tail -30 migration.log | grep -E "Total|Successful|Failed"
```

### Contact
For issues, check:
1. `migration.log` for error messages
2. README.md for common issues
3. config.json for misconfigurations
