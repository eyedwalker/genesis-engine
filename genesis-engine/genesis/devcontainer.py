"""
DevContainer Manager - Human-in-the-Loop Escalation.

When the self-healing loop fails (max iterations reached), the factory
must escalate to a human developer. This module handles:

1. Workspace snapshotting (preserve AI's work)
2. DevContainer configuration generation
3. VS Code Remote URL creation
4. Commit monitoring for resumption

The goal is seamless handoff: human opens link, sees exact AI state,
fixes the issue, commits, and the factory automatically resumes.
"""

from dataclasses import dataclass
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
import os
import json
import shutil
from datetime import datetime


# ============================================================================
# Models
# ============================================================================

class DevContainerConfig(BaseModel):
    """Configuration for a DevContainer."""
    name: str = Field(description="Container name")
    image: str = Field(default="mcr.microsoft.com/devcontainers/python:3.10")

    # Features to install
    features: Dict[str, Any] = Field(default_factory=lambda: {
        "ghcr.io/devcontainers/features/docker-in-docker:2": {}
    })

    # VS Code extensions to install
    customizations: Dict[str, Any] = Field(default_factory=lambda: {
        "vscode": {
            "extensions": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "charliermarsh.ruff",
                "ms-python.mypy-type-checker"
            ]
        }
    })

    # Post-create command
    post_create_command: str = Field(default="pip install poetry && poetry install")

    # Forwarded ports
    forward_ports: List[int] = Field(default=[8000])

    # Environment variables
    container_env: Dict[str, str] = Field(default_factory=dict)


class EscalationSnapshot(BaseModel):
    """Snapshot of the factory state when escalation occurred."""
    snapshot_id: str = Field(description="Unique snapshot identifier")
    tenant_id: str = Field(description="Tenant identifier")
    feature_request: str = Field(description="Original feature request")
    workspace_path: str = Field(description="Path to workspace")
    iteration_count: int = Field(description="Number of iterations attempted")
    error_log: List[str] = Field(description="Errors encountered")
    files_created: List[str] = Field(description="Files created before failure")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # DevContainer info
    devcontainer_path: str = Field(description="Path to devcontainer.json")
    vscode_url: Optional[str] = Field(default=None, description="VS Code Remote URL")

    # Resolution tracking
    resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = Field(default=None)
    resolved_by: Optional[str] = Field(default=None)


# ============================================================================
# DevContainer Manager
# ============================================================================

