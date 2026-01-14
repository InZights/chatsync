"""Unit tests for migration module"""

import unittest
import json
from datetime import datetime
from src.teams_to_slack.migration import SlackMigrationTool


class TestSlackMigrationTool(unittest.TestCase):
    """Test cases for SlackMigrationTool"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user_map = {"T-USER-99": "U01ABC", "T-USER-44": "U02XYZ"}
        self.tool = SlackMigrationTool(user_map=self.user_map)
    
    def test_timestamp_conversion(self):
        """Test ISO to Slack timestamp conversion"""
        iso_ts = "2026-01-08T14:00:00Z"
        slack_ts = self.tool.to_slack_ts(iso_ts)
        
        # Should be numeric string with 6 decimals
        self.assertIsInstance(slack_ts, str)
        self.assertIn('.', slack_ts)
        parts = slack_ts.split('.')
        self.assertEqual(len(parts[1]), 6)
    
    def test_text_sanitization(self):
        """Test HTML to Markdown conversion"""
        html_text = "<div>This is <b>bold</b> and <i>italic</i> text</div>"
        clean_text = self.tool.sanitize_text(html_text)
        
        self.assertIn("*bold*", clean_text)
        self.assertIn("_italic_", clean_text)
        self.assertNotIn("<div>", clean_text)
        self.assertNotIn("</div>", clean_text)
    
    def test_user_mapping(self):
        """Test user ID mapping"""
        msg = {
            "id": "MSG_001",
            "createdDateTime": "2026-01-08T14:00:00Z",
            "from": {"user": {"id": "T-USER-99"}},
            "body": {"content": "Test message"}
        }
        
        result = self.tool.transform_message(msg)
        self.assertEqual(result['user'], "U01ABC")
    
    def test_message_deduplication(self):
        """Test duplicate detection"""
        msg = {
            "id": "MSG_001",
            "createdDateTime": "2026-01-08T14:00:00Z",
            "from": {"user": {"id": "T-USER-99"}},
            "body": {"content": "Test message"}
        }
        
        # First transform should succeed
        result1 = self.tool.transform_message(msg)
        self.assertIsNotNone(result1)
        
        # Second transform of same message should be skipped
        result2 = self.tool.transform_message(msg)
        self.assertIsNone(result2)
        self.assertEqual(self.tool.stats['skipped_duplicates'], 1)
    
    def test_thread_preservation(self):
        """Test thread linking"""
        msg = {
            "id": "MSG_002",
            "createdDateTime": "2026-01-08T14:05:00Z",
            "from": {"user": {"id": "T-USER-44"}},
            "body": {"content": "Reply message"}
        }
        
        parent_ts = "1767880800.000000"
        parent_user = "U01ABC"
        
        result = self.tool.transform_message(msg, parent_ts=parent_ts, parent_user_id=parent_user)
        
        self.assertEqual(result['thread_ts'], parent_ts)
        self.assertEqual(result['parent_user_id'], parent_user)


if __name__ == '__main__':
    unittest.main()
