# Teams to Slack Migration Pipeline

Production-grade migration tool for transforming Microsoft Teams conversations to Slack format.

## Quick Start

### Installation
```bash
pip install -r requirements.txt
python -m pip install -e .
```

### Basic Usage
```bash
python migrate.py
```

### With Slack Upload
```bash
export SLACK_BOT_TOKEN="xoxb-your-token"
python migrate.py
```

## Project Structure

```
data_pipeline/
├── src/teams_to_slack/          # Main application
│   ├── __init__.py
│   ├── migration.py             # Core migration logic
│   ├── utils.py                 # Utilities
│   └── __main__.py              # Entry point
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── fixtures/                # Test data
├── config/                       # Configuration files
├── data/
│   ├── input/                   # Input Teams exports
│   └── output/                  # Generated Slack exports
├── docs/                        # Documentation
├── logs/                        # Execution logs
├── scripts/                     # Utility scripts
├── migrate.py                   # Main entry point
├── requirements.txt             # Dependencies
├── setup.py                     # Package setup
└── Makefile                     # Build commands
```

## Features

- ✓ Memory-efficient streaming (handles 10M+ messages)
- ✓ Error handling & recovery
- ✓ Comprehensive logging
- ✓ User ID mapping
- ✓ Thread preservation
- ✓ HTML to Markdown conversion
- ✓ Deduplication
- ✓ Slack API integration

## Configuration

Edit `config/settings.json` to customize:
- Input/output directories
- Batch sizes
- Feature toggles
- Slack settings

## Testing

```bash
# Run all tests
make test

# Run specific test
pytest tests/unit/test_migration.py -v
```

## Documentation

- [User Guide](docs/guides/README.md)
- [Deployment](docs/DEPLOYMENT.md)
- [API Reference](docs/api/API.md)

## License

Internal Assessment Tool
