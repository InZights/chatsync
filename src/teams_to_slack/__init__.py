"""Teams to Slack Migration Tool - Main Package"""

__version__ = "1.0.0"
__author__ = "Data Pipeline Team"
__description__ = "Production-grade migration tool for Teams to Slack conversations"

from .migration import SlackMigrationTool

__all__ = ['SlackMigrationTool']
