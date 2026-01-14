"""
Slack Notification System
Sends alerts for migration errors, anomalies, and status updates
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SlackNotifier:
    """Send Slack notifications for migration monitoring and alerts"""
    
    def __init__(
        self, 
        webhook_url: Optional[str] = None,
        bot_token: Optional[str] = None,
        notification_channel: Optional[str] = None,
        enabled: bool = True,
        alert_threshold: Dict[str, float] = None
    ):
        """
        Initialize Slack notifier.
        
        Args:
            webhook_url: Slack webhook URL for incoming webhooks
            bot_token: Slack bot token for API-based notifications
            notification_channel: Channel ID or name for notifications
            enabled: Enable/disable notifications
            alert_threshold: Thresholds for triggering alerts
                {
                    'error_rate': 0.05,  # 5% error rate
                    'duplicate_rate': 0.30,  # 30% duplicates
                    'processing_time_minutes': 60  # 1 hour
                }
        """
        self.webhook_url = webhook_url
        self.bot_token = bot_token
        self.notification_channel = notification_channel or "#migration-alerts"
        self.enabled = enabled
        
        # Default alert thresholds
        self.alert_threshold = alert_threshold or {
            'error_rate': 0.05,  # Alert if >5% messages fail
            'duplicate_rate': 0.30,  # Alert if >30% are duplicates
            'processing_time_minutes': 60,  # Alert if processing >60 min
            'critical_error_count': 10  # Alert after 10 critical errors
        }
        
        self.start_time = datetime.now()
        self.alerts_sent = []
    
    def _format_message(
        self, 
        title: str, 
        message: str, 
        level: AlertLevel,
        fields: Optional[List[Dict]] = None,
        include_timestamp: bool = True
    ) -> Dict:
        """
        Format Slack message with blocks and attachments.
        
        Args:
            title: Alert title
            message: Alert message body
            level: Alert severity level
            fields: Additional fields to display
            include_timestamp: Include timestamp in footer
            
        Returns:
            Formatted Slack message payload
        """
        # Color coding by severity
        color_map = {
            AlertLevel.INFO: "#36a64f",      # Green
            AlertLevel.WARNING: "#ff9800",   # Orange
            AlertLevel.ERROR: "#f44336",     # Red
            AlertLevel.CRITICAL: "#9c27b0"   # Purple
        }
        
        # Emoji icons
        icon_map = {
            AlertLevel.INFO: "✅",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🚨"
        }
        
        color = color_map.get(level, "#808080")
        icon = icon_map.get(level, "ℹ️")
        
        # Build message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{icon} {title}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ]
        
        # Add fields if provided
        if fields:
            field_items = []
            for field in fields:
                field_items.append({
                    "type": "mrkdwn",
                    "text": f"*{field['title']}*\n{field['value']}"
                })
            
            blocks.append({
                "type": "section",
                "fields": field_items
            })
        
        # Add context footer
        if include_timestamp:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Migration Pipeline"
                    }
                ]
            })
        
        return {
            "blocks": blocks,
            "attachments": [
                {
                    "color": color,
                    "fallback": f"{title}: {message}"
                }
            ]
        }
    
    def _send_webhook(self, payload: Dict) -> bool:
        """Send notification via incoming webhook"""
        if not self.webhook_url:
            logger.debug("Webhook URL not configured, skipping webhook notification")
            return False
        
        try:
            import requests
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            logger.info("Webhook notification sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False
    
    def _send_via_api(self, payload: Dict) -> bool:
        """Send notification via Slack API"""
        if not self.bot_token:
            logger.debug("Bot token not configured, skipping API notification")
            return False
        
        try:
            from slack_sdk import WebClient
            from slack_sdk.errors import SlackApiError
            
            client = WebClient(token=self.bot_token)
            
            response = client.chat_postMessage(
                channel=self.notification_channel,
                blocks=payload.get('blocks'),
                attachments=payload.get('attachments'),
                text=payload.get('attachments', [{}])[0].get('fallback', 'Migration Alert')
            )
            
            logger.info(f"API notification sent to {self.notification_channel}")
            return True
            
        except ImportError:
            logger.warning("slack-sdk not installed. Install with: pip install slack-sdk")
            return False
        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            return False
        except Exception as e:
            logger.error(f"Failed to send API notification: {e}")
            return False
    
    def send_notification(
        self, 
        title: str, 
        message: str, 
        level: AlertLevel = AlertLevel.INFO,
        fields: Optional[List[Dict]] = None
    ) -> bool:
        """
        Send notification to Slack.
        
        Args:
            title: Notification title
            message: Notification message
            level: Alert severity level
            fields: Additional fields [{'title': '...', 'value': '...'}]
            
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            logger.debug("Notifications disabled, skipping")
            return False
        
        payload = self._format_message(title, message, level, fields)
        
        # Try webhook first, fallback to API
        success = self._send_webhook(payload)
        if not success:
            success = self._send_via_api(payload)
        
        if success:
            self.alerts_sent.append({
                'timestamp': datetime.now().isoformat(),
                'level': level.value,
                'title': title
            })
        
        return success
    
    def check_anomalies(self, stats: Dict) -> None:
        """
        Analyze migration stats and send alerts for anomalies.
        
        Args:
            stats: Migration statistics dictionary
        """
        if not self.enabled:
            return
        
        alerts = []
        
        # Check error rate
        total = stats.get('total_messages', 0)
        failed = stats.get('failed_transforms', 0)
        if total > 0:
            error_rate = failed / total
            if error_rate > self.alert_threshold['error_rate']:
                alerts.append({
                    'level': AlertLevel.ERROR,
                    'title': 'High Error Rate Detected',
                    'message': f"⚠️ Error rate is *{error_rate:.1%}* (threshold: {self.alert_threshold['error_rate']:.1%})",
                    'fields': [
                        {'title': 'Failed Messages', 'value': f"{failed:,}"},
                        {'title': 'Total Processed', 'value': f"{total:,}"},
                        {'title': 'Error Rate', 'value': f"{error_rate:.2%}"}
                    ]
                })
        
        # Check duplicate rate
        duplicates = stats.get('skipped_duplicates', 0)
        if total > 0:
            dup_rate = duplicates / total
            if dup_rate > self.alert_threshold['duplicate_rate']:
                alerts.append({
                    'level': AlertLevel.WARNING,
                    'title': 'High Duplicate Rate',
                    'message': f"⚠️ Duplicate rate is *{dup_rate:.1%}* - possible data quality issue",
                    'fields': [
                        {'title': 'Duplicates', 'value': f"{duplicates:,}"},
                        {'title': 'Duplicate Rate', 'value': f"{dup_rate:.2%}"}
                    ]
                })
        
        # Check API failures
        api_uploads = stats.get('api_uploads', 0)
        api_failures = stats.get('api_failures', 0)
        if api_uploads > 0 and api_failures > 0:
            failure_rate = api_failures / (api_uploads + api_failures)
            if failure_rate > 0.1:  # >10% API failure rate
                alerts.append({
                    'level': AlertLevel.ERROR,
                    'title': 'Slack API Upload Failures',
                    'message': f"❌ *{api_failures:,}* messages failed to upload to Slack",
                    'fields': [
                        {'title': 'Failed', 'value': f"{api_failures:,}"},
                        {'title': 'Success', 'value': f"{api_uploads:,}"},
                        {'title': 'Failure Rate', 'value': f"{failure_rate:.2%}"}
                    ]
                })
        
        # Send all detected alerts
        for alert in alerts:
            self.send_notification(
                title=alert['title'],
                message=alert['message'],
                level=alert['level'],
                fields=alert.get('fields')
            )
    
    def notify_migration_start(self, input_file: str, total_messages: int) -> None:
        """Send notification when migration starts"""
        self.send_notification(
            title="Migration Started",
            message=f"🚀 Teams to Slack migration has begun",
            level=AlertLevel.INFO,
            fields=[
                {'title': 'Input File', 'value': f"`{input_file}`"},
                {'title': 'Total Messages', 'value': f"{total_messages:,}"}
            ]
        )
    
    def notify_migration_complete(self, stats: Dict, duration_minutes: float) -> None:
        """Send notification when migration completes successfully"""
        total = stats.get('total_messages', 0)
        success = stats.get('successful_transforms', 0)
        failed = stats.get('failed_transforms', 0)
        uploaded = stats.get('api_uploads', 0)
        
        fields = [
            {'title': 'Total Processed', 'value': f"{total:,}"},
            {'title': 'Successful', 'value': f"{success:,}"},
            {'title': 'Failed', 'value': f"{failed:,}"},
            {'title': 'Duration', 'value': f"{duration_minutes:.1f} minutes"}
        ]
        
        if uploaded > 0:
            fields.append({'title': 'Uploaded to Slack', 'value': f"{uploaded:,}"})
        
        self.send_notification(
            title="Migration Complete ✅",
            message=f"🎉 Migration finished successfully! Processed *{total:,}* messages in *{duration_minutes:.1f}* minutes.",
            level=AlertLevel.INFO,
            fields=fields
        )
    
    def notify_migration_failed(self, error: str, stats: Dict) -> None:
        """Send critical notification when migration fails"""
        self.send_notification(
            title="Migration Failed ❌",
            message=f"🚨 *CRITICAL*: Migration process has failed!\n\n```{error}```",
            level=AlertLevel.CRITICAL,
            fields=[
                {'title': 'Processed Before Failure', 'value': f"{stats.get('total_messages', 0):,}"},
                {'title': 'Error Count', 'value': f"{len(stats.get('error_log', [])):,}"}
            ]
        )
    
    def notify_error_threshold(self, error_count: int, error_samples: List[str]) -> None:
        """Send alert when error threshold is exceeded"""
        sample_text = "\n".join([f"• {err[:100]}" for err in error_samples[:3]])
        
        self.send_notification(
            title="Error Threshold Exceeded",
            message=f"🚨 Migration has encountered *{error_count}* errors!\n\n*Recent errors:*\n{sample_text}",
            level=AlertLevel.ERROR,
            fields=[
                {'title': 'Total Errors', 'value': f"{error_count:,}"},
                {'title': 'Threshold', 'value': f"{self.alert_threshold['critical_error_count']:,}"}
            ]
        )
    
    def get_summary(self) -> Dict:
        """Get summary of notifications sent"""
        return {
            'enabled': self.enabled,
            'alerts_sent': len(self.alerts_sent),
            'webhook_configured': bool(self.webhook_url),
            'bot_token_configured': bool(self.bot_token),
            'recent_alerts': self.alerts_sent[-5:] if self.alerts_sent else []
        }
