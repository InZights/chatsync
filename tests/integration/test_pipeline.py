"""Integration tests for the migration pipeline"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from src.teams_to_slack.migration import SlackMigrationTool


class TestMigrationIntegration(unittest.TestCase):
    """Integration tests for full migration pipeline"""
    
    def setUp(self):
        """Set up test environment"""
        self.user_map = {"T-USER-99": "U01ABC", "T-USER-44": "U02XYZ"}
        self.tool = SlackMigrationTool(user_map=self.user_map)
        self.temp_dir = tempfile.mkdtemp()
    
    def test_full_migration_pipeline(self):
        """Test complete migration workflow"""
        # Create sample Teams data
        teams_data = [
            {
                "id": "MSG_001",
                "createdDateTime": "2026-01-08T14:00:00Z",
                "from": {"user": {"id": "T-USER-99"}},
                "body": {"content": "<div>Test <b>message</b></div>"},
                "replies": [
                    {
                        "id": "MSG_001_R1",
                        "createdDateTime": "2026-01-08T14:05:00Z",
                        "from": {"user": {"id": "T-USER-44"}},
                        "body": {"content": "<div>Reply with <i>emphasis</i></div>"}
                    }
                ]
            }
        ]
        
        # Write test data
        test_file = os.path.join(self.temp_dir, 'test_teams.json')
        with open(test_file, 'w') as f:
            json.dump(teams_data, f)
        
        # Process
        self.tool.process_export_streaming(test_file)
        
        # Verify
        self.assertEqual(self.tool.stats['total_messages'], 2)
        self.assertEqual(self.tool.stats['successful_transforms'], 2)

    def test_export_writes_date_partitioned_file(self):
        """Ensure export_to_slack_format creates Slack import files."""
        teams_data = [
            {
                "id": "MSG_010",
                "createdDateTime": "2026-01-08T14:00:00Z",
                "from": {"user": {"id": "T-USER-99"}},
                "body": {"content": "<div>Parent</div>"},
                "replies": [],
            }
        ]

        test_file = os.path.join(self.temp_dir, "test_export.json")
        with open(test_file, "w") as handle:
            json.dump(teams_data, handle)

        self.tool.process_export_streaming(test_file, output_dir=self.temp_dir)
        self.tool.export_to_slack_format(self.temp_dir)

        expected_file = Path(self.temp_dir) / "2026-01-08.json"
        self.assertTrue(expected_file.exists())

        with open(expected_file, "r") as handle:
            payload = json.load(handle)
        self.assertEqual(len(payload), 1)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)


if __name__ == '__main__':
    unittest.main()
