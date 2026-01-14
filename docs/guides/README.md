# User Guide

## Installation

### Requirements
- Python 3.8+
- pip

### Steps

1. Clone repository
```bash
git clone <repo-url>
cd data_pipeline
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment
```bash
cp config/.env.example .env
# Edit .env with your settings
```

4. Set up Slack token (optional)
```bash
export SLACK_BOT_TOKEN="xoxb-..."
```

## Usage

### Basic Migration
```bash
python migrate.py
```

Output files will be in `data/output/`

### Check Results
```bash
ls data/output/
cat data/output/2026-01-08.json
```

### View Logs
```bash
tail -f logs/migration.log
```

## Configuration

Edit `config/settings.json`:

```json
{
  "migration": {
    "input_file": "data/input/teams.json",
    "output_dir": "data/output",
    "dry_run": false
  },
  "slack": {
    "channel_name": "migrated-teams"
  }
}
```

## User Mapping

Edit `config/user_mapping.json` to map Teams IDs to Slack IDs:

```json
{
  "T-USER-99": "U01ABC",
  "T-USER-44": "U02XYZ"
}
```

## Troubleshooting

### FileNotFoundError
Ensure input file exists in `data/input/`

### Invalid JSON
Check file encoding and format

### Memory Issues
Reduce batch size in settings.json

## Support

See logs/migration.log for detailed error information.
