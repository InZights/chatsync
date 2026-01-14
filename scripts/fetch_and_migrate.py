#!/usr/bin/env python
"""
Quick script to fetch Teams data and run migration
Combines teams_fetcher + migrate in one workflow
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from teams_to_slack.teams_fetcher import TeamsFetcher, get_access_token_device_flow

# Configuration
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
TENANT_ID = os.getenv('AZURE_TENANT_ID', 'common')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Fetch from Teams and run migration"""
    
    if not CLIENT_ID:
        print("❌ Error: AZURE_CLIENT_ID environment variable not set")
        print("\nSet it with:")
        print('  $env:AZURE_CLIENT_ID = "your-client-id"  (PowerShell)')
        print('  export AZURE_CLIENT_ID="your-client-id"  (Bash)')
        sys.exit(1)
    
    print("\n" + "="*70)
    print("  TEAMS TO SLACK - AUTOMATED FETCH & MIGRATE")
    print("="*70 + "\n")
    
    try:
        # Step 1: Authenticate
        print("📝 Step 1: Authenticating with Microsoft...")
        access_token = get_access_token_device_flow(CLIENT_ID, TENANT_ID)
        
        # Step 2: Fetch Teams data
        print("\n📥 Step 2: Fetching Teams data...")
        fetcher = TeamsFetcher(access_token)
        
        teams = fetcher.get_teams()
        if not teams:
            print("❌ No teams found")
            sys.exit(0)
        
        # Display teams
        print(f"\n✓ Found {len(teams)} teams:")
        print("-" * 70)
        for i, team in enumerate(teams, 1):
            print(f"  {i}. {team['displayName']}")
        
        # Select team
        choice = input(f"\n👉 Select team (1-{len(teams)}): ")
        team_idx = int(choice) - 1
        selected_team = teams[team_idx]
        
        # Get channels
        print(f"\n📂 Fetching channels from '{selected_team['displayName']}'...")
        channels = fetcher.get_channels(selected_team['id'])
        
        if not channels:
            print("❌ No channels found")
            sys.exit(0)
        
        print(f"\n✓ Found {len(channels)} channels:")
        print("-" * 70)
        for i, channel in enumerate(channels, 1):
            print(f"  {i}. {channel['displayName']}")
        
        # Select channel
        channel_choice = input(f"\n👉 Select channel (1-{len(channels)}) or 'all' for all channels: ")
        
        output_file = "data/input/teams_convo.json"
        
        if channel_choice.lower() == 'all':
            # Export all channels to directory
            print(f"\n📦 Exporting all channels...")
            output_dir = "data/input/teams_export"
            results = fetcher.export_team_to_json(
                selected_team['id'],
                output_dir,
                include_replies=True
            )
            
            print("\n✓ Export complete:")
            for channel_name, count in results.items():
                print(f"  • {channel_name}: {count} messages")
            
            total = sum(results.values())
            print(f"\n📊 Total: {total} messages exported to {output_dir}/")
            
        else:
            # Export single channel
            channel_idx = int(channel_choice) - 1
            selected_channel = channels[channel_idx]
            
            print(f"\n📦 Exporting '{selected_channel['displayName']}'...")
            count = fetcher.export_channel_to_json(
                selected_team['id'],
                selected_channel['id'],
                output_file,
                include_replies=True
            )
            
            print(f"\n✓ Exported {count} messages to {output_file}")
        
        # Step 3: Ask to run migration
        print("\n" + "="*70)
        run_migration = input("\n🚀 Run migration to Slack format now? (y/n): ")
        
        if run_migration.lower() == 'y':
            print("\n📤 Step 3: Running migration...")
            os.system("python migrate.py")
        else:
            print("\n✓ Teams data exported. Run migration later with:")
            print("   python migrate.py")
        
        print("\n" + "="*70)
        print("  ✅ WORKFLOW COMPLETE")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
