#!/usr/bin/env python
"""
Teams to Slack Migration Pipeline
Entry point for production deployment
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from teams_to_slack import SlackMigrationTool
from teams_to_slack.utils import load_config, load_user_mapping, create_output_dirs
from teams_to_slack.slack_notifier import SlackNotifier

# Configure logging
Path("logs").mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/migration.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    # Create output directories
    create_output_dirs()
    
    logger.info("Starting Teams to Slack migration...")
    
    # Load configuration
    config = load_config("config/settings.json")
    
    # Load user mapping
    user_map = load_user_mapping(json_path="config/user_mapping.json")
    
    # Initialize Slack notifier
    notifier = None
    notification_config = config.get("notifications", {})
    if notification_config.get("enabled", False):
        webhook_url = os.getenv(
            notification_config.get("webhook_url_env", "SLACK_WEBHOOK_URL")
        )
        bot_token = os.getenv(config.get("slack", {}).get("bot_token_env", "SLACK_BOT_TOKEN"))
        
        if webhook_url or bot_token:
            notifier = SlackNotifier(
                webhook_url=webhook_url,
                bot_token=bot_token,
                notification_channel=notification_config.get(
                    "notification_channel", "#migration-alerts"
                ),
                enabled=True,
                alert_threshold=notification_config.get("alert_thresholds", {}),
            )
            logger.info("Slack notifications enabled")
        else:
            logger.warning("Notifications enabled but no webhook URL or bot token found")
    
    # Initialize tool
    migration_cfg = config.get("migration", {})
    slack_cfg = config.get("slack", {})
    features_cfg = config.get("features", {})

    tool = SlackMigrationTool(
        user_map=user_map,
        slack_token=os.getenv(slack_cfg.get("bot_token_env", "SLACK_BOT_TOKEN")),
        channel_name=slack_cfg.get("channel_name", "migrated-teams"),
        dry_run=migration_cfg.get("dry_run", True),
        notifier=notifier,
        batch_size=migration_cfg.get("batch_size"),
        max_message_length=migration_cfg.get("max_message_length"),
        team_id=slack_cfg.get("team_id", "T001BRYD"),
        upload_enabled=slack_cfg.get("upload_enabled", False),
        api_rate_limit_per_second=slack_cfg.get("api_rate_limit_per_second", 50),
        deduplication=features_cfg.get("deduplication", True),
        attachment_processing=features_cfg.get("attachment_processing", True),
        output_dir=migration_cfg.get("output_dir", "data/output"),
        attachment_dir=os.path.join(migration_cfg.get("output_dir", "data/output"), "attachments"),
    )
    
    # Process Teams export
    input_file = migration_cfg.get("input_file", "data/input/teams_convo.json")
    try:
        tool.process_export_streaming(input_file)

        tool.export_to_slack_format(migration_cfg.get("output_dir", "data/output"))

        tool.print_migration_report()
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        if notifier:
            notifier.notify_migration_failed(str(e), tool.stats)
        raise
    
    logger.info("Migration completed successfully")


if __name__ == "__main__":
    main()