@dataclass
class DevContainerManager:
    """
    Manages DevContainer creation for human-in-the-loop escalation.

    When the self-healing loop fails, this manager:
    1. Creates a snapshot of the current workspace
    2. Generates a devcontainer.json configuration
    3. Creates a VS Code Remote URL
    4. Monitors for resolution (git commit)

    Example:
        manager = DevContainerManager()

        # Create escalation snapshot
        snapshot = await manager.create_escalation_snapshot(
            tenant_id="apex_logistics",
            workspace_path="/workspaces/apex",
            feature_request="Add temperature monitoring",
            iteration_count=5,
            error_log=["mypy: Missing return type annotation"]
        )

        # Get VS Code URL for developer
        print(f"Open: {snapshot.vscode_url}")

        # Monitor for resolution
        resolved = await manager.check_resolution(snapshot.snapshot_id)
    """

    snapshot_dir: str = "/tmp/genesis/snapshots"
    devcontainer_template: Optional[DevContainerConfig] = None

    def __post_init__(self):
        os.makedirs(self.snapshot_dir, exist_ok=True)
        if self.devcontainer_template is None:
            self.devcontainer_template = DevContainerConfig(
                name="Genesis Factory DevContainer"
            )

    async def create_escalation_snapshot(
        self,
        tenant_id: str,
        workspace_path: str,
        feature_request: str,
        iteration_count: int,
        error_log: List[str],
        files_created: Optional[List[str]] = None
    ) -> EscalationSnapshot:
        """
        Create a snapshot for human escalation.

        This preserves the AI's work and creates a ready-to-use
        DevContainer for a human developer.

        Args:
            tenant_id: Tenant identifier
            workspace_path: Path to the workspace
            feature_request: Original feature request
            iteration_count: Number of iterations attempted
            error_log: Errors encountered
            files_created: Files created before failure

        Returns:
            EscalationSnapshot with all details
        """
        import hashlib
        import time

        # Generate unique snapshot ID
        snapshot_id = hashlib.sha256(
            f"{tenant_id}-{time.time()}".encode()
        ).hexdigest()[:16]

        # Create snapshot directory
        snapshot_path = os.path.join(self.snapshot_dir, snapshot_id)
        os.makedirs(snapshot_path, exist_ok=True)

        # Copy workspace to snapshot
        if os.path.exists(workspace_path):
            snapshot_workspace = os.path.join(snapshot_path, "workspace")
            shutil.copytree(workspace_path, snapshot_workspace, dirs_exist_ok=True)
        else:
            snapshot_workspace = snapshot_path

        # Generate devcontainer.json
        devcontainer_dir = os.path.join(snapshot_workspace, ".devcontainer")
        os.makedirs(devcontainer_dir, exist_ok=True)
        devcontainer_path = os.path.join(devcontainer_dir, "devcontainer.json")

        devcontainer_config = self._generate_devcontainer_config(
            tenant_id=tenant_id,
            feature_request=feature_request,
            error_log=error_log
        )

        with open(devcontainer_path, "w") as f:
            json.dump(devcontainer_config, f, indent=2)

        # Generate escalation README
        readme_path = os.path.join(snapshot_workspace, "ESCALATION_README.md")
        self._write_escalation_readme(
            readme_path,
            feature_request=feature_request,
            iteration_count=iteration_count,
            error_log=error_log,
            files_created=files_created or []
        )

        # Generate VS Code URL
        vscode_url = self._generate_vscode_url(snapshot_workspace)

        # Create snapshot record
        snapshot = EscalationSnapshot(
            snapshot_id=snapshot_id,
            tenant_id=tenant_id,
            feature_request=feature_request,
            workspace_path=snapshot_workspace,
            iteration_count=iteration_count,
            error_log=error_log,
            files_created=files_created or [],
            devcontainer_path=devcontainer_path,
            vscode_url=vscode_url
        )

        # Save snapshot metadata
        metadata_path = os.path.join(snapshot_path, "snapshot.json")
        with open(metadata_path, "w") as f:
            f.write(snapshot.model_dump_json(indent=2))

        return snapshot

    def _generate_devcontainer_config(
        self,
        tenant_id: str,
        feature_request: str,
        error_log: List[str]
    ) -> Dict[str, Any]:
        """Generate devcontainer.json content."""
        config = self.devcontainer_template.model_dump()

        # Customize name
        config["name"] = f"Genesis Escalation: {tenant_id}"

        # Add environment variables
        config["containerEnv"] = {
            "TENANT_ID": tenant_id,
            "FEATURE_REQUEST": feature_request,
            "ESCALATION": "true"
        }

        # Add post-create command
        config["postCreateCommand"] = (
            "pip install poetry && "
            "poetry install && "
            "pip install ruff mypy pytest"
        )

        return config

    def _write_escalation_readme(
        self,
        path: str,
        feature_request: str,
        iteration_count: int,
        error_log: List[str],
        files_created: List[str]
    ) -> None:
        """Write README explaining the escalation."""
        errors_formatted = "\n".join(f"- {e}" for e in error_log[-5:])
        files_formatted = "\n".join(f"- {f}" for f in files_created) or "- None"

        content = f"""# Human Intervention Required

The Genesis Factory was unable to complete this feature after {iteration_count} iterations.

## Original Request

> {feature_request}

## Files Created

{files_formatted}

## Recent Errors

{errors_formatted}

## What You Need To Do

1. Review the generated code in this workspace
2. Fix the errors listed above
3. Run the linter: `ruff check . && mypy . --strict`
4. Run the tests: `pytest`
5. Commit your changes: `git commit -am "Fix: [description]"`

## When You're Done

After committing, the Genesis Factory will automatically:
1. Detect the new commit
2. Resume the QA process
3. Complete the feature if all checks pass

## Tips

- The AI got stuck on the errors above - focus there first
- All code must pass `mypy --strict`
- Follow the patterns in existing files
- Check CONTEXT.md for coding standards

---
*Generated by Genesis Engine - Escalation System*
"""

        with open(path, "w") as f:
            f.write(content)

    def _generate_vscode_url(self, workspace_path: str) -> str:
        """
        Generate VS Code Remote URL.

        In production, this would:
        1. Push workspace to a git repo
        2. Create a GitHub Codespace or similar
        3. Return the launch URL

        For local development, we return a local path URL.
        """
        # Local development: open in VS Code
        # vscode://vscode-remote/dev-container+{path}
        import urllib.parse
        encoded_path = urllib.parse.quote(workspace_path, safe="")
        return f"vscode://vscode-remote/dev-container+{encoded_path}"

    async def check_resolution(self, snapshot_id: str) -> bool:
        """
        Check if a snapshot has been resolved (human committed fix).

        Args:
            snapshot_id: Snapshot identifier

        Returns:
            True if resolved
        """
        snapshot_path = os.path.join(self.snapshot_dir, snapshot_id)
        metadata_path = os.path.join(snapshot_path, "snapshot.json")

        if not os.path.exists(metadata_path):
            return False

        with open(metadata_path) as f:
            data = json.load(f)

        return data.get("resolved", False)

    async def mark_resolved(
        self,
        snapshot_id: str,
        resolved_by: str = "human"
    ) -> Optional[EscalationSnapshot]:
        """
        Mark a snapshot as resolved.

        Args:
            snapshot_id: Snapshot identifier
            resolved_by: Who resolved it

        Returns:
            Updated snapshot or None
        """
        snapshot_path = os.path.join(self.snapshot_dir, snapshot_id)
        metadata_path = os.path.join(snapshot_path, "snapshot.json")

        if not os.path.exists(metadata_path):
            return None

        with open(metadata_path) as f:
            data = json.load(f)

        data["resolved"] = True
        data["resolved_at"] = datetime.utcnow().isoformat()
        data["resolved_by"] = resolved_by

        with open(metadata_path, "w") as f:
            json.dump(data, f, indent=2)

        return EscalationSnapshot(**data)

    async def get_snapshot(self, snapshot_id: str) -> Optional[EscalationSnapshot]:
        """
        Get snapshot by ID.

        Args:
            snapshot_id: Snapshot identifier

        Returns:
            EscalationSnapshot or None
        """
        snapshot_path = os.path.join(self.snapshot_dir, snapshot_id)
        metadata_path = os.path.join(snapshot_path, "snapshot.json")

        if not os.path.exists(metadata_path):
            return None

        with open(metadata_path) as f:
            data = json.load(f)

        return EscalationSnapshot(**data)

    async def list_pending_escalations(
        self,
        tenant_id: Optional[str] = None
    ) -> List[EscalationSnapshot]:
        """
        List all pending (unresolved) escalations.

        Args:
            tenant_id: Optional filter by tenant

        Returns:
            List of pending snapshots
        """
        pending = []

        for snapshot_id in os.listdir(self.snapshot_dir):
            snapshot = await self.get_snapshot(snapshot_id)
            if snapshot and not snapshot.resolved:
                if tenant_id is None or snapshot.tenant_id == tenant_id:
                    pending.append(snapshot)

        return pending

    async def cleanup_resolved(self, older_than_days: int = 7) -> int:
        """
        Clean up resolved snapshots older than specified days.

        Args:
            older_than_days: Age threshold in days

        Returns:
            Number of snapshots cleaned up
        """
        from datetime import timedelta

        threshold = datetime.utcnow() - timedelta(days=older_than_days)
        cleaned = 0

        for snapshot_id in os.listdir(self.snapshot_dir):
            snapshot = await self.get_snapshot(snapshot_id)
            if snapshot and snapshot.resolved:
                if snapshot.resolved_at and snapshot.resolved_at < threshold:
                    snapshot_path = os.path.join(self.snapshot_dir, snapshot_id)
                    shutil.rmtree(snapshot_path, ignore_errors=True)
                    cleaned += 1

        return cleaned


__all__ = [
    "DevContainerManager",
    "DevContainerConfig",
    "EscalationSnapshot",
]
