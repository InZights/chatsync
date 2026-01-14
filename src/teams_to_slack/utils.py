"""Utility functions for Teams to Slack migration"""

import json
from pathlib import Path
from typing import Dict


def load_config(config_path: str) -> Dict:
    """Load configuration from JSON file."""
    with open(config_path, 'r') as f:
        return json.load(f)


def load_user_mapping(csv_path: str = None, json_path: str = None) -> Dict[str, str]:
    """Load user mapping from CSV or JSON."""
    user_map = {}
    
    if json_path:
        with open(json_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict):
                user_map.update(data)
    
    if csv_path:
        import csv
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_map[row['teams_id']] = row['slack_id']
    
    return user_map


def create_output_dirs(base_path: str = "data/output") -> None:
    """Create necessary output directories."""
    Path(base_path).mkdir(parents=True, exist_ok=True)
    Path(f"{base_path}/attachments").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)
