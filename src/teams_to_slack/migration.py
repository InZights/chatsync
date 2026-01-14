"""Teams to Slack Migration - Core Migration Logic."""

import json
import logging
import hashlib
import os
import time
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional, Iterable, Tuple

import requests

logger = logging.getLogger(__name__)

# Import notification system
try:
    from .slack_notifier import SlackNotifier, AlertLevel
except ImportError:
    SlackNotifier = None
    AlertLevel = None
    logger.warning("SlackNotifier not available - notifications disabled")


class SlackExportWriter:
    """Streaming writer that keeps Slack import files append-only."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.handles: Dict[str, Tuple[object, bool]] = {}
        os.makedirs(output_dir, exist_ok=True)

    def _ensure_handle(self, date_key: str) -> Tuple[object, bool]:
        if date_key in self.handles:
            return self.handles[date_key]
        file_path = os.path.join(self.output_dir, f"{date_key}.json")
        handle = open(file_path, "w", encoding="utf-8")
        # Bool tracks whether we have written at least one element
        self.handles[date_key] = (handle, False)
        return handle, False

    def write_batch(self, date_key: str, messages: List[Dict]) -> None:
        if not messages:
            return
        handle, has_written = self._ensure_handle(date_key)
        for msg in messages:
            if not has_written:
                handle.write("[\n")
                json.dump(msg, handle, ensure_ascii=False)
                has_written = True
            else:
                handle.write(",\n")
                json.dump(msg, handle, ensure_ascii=False)
        self.handles[date_key] = (handle, has_written)

    def finalize(self) -> None:
        for date_key, (handle, has_written) in self.handles.items():
            if not has_written:
                handle.write("[]")
            else:
                handle.write("\n]\n")
            handle.close()
        self.handles.clear()


class SlackMigrationTool:
    """Production-grade Teams to Slack migration tool with error handling and scalability."""

    BATCH_SIZE = 1000
    MAX_MESSAGE_LENGTH = 4000
    CHUNK_SIZE = 10 * 1024 * 1024

    def __init__(
        self,
        user_map: Dict[str, str],
        slack_token: Optional[str] = None,
        channel_name: str = "migrated-teams",
        dry_run: bool = False,
        notifier: Optional["SlackNotifier"] = None,
        batch_size: Optional[int] = None,
        max_message_length: Optional[int] = None,
        team_id: str = "T001BRYD",
        upload_enabled: bool = False,
        api_rate_limit_per_second: int = 50,
        deduplication: bool = True,
        attachment_processing: bool = True,
        output_dir: str = "data/output",
        attachment_dir: str = "data/output/attachments",
    ):
        """Initialize migration tool."""

        self.user_map = user_map
        self.slack_token = slack_token
        self.channel_name = channel_name
        self.slack_team_id = team_id
        self.dry_run = dry_run
        self.notifier = notifier
        self.migration_start_time = datetime.now()

        self.batch_size = batch_size or self.BATCH_SIZE
        self.max_message_length = max_message_length or self.MAX_MESSAGE_LENGTH
        self.upload_enabled = upload_enabled and bool(slack_token)
        self.api_rate_limit_per_second = api_rate_limit_per_second
        self.deduplication = deduplication
        self.attachment_processing = attachment_processing
        self.output_dir = output_dir
        self.attachment_dir = attachment_dir
        self.max_attachment_bytes = 20 * 1024 * 1024

        self.export_writer: Optional[SlackExportWriter] = None
        self.buffered_message_count = 0
        self.messages_by_date = defaultdict(list)
        self.message_hashes = set()
        self.error_log: List[str] = []
        self.thread_ts_map: Dict[str, str] = {}
        self.stats = {
            "total_messages": 0,
            "successful_transforms": 0,
            "skipped_duplicates": 0,
            "failed_transforms": 0,
            "attachments_downloaded": 0,
            "api_uploads": 0,
            "api_failures": 0,
        }

        self._slack_client = None
        self._channel_id: Optional[str] = None
        self._last_api_call = 0.0

        os.makedirs(os.path.dirname("logs/migration.log"), exist_ok=True)

    def to_slack_ts(self, iso_str: str) -> str:
        """Convert ISO timestamp to Slack epoch format."""
        try:
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
            return f"{dt.timestamp():.6f}"
        except ValueError as exc:
            logger.warning(f"Invalid timestamp {iso_str}: {exc}")
            return f"{datetime.now().timestamp():.6f}"

    def get_date_key(self, iso_str: str) -> str:
        """Extract date in YYYY-MM-DD format."""
        try:
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return datetime.now().strftime("%Y-%m-%d")

    def sanitize_text(self, text: str) -> str:
        """Convert Teams HTML to Slack markdown."""
        if not text:
            return ""

        text = text.replace("<b>", "*").replace("</b>", "*")
        text = text.replace("<i>", "_").replace("</i>", "_")
        text = text.replace("<strong>", "*").replace("</strong>", "*")
        text = text.replace("<em>", "_").replace("</em>", "_")
        text = text.replace("<div>", "").replace("</div>", "")
        text = text.replace("<br>", "\n").replace("<br/>", "\n")
        text = text.replace("&quot;", '"').replace("&amp;", "&")
        text = text.replace("&lt;", "<").replace("&gt;", ">")

        if len(text) > self.max_message_length:
            logger.warning(
                f"Message truncated from {len(text)} to {self.max_message_length}"
            )
            text = text[: self.max_message_length - 3] + "..."

        return text.strip()

    def get_message_hash(self, msg: Dict) -> str:
        """Generate hash for deduplication."""
        key = f"{msg['id']}_{msg['createdDateTime']}_{msg['body'].get('content', '')}"
        return hashlib.sha256(key.encode()).hexdigest()

    def process_attachments(
        self, attachments: List[Dict], output_dir: Optional[str] = None
    ) -> List[Dict]:
        """Process attachments with optional download and size guard."""
        processed = []
        if not attachments:
            return processed

        output_dir = output_dir or self.attachment_dir
        os.makedirs(output_dir, exist_ok=True)

        for attachment in attachments:
            if "contentUrl" not in attachment:
                continue

            entry = {
                "title": attachment.get("name", "attachment"),
                "url": attachment["contentUrl"],
                "teams_ref_id": attachment.get("id"),
            }

            if self.attachment_processing and not self.dry_run:
                try:
                    response = requests.get(
                        attachment["contentUrl"], stream=True, timeout=10
                    )
                    response.raise_for_status()
                    filename = attachment.get("name", attachment.get("id", "file"))
                    safe_name = "".join(
                        c if c.isalnum() or c in ("-", "_") else "_" for c in filename
                    )
                    target_path = os.path.join(output_dir, safe_name)
                    size = 0
                    with open(target_path, "wb") as file_handle:
                        for chunk in response.iter_content(chunk_size=8192):
                            if not chunk:
                                continue
                            size += len(chunk)
                            if size > self.max_attachment_bytes:
                                raise ValueError("Attachment exceeds max size")
                            file_handle.write(chunk)
                    entry["download_path"] = target_path
                    self.stats["attachments_downloaded"] += 1
                except Exception as exc:  # noqa: BLE001 - logging path
                    logger.warning(
                        f"Failed to download attachment {attachment.get('id')}: {exc}"
                    )
            processed.append(entry)

        return processed

    def transform_message(
        self,
        msg: Dict,
        parent_ts: Optional[str] = None,
        parent_user_id: Optional[str] = None,
        parent_teams_id: Optional[str] = None,
    ) -> Optional[Dict]:
        """Transform Teams message to Slack format."""
        try:
            if "id" not in msg or "createdDateTime" not in msg:
                raise ValueError("Missing required fields: id or createdDateTime")

            if self.deduplication:
                msg_hash = self.get_message_hash(msg)
                if msg_hash in self.message_hashes:
                    self.stats["skipped_duplicates"] += 1
                    return None
                self.message_hashes.add(msg_hash)

            user_id = msg.get("from", {}).get("user", {}).get("id")
            if not user_id:
                logger.warning(f"Message {msg['id']} missing user ID")
                user_id = "U_GHOST"

            slack_user = self.user_map.get(
                user_id, f"U_UNKNOWN_{hashlib.md5(user_id.encode()).hexdigest()[:8]}"
            )

            text = msg.get("body", {}).get("content", "")
            text = self.sanitize_text(text)

            if not text:
                logger.warning(f"Message {msg['id']} has empty content")
                return None

            slack_msg = {
                "type": "message",
                "user": slack_user,
                "text": text,
                "ts": self.to_slack_ts(msg["createdDateTime"]),
                "team": self.slack_team_id,
                "replace_original": False,
                "metadata": {
                    "event_type": "migration_source",
                    "event_payload": {
                        "teams_id": msg["id"],
                        "teams_user_id": user_id,
                        "parent_teams_id": parent_teams_id,
                        "migration_timestamp": datetime.now().isoformat(),
                    },
                },
            }

            attachments = msg.get("attachments", [])
            if attachments:
                processed_attachments = self.process_attachments(attachments)
                if processed_attachments:
                    slack_msg["files"] = processed_attachments

            if parent_ts:
                slack_msg["thread_ts"] = parent_ts
                slack_msg["parent_user_id"] = parent_user_id

            self.stats["successful_transforms"] += 1
            return slack_msg

        except Exception as exc:  # noqa: BLE001 - log and continue
            self.stats["failed_transforms"] += 1
            error_msg = f"Failed to transform message {msg.get('id', 'UNKNOWN')}: {exc}"
            logger.error(error_msg)
            self.error_log.append(error_msg)
            return None

    def _iter_messages(self, file_path: str) -> Iterable[Dict]:
        """Yield parent messages one by one using streaming parser when available."""
        try:
            import ijson

            with open(file_path, "r", encoding="utf-8-sig") as handle:
                for item in ijson.items(handle, "item"):
                    yield item
        except ImportError:
            logger.warning("ijson not installed; falling back to in-memory json.load")
            with open(file_path, "r", encoding="utf-8-sig") as handle:
                data = json.load(handle)
            if not isinstance(data, list):
                raise ValueError("Expected JSON array at root level")
            for item in data:
                yield item

    def _ensure_writer(self) -> None:
        if not self.export_writer:
            self.export_writer = SlackExportWriter(self.output_dir)

    def _flush_buffers(self) -> None:
        if not self.messages_by_date:
            return
        if self.output_dir:
            self._ensure_writer()
            for date_key, msgs in list(self.messages_by_date.items()):
                if not msgs:
                    continue
                self.export_writer.write_batch(date_key, msgs)
                self.messages_by_date[date_key] = []
        self.buffered_message_count = 0

    def _respect_rate_limit(self) -> None:
        if self.api_rate_limit_per_second <= 0:
            return
        min_interval = 1 / float(self.api_rate_limit_per_second)
        elapsed = time.time() - self._last_api_call
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)

    def _ensure_slack_client(self) -> None:
        if self._slack_client or not self.upload_enabled:
            return
        try:
            from slack_sdk import WebClient

            self._slack_client = WebClient(token=self.slack_token)
        except ImportError as exc:
            raise RuntimeError("slack-sdk is required for Slack uploads") from exc

    def _resolve_channel(self) -> None:
        if self._channel_id or not self.upload_enabled:
            return
        self._ensure_slack_client()
        client = self._slack_client
        cursor = None
        try:
            while True:
                response = client.conversations_list(
                    types="public_channel,private_channel",
                    limit=200,
                    cursor=cursor,
                )
                for channel in response.get("channels", []):
                    if channel.get("name") == self.channel_name:
                        self._channel_id = channel.get("id")
                        break
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if self._channel_id or not cursor:
                    break

            if not self._channel_id:
                create_resp = client.conversations_create(
                    name=self.channel_name, is_private=False
                )
                self._channel_id = create_resp["channel"]["id"]
        except Exception as exc:  # noqa: BLE001 - Slack API failure
            self.error_log.append(str(exc))
            raise

    def _upload_message(self, msg: Dict) -> None:
        if not self.upload_enabled:
            return
        try:
            self._resolve_channel()
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Failed to resolve Slack channel: {exc}")
            self.stats["api_failures"] += 1
            return

        client = self._slack_client
        payload = {
            "channel": self._channel_id,
            "text": msg.get("text", ""),
            "metadata": msg.get("metadata"),
        }

        parent_id = msg.get("metadata", {}).get("event_payload", {}).get(
            "parent_teams_id"
        )
        if parent_id and parent_id in self.thread_ts_map:
            payload["thread_ts"] = self.thread_ts_map[parent_id]

        attempts = 3
        for attempt in range(1, attempts + 1):
            try:
                self._respect_rate_limit()
                response = client.chat_postMessage(**payload)
                self._last_api_call = time.time()
                slack_ts = response["ts"]
                teams_id = msg.get("metadata", {}).get("event_payload", {}).get(
                    "teams_id"
                )
                if teams_id:
                    self.thread_ts_map[teams_id] = slack_ts
                self.stats["api_uploads"] += 1
                return
            except Exception as exc:  # noqa: BLE001 - retry on failure
                wait_time = 2**attempt
                if hasattr(exc, "response") and getattr(exc.response, "status_code", 0) == 429:
                    retry_after = exc.response.headers.get("Retry-After")
                    wait_time = int(retry_after) if retry_after else wait_time
                logger.warning(
                    f"Slack API error on attempt {attempt}/{attempts}: {exc}"
                )
                time.sleep(wait_time)

        self.stats["api_failures"] += 1

    def process_export_streaming(self, file_path: str, output_dir: Optional[str] = None) -> None:
        """Stream process Teams export and optionally upload to Slack."""
        self.output_dir = output_dir or self.output_dir
        try:
            for idx, parent in enumerate(self._iter_messages(file_path)):
                try:
                    self.stats["total_messages"] += 1

                    parent_slack = self.transform_message(parent)
                    if parent_slack:
                        parent_date = self.get_date_key(parent["createdDateTime"])
                        self.messages_by_date[parent_date].append(parent_slack)
                        self.buffered_message_count += 1
                        if self.upload_enabled:
                            self._upload_message(parent_slack)

                    for reply in parent.get("replies", []):
                        self.stats["total_messages"] += 1
                        reply_slack = self.transform_message(
                            reply,
                            parent_ts=parent_slack["ts"] if parent_slack else None,
                            parent_user_id=parent_slack["user"] if parent_slack else None,
                            parent_teams_id=parent.get("id"),
                        )
                        if reply_slack:
                            reply_date = self.get_date_key(reply["createdDateTime"])
                            self.messages_by_date[reply_date].append(reply_slack)
                            self.buffered_message_count += 1
                            if self.upload_enabled:
                                self._upload_message(reply_slack)

                    if self.buffered_message_count >= self.batch_size:
                        self._flush_buffers()

                    if (idx + 1) % 100 == 0:
                        logger.info(f"Processed {idx + 1} parent messages...")
                        if self.notifier and (idx + 1) % 500 == 0:
                            self.notifier.check_anomalies(self.stats)

                except Exception as exc:  # noqa: BLE001
                    logger.error(f"Error processing parent message {idx}: {exc}")
                    self.error_log.append(str(exc))
                    self.stats["failed_transforms"] += 1

                    if self.notifier and len(self.error_log) >= self.notifier.alert_threshold.get(
                        "critical_error_count", 10
                    ):
                        if len(self.error_log) == self.notifier.alert_threshold.get(
                            "critical_error_count", 10
                        ):
                            self.notifier.notify_error_threshold(
                                len(self.error_log), self.error_log[-5:]
                            )

            self._flush_buffers()

        except json.JSONDecodeError as exc:
            logger.error(f"Invalid JSON in {file_path}: {exc}")
            if self.notifier:
                self.notifier.notify_migration_failed(
                    f"Invalid JSON: {str(exc)}", self.stats
                )
            raise
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            if self.notifier:
                self.notifier.notify_migration_failed(
                    f"File not found: {file_path}", self.stats
                )
            raise
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Unexpected error: {exc}")
            if self.notifier:
                self.notifier.notify_migration_failed(
                    f"Unexpected error: {str(exc)}", self.stats
                )
            raise

    def export_to_slack_format(self, output_dir: Optional[str] = None) -> None:
        """Export buffered messages to Slack import files and finalize streams."""
        self.output_dir = output_dir or self.output_dir
        if self.messages_by_date:
            self._flush_buffers()
        if self.export_writer:
            self.export_writer.finalize()

        if self.notifier:
            self.notifier.check_anomalies(self.stats)
            duration = (datetime.now() - self.migration_start_time).total_seconds() / 60
            self.notifier.notify_migration_complete(self.stats, duration)

    def print_migration_report(self) -> None:
        """Print migration statistics."""
        print("\n" + "=" * 60)
        print("MIGRATION REPORT".center(60))
        print("=" * 60)
        print(f"Total Messages Processed:     {self.stats['total_messages']:,}")
        print(f"Successful Transforms:       {self.stats['successful_transforms']:,}")
        print(f"Skipped (Duplicates):        {self.stats['skipped_duplicates']:,}")
        print(f"Failed Transforms:           {self.stats['failed_transforms']:,}")
        print(f"Attachments Processed:       {self.stats['attachments_downloaded']:,}")
        print(f"Slack API Uploads:           {self.stats['api_uploads']:,}")
        print(f"API Upload Failures:         {self.stats['api_failures']:,}")
        print("=" * 60)

        if self.error_log:
            print(f"\nErrors encountered: {len(self.error_log)}")
            for error in self.error_log[:5]:
                print(f"  - {error}")
            if len(self.error_log) > 5:
                print(
                    f"  ... and {len(self.error_log) - 5} more (see logs/migration.log)"
                )

        print("=" * 60 + "\n")
