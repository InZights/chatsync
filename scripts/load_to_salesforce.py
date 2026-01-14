#!/usr/bin/env python
"""
Load migrated conversation data to Salesforce Data Cloud
Ingests messages, threads, and user interactions for analytics
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Salesforce Authentication
SALESFORCE_INSTANCE_URL = os.getenv('SALESFORCE_INSTANCE_URL', 'https://login.salesforce.com')
SALESFORCE_CLIENT_ID = os.getenv('SALESFORCE_CLIENT_ID')
SALESFORCE_CLIENT_SECRET = os.getenv('SALESFORCE_CLIENT_SECRET')
SALESFORCE_USERNAME = os.getenv('SALESFORCE_USERNAME')
SALESFORCE_PASSWORD = os.getenv('SALESFORCE_PASSWORD')
SALESFORCE_SECURITY_TOKEN = os.getenv('SALESFORCE_SECURITY_TOKEN', '')

# Data Cloud specific
DATA_CLOUD_INGESTION_API = os.getenv('DATA_CLOUD_INGESTION_API')
DATA_CLOUD_SOURCE_API_NAME = os.getenv('DATA_CLOUD_SOURCE_API_NAME', 'Teams_Conversations')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SalesforceDataCloudLoader:
    """Load conversation data into Salesforce Data Cloud"""
    
    def __init__(
        self,
        instance_url: str,
        access_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        ingestion_api_url: Optional[str] = None,
        source_api_name: str = 'Teams_Conversations'
    ):
        """
        Initialize Salesforce Data Cloud loader.
        
        Args:
            instance_url: Salesforce instance URL
            access_token: Pre-existing access token (if available)
            client_id: Connected App Client ID
            client_secret: Connected App Client Secret
            username: Salesforce username
            password: Salesforce password (+ security token)
            ingestion_api_url: Data Cloud Ingestion API endpoint
            source_api_name: Data Cloud source API name
        """
        self.instance_url = instance_url.rstrip('/')
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.ingestion_api_url = ingestion_api_url
        self.source_api_name = source_api_name
        
        self.stats = {
            'messages_processed': 0,
            'messages_uploaded': 0,
            'threads_processed': 0,
            'users_identified': 0,
            'files_processed': 0,
            'errors': 0
        }
        
        if not self.access_token:
            self.authenticate()
    
    def authenticate(self) -> str:
        """Authenticate with Salesforce using OAuth 2.0 password flow"""
        
        if not all([self.client_id, self.client_secret, self.username, self.password]):
            raise ValueError(
                "Missing Salesforce credentials. Provide: "
                "CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD"
            )
        
        logger.info("Authenticating with Salesforce...")
        
        auth_url = f"{self.instance_url}/services/oauth2/token"
        payload = {
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': self.username,
            'password': self.password
        }
        
        try:
            response = requests.post(auth_url, data=payload)
            response.raise_for_status()
            auth_data = response.json()
            
            self.access_token = auth_data['access_token']
            self.instance_url = auth_data['instance_url']
            
            logger.info(f"✓ Authenticated successfully: {self.instance_url}")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def transform_message_for_data_cloud(self, message: Dict, date_key: str) -> Dict:
        """
        Transform Slack-formatted message to Data Cloud schema.
        
        Data Cloud expects:
        - Flat structure (no deep nesting)
        - Consistent field names
        - ISO timestamps
        - String IDs
        """
        ts = message.get('ts', '')
        
        # Convert Slack epoch timestamp back to ISO
        try:
            ts_float = float(ts)
            dt = datetime.fromtimestamp(ts_float)
            iso_timestamp = dt.isoformat()
        except (ValueError, TypeError):
            iso_timestamp = datetime.now().isoformat()
        
        transformed = {
            # Primary identifiers
            'message_id': f"{message.get('user', 'unknown')}_{ts}",
            'timestamp': iso_timestamp,
            'date_key': date_key,
            'epoch_ts': ts,
            
            # Message content
            'text': message.get('text', '')[:4000],  # Truncate if needed
            'message_type': message.get('type', 'message'),
            'subtype': message.get('subtype', 'standard'),
            
            # User info
            'user_id': message.get('user', 'unknown'),
            'user_name': message.get('user_profile', {}).get('real_name', ''),
            'user_team': message.get('team', ''),
            
            # Thread info
            'is_threaded': 'thread_ts' in message,
            'thread_ts': message.get('thread_ts', ''),
            'parent_ts': message.get('thread_ts', '') if 'thread_ts' in message and message.get('thread_ts') != ts else '',
            
            # Metadata
            'channel': message.get('channel', 'migrated-teams'),
            'source_system': message.get('metadata', {}).get('source', 'teams'),
            'migrated_at': message.get('metadata', {}).get('migrated_at', ''),
            
            # Engagement metrics
            'has_attachments': len(message.get('files', [])) > 0,
            'attachment_count': len(message.get('files', [])),
            'reactions_count': len(message.get('reactions', [])),
            
            # Original data (as JSON string for reference)
            'original_payload': json.dumps(message)[:5000]  # Truncate
        }
        
        return transformed
    
    def load_via_bulk_api(self, records: List[Dict], object_name: str = 'Conversation_Message__c') -> Dict:
        """
        Load data via Salesforce Bulk API 2.0
        
        Args:
            records: List of records to insert
            object_name: Salesforce object API name
            
        Returns:
            Job status and results
        """
        logger.info(f"Creating Bulk API job for {len(records)} records...")
        
        # Step 1: Create bulk job
        job_url = f"{self.instance_url}/services/data/v59.0/jobs/ingest"
        job_payload = {
            'object': object_name,
            'operation': 'insert',
            'contentType': 'JSON',
            'lineEnding': 'LF'
        }
        
        try:
            response = requests.post(job_url, json=job_payload, headers=self.get_headers())
            response.raise_for_status()
            job_data = response.json()
            job_id = job_data['id']
            
            logger.info(f"✓ Job created: {job_id}")
            
            # Step 2: Upload data
            upload_url = f"{self.instance_url}/services/data/v59.0/jobs/ingest/{job_id}/batches"
            
            # Convert records to newline-delimited JSON
            ndjson_data = '\n'.join([json.dumps(record) for record in records])
            
            headers = self.get_headers()
            headers['Content-Type'] = 'application/json'
            
            response = requests.put(upload_url, data=ndjson_data, headers=headers)
            response.raise_for_status()
            
            logger.info(f"✓ Data uploaded to job {job_id}")
            
            # Step 3: Close job (triggers processing)
            close_url = f"{self.instance_url}/services/data/v59.0/jobs/ingest/{job_id}"
            close_payload = {'state': 'UploadComplete'}
            
            response = requests.patch(close_url, json=close_payload, headers=self.get_headers())
            response.raise_for_status()
            
            logger.info(f"✓ Job closed and processing...")
            
            return {
                'job_id': job_id,
                'status': 'processing',
                'records_submitted': len(records)
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Bulk API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            self.stats['errors'] += 1
            raise
    
    def load_via_data_cloud_ingestion_api(self, records: List[Dict]) -> Dict:
        """
        Load data via Data Cloud Ingestion API (streaming)
        
        Args:
            records: List of records to ingest
            
        Returns:
            Ingestion status
        """
        if not self.ingestion_api_url:
            raise ValueError("Data Cloud Ingestion API URL not configured")
        
        logger.info(f"Ingesting {len(records)} records to Data Cloud...")
        
        url = f"{self.ingestion_api_url}/data/{self.source_api_name}"
        
        payload = {
            'data': records
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.get_headers())
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"✓ Ingested {len(records)} records")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Data Cloud Ingestion API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            self.stats['errors'] += 1
            raise
    
    def load_from_output_directory(
        self,
        output_dir: str = 'data/output',
        batch_size: int = 1000,
        use_bulk_api: bool = True
    ) -> None:
        """
        Load all output JSON files to Salesforce Data Cloud.
        
        Args:
            output_dir: Directory containing output JSON files
            batch_size: Number of records per batch
            use_bulk_api: Use Bulk API (True) or Ingestion API (False)
        """
        output_path = Path(output_dir)
        
        if not output_path.exists():
            raise FileNotFoundError(f"Output directory not found: {output_dir}")
        
        # Find all JSON files (date-organized)
        json_files = sorted(output_path.glob('*.json'))
        
        if not json_files:
            logger.warning(f"No JSON files found in {output_dir}")
            return
        
        logger.info(f"Found {len(json_files)} output files to process")
        
        all_records = []
        user_set = set()
        thread_set = set()
        
        # Process each date file
        for json_file in json_files:
            date_key = json_file.stem  # e.g., '2026-01-08'
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                
                logger.info(f"Processing {json_file.name}: {len(messages)} messages")
                
                for message in messages:
                    # Transform to Data Cloud format
                    transformed = self.transform_message_for_data_cloud(message, date_key)
                    all_records.append(transformed)
                    
                    # Track stats
                    self.stats['messages_processed'] += 1
                    
                    if message.get('user'):
                        user_set.add(message['user'])
                    
                    if message.get('thread_ts'):
                        thread_set.add(message['thread_ts'])
                        self.stats['threads_processed'] += 1
                    
                    if message.get('files'):
                        self.stats['files_processed'] += len(message['files'])
                
            except Exception as e:
                logger.error(f"Error processing {json_file.name}: {e}")
                self.stats['errors'] += 1
                continue
        
        self.stats['users_identified'] = len(user_set)
        
        logger.info(f"\nProcessed totals:")
        logger.info(f"  Messages: {self.stats['messages_processed']}")
        logger.info(f"  Unique users: {self.stats['users_identified']}")
        logger.info(f"  Threads: {self.stats['threads_processed']}")
        logger.info(f"  Files: {self.stats['files_processed']}")
        
        # Upload in batches
        if not all_records:
            logger.warning("No records to upload")
            return
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Uploading {len(all_records)} records to Salesforce Data Cloud")
        logger.info(f"{'='*60}\n")
        
        for i in range(0, len(all_records), batch_size):
            batch = all_records[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(all_records) + batch_size - 1) // batch_size
            
            logger.info(f"Uploading batch {batch_num}/{total_batches} ({len(batch)} records)...")
            
            try:
                if use_bulk_api:
                    result = self.load_via_bulk_api(batch)
                    logger.info(f"  Job ID: {result['job_id']}")
                else:
                    result = self.load_via_data_cloud_ingestion_api(batch)
                
                self.stats['messages_uploaded'] += len(batch)
                
            except Exception as e:
                logger.error(f"Failed to upload batch {batch_num}: {e}")
                continue
    
    def print_summary(self) -> None:
        """Print upload summary"""
        print("\n" + "="*60)
        print("  SALESFORCE DATA CLOUD UPLOAD SUMMARY")
        print("="*60)
        print(f"\n✓ Messages processed:    {self.stats['messages_processed']:,}")
        print(f"✓ Messages uploaded:     {self.stats['messages_uploaded']:,}")
        print(f"✓ Unique users:          {self.stats['users_identified']:,}")
        print(f"✓ Threads:               {self.stats['threads_processed']:,}")
        print(f"✓ Files referenced:      {self.stats['files_processed']:,}")
        
        if self.stats['errors'] > 0:
            print(f"\n⚠️  Errors encountered:    {self.stats['errors']:,}")
        
        print("\n" + "="*60 + "\n")


def main():
    """Main entry point"""
    
    print("\n" + "="*70)
    print("  SALESFORCE DATA CLOUD LOADER")
    print("="*70 + "\n")
    
    # Check for required credentials
    if not SALESFORCE_CLIENT_ID:
        print("❌ Error: SALESFORCE_CLIENT_ID not set")
        print("\nSet Salesforce credentials in .env file:")
        print("  SALESFORCE_INSTANCE_URL=https://login.salesforce.com")
        print("  SALESFORCE_CLIENT_ID=your_client_id")
        print("  SALESFORCE_CLIENT_SECRET=your_client_secret")
        print("  SALESFORCE_USERNAME=your_username@example.com")
        print("  SALESFORCE_PASSWORD=your_password+security_token")
        print("\nOptional (for Data Cloud Ingestion API):")
        print("  DATA_CLOUD_INGESTION_API=https://your-instance.my.salesforce.com")
        print("  DATA_CLOUD_SOURCE_API_NAME=Teams_Conversations")
        sys.exit(1)
    
    try:
        # Initialize loader
        loader = SalesforceDataCloudLoader(
            instance_url=SALESFORCE_INSTANCE_URL,
            client_id=SALESFORCE_CLIENT_ID,
            client_secret=SALESFORCE_CLIENT_SECRET,
            username=SALESFORCE_USERNAME,
            password=SALESFORCE_PASSWORD + SALESFORCE_SECURITY_TOKEN,
            ingestion_api_url=DATA_CLOUD_INGESTION_API,
            source_api_name=DATA_CLOUD_SOURCE_API_NAME
        )
        
        # Ask which API to use
        print("\nSelect upload method:")
        print("  1. Bulk API 2.0 (recommended for large datasets)")
        print("  2. Data Cloud Ingestion API (streaming)")
        
        choice = input("\nChoice (1 or 2, default=1): ").strip() or "1"
        use_bulk = choice == "1"
        
        # Load data
        output_dir = input("\nOutput directory (default='data/output'): ").strip() or "data/output"
        batch_size = input("Batch size (default=1000): ").strip() or "1000"
        
        loader.load_from_output_directory(
            output_dir=output_dir,
            batch_size=int(batch_size),
            use_bulk_api=use_bulk
        )
        
        # Print summary
        loader.print_summary()
        
        print("✅ Upload complete!")
        
        if use_bulk:
            print("\n💡 Check job status in Salesforce Setup > Bulk Data Load Jobs")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Upload cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
