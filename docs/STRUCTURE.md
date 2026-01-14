# Project Structure Guide

## Overview

This is a **production-grade** project with professional organization following Python best practices.

## Directory Organization

### `/src` - Source Code
Main application code organized as a Python package.

```
src/teams_to_slack/
├── __init__.py         # Package initialization & exports
├── migration.py        # Core migration logic (main class)
├── utils.py           # Utility functions
└── __main__.py        # Module entry point for direct execution
```

**Key principle**: Source code is in `/src` to keep project root clean.

### `/tests` - Testing
Comprehensive test suite for quality assurance.

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration
├── unit/                    # Unit tests
│   ├── __init__.py
│   └── test_migration.py   # Core logic tests
├── integration/             # Integration tests
│   ├── __init__.py
│   └── test_pipeline.py    # End-to-end tests
└── fixtures/                # Test data & mocks
```

**Run tests**: `pytest tests/`

### `/config` - Configuration
All configuration files in one place.

```
config/
├── settings.json        # Runtime configuration
└── user_mapping.json    # Teams→Slack ID mapping
```

**Usage**: Loaded at runtime, environment-specific overrides possible.

### `/data` - Data Management
Organized input/output structure.

```
data/
├── input/               # Teams export files
│   └── teams_convo.json # Sample input
└── output/              # Generated Slack exports
    └── 2026-01-08.json # Sample output
    └── attachments/    # Downloaded files
```

**Separation**: Clear input/output distinction.

### `/docs` - Documentation
Comprehensive documentation organized by type.

```
docs/
├── README.md            # Main documentation
├── guides/              # How-to guides
│   └── README.md       # User guide
└── api/                 # API documentation
    └── API.md          # API reference
```

### `/logs` - Logging
Centralized log storage.

```
logs/
└── migration.log        # Execution logs (auto-created)
```

### `/scripts` - Utility Scripts
Helper scripts for common tasks.

```
scripts/
└── utilities/           # Organized by function
```

### `/.github` - GitHub Integration
CI/CD and repository configuration.

```
.github/
└── workflows/           # GitHub Actions
    └── tests.yml       # Automated testing
```

### `/build` & `/dist` - Distribution
Build artifacts (auto-generated).

```
build/                   # Intermediate build files
dist/                    # Distribution packages
```

## Root Level Files

### Configuration & Setup
- `setup.py` - Package installation configuration
- `requirements.txt` - Python dependencies
- `Makefile` - Build automation commands
- `.env.example` - Environment variable template
- `.gitignore` - Git configuration

### Main Entry Points
- `migrate.py` - Primary entry point for users
- `README.md` - Quick start guide
- `INDEX.md` - Project navigation
- `DEPLOYMENT.md` - Production deployment guide
- `ASSESSMENT_SUBMISSION.md` - Assessment proof

## File Organization Principles

### 1. Separation of Concerns
- Source code → `/src`
- Tests → `/tests`
- Configuration → `/config`
- Data → `/data`
- Documentation → `/docs`

### 2. Python Package Standards
- `__init__.py` in all packages
- `src/` layout for main code
- `setup.py` for packaging
- `requirements.txt` for dependencies

### 3. Production Readiness
- Centralized logging (`/logs`)
- Configuration management (`/config`)
- CI/CD workflows (`.github/workflows`)
- Comprehensive documentation (`/docs`)

### 4. Scalability
- Modular code in `/src`
- Test coverage in `/tests`
- Input/output separation in `/data`
- Resource isolation (`/logs`, `/build`)

## Usage Examples

### Running Migration
```bash
# From any directory
python migrate.py

# Or as installed package
python -m teams_to_slack
```

### Running Tests
```bash
# All tests
pytest tests/

# Specific suite
pytest tests/unit/
pytest tests/integration/

# With coverage
pytest tests/ --cov=src
```

### Build Commands
```bash
# Using Makefile
make install      # Install dependencies
make test         # Run tests
make migrate      # Run migration
make build        # Create distribution
make clean        # Clean artifacts
```

## Best Practices

✓ **Source in `/src`**: Keeps project root clean
✓ **Tests alongside code**: Easy to find and maintain
✓ **Configuration external**: Settings not hardcoded
✓ **Data separation**: Clear input/output boundaries
✓ **Documentation together**: All docs in one place
✓ **CI/CD integrated**: Automated quality checks
✓ **Logging centralized**: All logs in `/logs`

## Migration Path

This structure supports:
- **Local development**: Easy to understand and modify
- **CI/CD pipeline**: GitHub Actions ready
- **Distribution**: Setup.py ready for PyPI
- **Docker deployment**: Can be containerized
- **Scaling**: Modular design allows easy extension

## Example: Adding a New Feature

1. Create feature in `/src/teams_to_slack/new_feature.py`
2. Write tests in `/tests/unit/test_new_feature.py`
3. Update documentation in `/docs`
4. Update `__init__.py` to export new feature
5. Run tests: `pytest tests/`
6. Commit: Git will follow `.gitignore`

## Configuration Hierarchy

Files are loaded in order (later overwrites earlier):
1. `config/settings.json` (base)
2. `.env` (environment overrides)
3. Command-line arguments (CLI overrides)

## Database/Artifact Locations

- **Input data**: `data/input/`
- **Output data**: `data/output/`
- **Attachments**: `data/output/attachments/`
- **Logs**: `logs/`
- **Build artifacts**: `build/`, `dist/`

---

**Status**: ✅ Production-Grade Structure
