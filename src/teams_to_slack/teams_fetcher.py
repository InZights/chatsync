"""
Microsoft Teams Data Fetcher
Fetches conversation data from Teams using Microsoft Graph API
"""

import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class TeamsFetcher:
    """Fetch Teams conversations via Microsoft Graph API"""
    
    GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
    GRAPH_API_BETA = "https://graph.microsoft.com/beta"
    
    def __init__(self, access_token: str):
        """
        Initialize Teams fetcher with Microsoft Graph API access token.
        
        Args:
            access_token: Azure AD OAuth2 access token with required permissions:
                - Channel.ReadBasic.All
                - ChannelMessage.Read.All
                - Team.ReadBasic.All
        """
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_teams(self) -> List[Dict]:
        """
        Get all teams the authenticated user is a member of.
        
        Returns:
            List of team objects with id, displayName, description
        """
        url = f"{self.GRAPH_API_ENDPOINT}/me/joinedTeams"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            teams = data.get('value', [])
            logger.info(f"Retrieved {len(teams)} teams")
            return teams
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching teams: {e}")
            raise
    
    def get_channels(self, team_id: str) -> List[Dict]:
        """
        Get all channels in a team.
        
        Args:
            team_id: Teams team ID
            
        Returns:
            List of channel objects
        """
        url = f"{self.GRAPH_API_ENDPOINT}/teams/{team_id}/channels"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            channels = data.get('value', [])
            logger.info(f"Retrieved {len(channels)} channels for team {team_id}")
            return channels
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching channels: {e}")
            raise
    
    def get_channel_messages(
        self, 
        team_id: str, 
        channel_id: str,
        top: int = 50
    ) -> List[Dict]:
        """
        Get messages from a specific channel.
        
        Args:
            team_id: Teams team ID
            channel_id: Channel ID
            top: Number of messages to retrieve (default 50, max 50 per request)
            
        Returns:
            List of message objects
        """
        url = f"{self.GRAPH_API_ENDPOINT}/teams/{team_id}/channels/{channel_id}/messages"
        params = {'$top': top}
        
        all_messages = []
        
        try:
            while url:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                messages = data.get('value', [])
                all_messages.extend(messages)
                
                # Handle pagination
                url = data.get('@odata.nextLink')
                params = {}  # Next link includes params
                
                logger.info(f"Fetched {len(messages)} messages (total: {len(all_messages)})")
            
            return all_messages
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching messages: {e}")
            raise
    
    def get_message_replies(
        self, 
        team_id: str, 
        channel_id: str, 
        message_id: str
    ) -> List[Dict]:
        """
        Get replies to a specific message.
        
        Args:
            team_id: Teams team ID
            channel_id: Channel ID
            message_id: Parent message ID
            
        Returns:
            List of reply objects
        """
        url = f"{self.GRAPH_API_ENDPOINT}/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            replies = data.get('value', [])
            logger.info(f"Retrieved {len(replies)} replies for message {message_id}")
            return replies
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching replies: {e}")
            raise
    
    def export_channel_to_json(
        self,
        team_id: str,
        channel_id: str,
        output_file: str,
        include_replies: bool = True
    ) -> int:
        """
        Export entire channel conversation to JSON file.
        
        Args:
            team_id: Teams team ID
            channel_id: Channel ID
            output_file: Output JSON file path
            include_replies: Whether to fetch replies for each message
            
        Returns:
            Number of messages exported
        """
        logger.info(f"Starting export for channel {channel_id}")
        
        # Get all channel messages
        messages = self.get_channel_messages(team_id, channel_id)
        
        export_data = []
        
        for msg in messages:
            # Transform to our standard format
            message_obj = {
                'id': msg.get('id'),
                'createdDateTime': msg.get('createdDateTime'),
                'from': msg.get('from', {}),
                'body': msg.get('body', {}),
                'importance': msg.get('importance', 'normal'),
                'reactions': msg.get('reactions', []),
                'attachments': msg.get('attachments', []),
                'replies': []
            }
            
            # Fetch replies if requested
            if include_replies and not msg.get('replyToId'):
                try:
                    replies = self.get_message_replies(team_id, channel_id, msg['id'])
                    message_obj['replies'] = [
                        {
                            'id': reply.get('id'),
                            'replyToId': msg.get('id'),
                            'createdDateTime': reply.get('createdDateTime'),
                            'from': reply.get('from', {}),
                            'body': reply.get('body', {}),
                            'attachments': reply.get('attachments', []),
                            'reactions': reply.get('reactions', [])
                        }
                        for reply in replies
                    ]
                except Exception as e:
                    logger.warning(f"Could not fetch replies for message {msg['id']}: {e}")
            
            export_data.append(message_obj)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        total_messages = len(export_data)
        total_replies = sum(len(msg['replies']) for msg in export_data)
        
        logger.info(f"✓ Exported {total_messages} messages with {total_replies} replies to {output_file}")
        
        return total_messages + total_replies
    
    def export_team_to_json(
        self,
        team_id: str,
        output_dir: str,
        include_replies: bool = True
    ) -> Dict[str, int]:
        """
        Export all channels from a team to separate JSON files.
        
        Args:
            team_id: Teams team ID
            output_dir: Output directory for JSON files
            include_replies: Whether to include replies
            
        Returns:
            Dictionary mapping channel names to message counts
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        channels = self.get_channels(team_id)
        results = {}
        
        for channel in channels:
            channel_name = channel.get('displayName', 'unknown')
            channel_id = channel.get('id')
            
            # Sanitize filename
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in channel_name)
            output_file = os.path.join(output_dir, f"{safe_name}.json")
            
            try:
                count = self.export_channel_to_json(
                    team_id, 
                    channel_id, 
                    output_file,
                    include_replies
                )
                results[channel_name] = count
                
            except Exception as e:
                logger.error(f"Failed to export channel {channel_name}: {e}")
                results[channel_name] = 0
        
        return results


def get_access_token_device_flow(
    client_id: str,
    tenant_id: str = "common"
) -> str:
    """
    Get access token using device code flow (for user authentication).
    User will need to visit a URL and enter a code.
    
    Args:
        client_id: Azure AD application client ID
        tenant_id: Azure AD tenant ID (default: "common" for multi-tenant)
        
    Returns:
        Access token string
    """
    # Initiate device code flow
    device_code_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/devicecode"
    
    data = {
        'client_id': client_id,
        'scope': 'https://graph.microsoft.com/.default offline_access'
    }
    
    response = requests.post(device_code_url, data=data)
    response.raise_for_status()
    device_code_data = response.json()
    
    # Display instructions to user
    print("\n" + "="*60)
    print("MICROSOFT AUTHENTICATION REQUIRED")
    print("="*60)
    print(f"\n{device_code_data['message']}\n")
    print(f"URL: {device_code_data['verification_uri']}")
    print(f"Code: {device_code_data['user_code']}")
    print("\nWaiting for authentication...")
    print("="*60 + "\n")
    
    # Poll for token
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    poll_data = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
        'client_id': client_id,
        'device_code': device_code_data['device_code']
    }
    
    import time
    interval = device_code_data.get('interval', 5)
    expires_in = device_code_data.get('expires_in', 900)
    start_time = time.time()
    
    while time.time() - start_time < expires_in:
        time.sleep(interval)
        
        token_response = requests.post(token_url, data=poll_data)
        token_data = token_response.json()
        
        if 'access_token' in token_data:
            print("✓ Authentication successful!\n")
            return token_data['access_token']
        
        if token_data.get('error') not in ['authorization_pending', 'slow_down']:
            raise Exception(f"Authentication failed: {token_data.get('error_description')}")
    
    raise Exception("Authentication timeout")


if __name__ == "__main__":
    """
    Example usage:
    
    1. Register Azure AD app: https://portal.azure.com
    2. Add permissions: Channel.ReadBasic.All, ChannelMessage.Read.All
    3. Get client ID
    4. Run this script with your client ID
    """
    
    import sys
    import os
    
    # Configuration
    CLIENT_ID = os.getenv('AZURE_CLIENT_ID', 'YOUR_CLIENT_ID_HERE')
    TENANT_ID = os.getenv('AZURE_TENANT_ID', 'common')
    
    if CLIENT_ID == 'YOUR_CLIENT_ID_HERE':
        print("Error: Set AZURE_CLIENT_ID environment variable or edit the script")
        sys.exit(1)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Get access token
        access_token = get_access_token_device_flow(CLIENT_ID, TENANT_ID)
        
        # Initialize fetcher
        fetcher = TeamsFetcher(access_token)
        
        # Get teams
        teams = fetcher.get_teams()
        
        if not teams:
            print("No teams found")
            sys.exit(0)
        
        # Display teams
        print("\nAvailable Teams:")
        print("-" * 60)
        for i, team in enumerate(teams, 1):
            print(f"{i}. {team['displayName']} (ID: {team['id']})")
        
        # Select team
        choice = input(f"\nSelect team (1-{len(teams)}): ")
        team_idx = int(choice) - 1
        selected_team = teams[team_idx]
        
        # Export team conversations
        output_dir = "data/input/teams_export"
        print(f"\nExporting {selected_team['displayName']} to {output_dir}...")
        
        results = fetcher.export_team_to_json(
            selected_team['id'],
            output_dir,
            include_replies=True
        )
        
        # Summary
        print("\n" + "="*60)
        print("EXPORT SUMMARY")
        print("="*60)
        for channel_name, count in results.items():
            print(f"  {channel_name}: {count} messages")
        print(f"\nTotal: {sum(results.values())} messages exported")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        sys.exit(1)
