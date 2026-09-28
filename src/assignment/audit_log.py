"""
Assignment 11 — Structured audit log.

Records every interaction for forensics. Never blocks by itself —
other layers catch attacks; this layer makes them reviewable.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import time
import uuid


def default_audit_log_path() -> str:
    """Always resolve to <repo>/outputs/… (safe when cwd is src/)."""
    repo_root = Path(__file__).resolve().parents[2]
    return str(repo_root / "outputs" / "audit_log.json")


class AuditLogPlugin:
    """Framework-agnostic audit logger (wire into ADK callbacks or your pipeline)."""

    def __init__(self):
        self.name = "audit_log"
        self.logs: list[dict] = []
        self._open: dict[str, dict] = {}

    def record_input(self, *, user_id: str, text: str, request_id: str | None = None):
        """Store request input and start time; return its correlation ID."""
        correlation_id = request_id or f"{user_id}-{uuid.uuid4().hex[:12]}"
        self._open[correlation_id] = {
            "request_id": correlation_id,
            "user_id": user_id,
            "input": text,
            "started_at": utc_now_iso(),
            "started_monotonic": time.perf_counter(),
        }
        return correlation_id

    def record_output(
        self,
        *,
        user_id: str,
        text: str,
        blocked: bool = False,
        layer: str | None = None,
        request_id: str | None = None,
    ):
        """Complete an audit entry with output, policy decision and latency."""
        correlation_id = request_id
        if correlation_id is None:
            correlation_id = next(
                (
                    key
                    for key, value in reversed(list(self._open.items()))
                    if value.get("user_id") == user_id
                ),
                f"{user_id}-{uuid.uuid4().hex[:12]}",
            )

        started = self._open.pop(correlation_id, None)
        completed_at = utc_now_iso()
        latency_ms = 0.0
        if started is not None:
            latency_ms = max(
                0.0,
                (time.perf_counter() - started["started_monotonic"]) * 1000,
            )

        entry = {
            "request_id": correlation_id,
            "user_id": user_id,
            "input": started.get("input", "") if started else "",
            "output": text,
            "blocked": bool(blocked),
            "layer": layer,
            "started_at": started.get("started_at") if started else None,
            "completed_at": completed_at,
            "latency_ms": round(latency_ms, 3),
        }
        self.logs.append(entry)
        return entry

    def export_json(self, filepath: str | None = None):
        """Write logs to disk (JSON array) under repo-root ``outputs/`` by default."""
        path = Path(filepath or default_audit_log_path())
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.logs, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
