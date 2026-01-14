# API Reference

## SlackMigrationTool

Main class for Teams to Slack migration.

### Constructor

```python
SlackMigrationTool(
    user_map: Dict[str, str],
    slack_token: Optional[str] = None,
    channel_name: str = "migrated-teams",
    dry_run: bool = False
)
```

### Methods

#### `process_export_streaming(file_path: str)`
Process Teams export file with streaming to prevent memory overflow.

#### `export_to_slack_format(output_dir: str = "data/output")`
Export messages to Slack JSON format organized by date.

#### `transform_message(msg: Dict) -> Optional[Dict]`
Transform single Teams message to Slack format.

#### `print_migration_report()`
Print migration statistics and summary.

### Example

```python
from src.teams_to_slack import SlackMigrationTool

user_map = {
    "T-USER-99": "U01ABC",
    "T-USER-44": "U02XYZ"
}

tool = SlackMigrationTool(user_map=user_map)
tool.process_export_streaming('data/input/teams.json')
tool.export_to_slack_format()
tool.print_migration_report()
```
