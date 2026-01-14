#!/usr/bin/env python
"""
Test script for Slack notifications
Run this to verify your notification setup is working
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from teams_to_slack.slack_notifier import SlackNotifier, AlertLevel


def main():
    """Test notification system"""
    print("\n" + "="*60)
    print("  SLACK NOTIFICATION TEST")
    print("="*60 + "\n")
    
    # Check for webhook URL or bot token
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    bot_token = os.getenv('SLACK_BOT_TOKEN')
    
    if not webhook_url and not bot_token:
        print("❌ Error: No Slack credentials found!")
        print("\nPlease set one of the following environment variables:")
        print("  • SLACK_WEBHOOK_URL (recommended)")
        print("  • SLACK_BOT_TOKEN")
        print("\nExample:")
        print('  $env:SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/..."')
        return 1
    
    print(f"✓ Webhook URL: {'✓ Found' if webhook_url else '✗ Not set'}")
    print(f"✓ Bot Token: {'✓ Found' if bot_token else '✗ Not set'}")
    print()
    
    # Initialize notifier
    notifier = SlackNotifier(
        webhook_url=webhook_url,
        bot_token=bot_token,
        notification_channel='#migration-alerts',
        enabled=True
    )
    
    # Send test notifications
    tests = [
        {
            'title': 'Test: Info Level',
            'message': '🧪 This is an **INFO** level notification',
            'level': AlertLevel.INFO
        },
        {
            'title': 'Test: Warning Level',
            'message': '⚠️ This is a **WARNING** level notification',
            'level': AlertLevel.WARNING
        },
        {
            'title': 'Test: Error Level',
            'message': '❌ This is an **ERROR** level notification',
            'level': AlertLevel.ERROR,
            'fields': [
                {'title': 'Error Count', 'value': '5'},
                {'title': 'Error Rate', 'value': '2.3%'}
            ]
        }
    ]
    
    print("Sending test notifications...\n")
    
    success_count = 0
    for i, test in enumerate(tests, 1):
        print(f"[{i}/{len(tests)}] Sending: {test['title']}")
        
        success = notifier.send_notification(
            title=test['title'],
            message=test['message'],
            level=test['level'],
            fields=test.get('fields')
        )
        
        if success:
            print(f"     ✅ Sent successfully\n")
            success_count += 1
        else:
            print(f"     ❌ Failed to send\n")
    
    # Send migration simulation
    print("\nSending migration simulation notifications...\n")
    
    # Start notification
    print("[4/5] Simulating migration start...")
    notifier.notify_migration_start('data/input/teams_convo.json', 1245)
    success_count += 1
    
    # Complete notification
    print("[5/5] Simulating migration completion...")
    mock_stats = {
        'total_messages': 1245,
        'successful_transforms': 1240,
        'failed_transforms': 5,
        'skipped_duplicates': 0,
        'attachments_downloaded': 23,
        'api_uploads': 1240,
        'api_failures': 0
    }
    notifier.notify_migration_complete(mock_stats, 3.5)
    success_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    print(f"Notifications sent: {success_count}/{len(tests) + 2}")
    
    if success_count == len(tests) + 2:
        print("\n✅ All tests passed! Check your Slack channel for messages.\n")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check logs/migration.log for details.\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
