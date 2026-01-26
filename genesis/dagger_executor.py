"""
Dagger Executor - Containerized CI/CD Pipeline Execution.

This module provides deterministic, sandboxed execution environments
for linting, testing, and building code. Unlike subprocess calls,
Dagger ensures reproducible results across all environments.

Key Principles:
- Ephemeral containers (no side effects)
- Consistent environments (matches production)
- Secure execution (isolated from host)
- Detailed error capture (for self-healing loop)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
import asyncio
import os


@dataclass
class ExecutionResult:
    """Result from a Dagger pipeline execution."""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int
    container_id: Optional[str] = None


@dataclass
class PipelineConfig:
    """Configuration for a Dagger pipeline."""
    base_image: str = "python:3.10-slim"
    workspace_path: str = "/app"
    install_commands: List[str] = field(default_factory=lambda: [
        "pip install --upgrade pip",
        "pip install ruff mypy pytest pytest-asyncio pydantic fastapi sqlmodel"
    ])
    environment: Dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 300


class DaggerExecutor:
    """
    Executes code in isolated Dagger containers.

    This class provides the "hands" for the AI agents, allowing them
    to run linters, tests, and builds in a safe, reproducible environment.

    Example:
        executor = DaggerExecutor()

        # Run linter
        result = await executor.run_linter("/path/to/workspace")
        if not result.success:
            print(f"Linting failed: {result.stderr}")

        # Run tests
        result = await executor.run_tests("/path/to/workspace")
        if not result.success:
            print(f"Tests failed: {result.stdout}")
    """

    def __init__(
        self,
        config: Optional[PipelineConfig] = None,
        dagger_client: Optional[Any] = None
    ):
        """
        Initialize the Dagger executor.

        Args:
            config: Pipeline configuration
            dagger_client: Optional pre-configured Dagger client
        """
        self.config = config or PipelineConfig()
        self._client = dagger_client
        self._connected = False

    async def connect(self) -> None:
        """
        Connect to Dagger engine.

        This initializes the Dagger client if not already provided.
        Dagger will automatically start a local engine if needed.
        """
        if self._connected:
            return

        if self._client is None:
            try:
                import dagger
                self._client = await dagger.Connection().__aenter__()
                self._connected = True
            except ImportError:
                raise ImportError(
                    "Dagger SDK not installed. Install with: pip install dagger-io"
                )
            except Exception as e:
                raise RuntimeError(f"Failed to connect to Dagger: {e}")

    async def disconnect(self) -> None:
        """Disconnect from Dagger engine."""
        if self._connected and self._client:
            await self._client.__aexit__(None, None, None)
            self._connected = False

    async def _create_base_container(self, workspace_path: str) -> Any:
        """
        Create base container with workspace mounted.

        Args:
            workspace_path: Host path to mount as /app

        Returns:
            Configured Dagger container
        """
        await self.connect()

        # Get the workspace directory from host
        src = self._client.host().directory(workspace_path)

        # Create base container
        container = (
            self._client.container()
            .from_(self.config.base_image)
        )

        # Run install commands
        for cmd in self.config.install_commands:
            container = container.with_exec(["sh", "-c", cmd])

        # Mount workspace
        container = (
            container
            .with_directory(self.config.workspace_path, src)
            .with_workdir(self.config.workspace_path)
        )

        # Set environment variables
        for key, value in self.config.environment.items():
            container = container.with_env_variable(key, value)

        return container

    async def run_linter(self, workspace_path: str) -> ExecutionResult:
        """
        Run ruff and mypy linters on workspace.

        This is the primary quality gate for generated code.

        Args:
            workspace_path: Path to the code to lint

        Returns:
            ExecutionResult with linter output
        """
        import time
        start = time.time()

        try:
            container = await self._create_base_container(workspace_path)

            # Run ruff first (faster)
            try:
                ruff_output = await (
                    container
                    .with_exec(["ruff", "check", "."])
                    .stdout()
                )
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    stdout="",
                    stderr=f"RUFF FAILED:\n{str(e)}",
                    exit_code=1,
                    duration_ms=int((time.time() - start) * 1000)
                )

            # Run mypy (stricter)
            try:
                mypy_output = await (
                    container
                    .with_exec(["mypy", ".", "--strict", "--ignore-missing-imports"])
                    .stdout()
                )
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    stdout=ruff_output,
                    stderr=f"MYPY FAILED:\n{str(e)}",
                    exit_code=1,
                    duration_ms=int((time.time() - start) * 1000)
                )

            return ExecutionResult(
                success=True,
                stdout=f"RUFF:\n{ruff_output}\n\nMYPY:\n{mypy_output}",
                stderr="",
                exit_code=0,
                duration_ms=int((time.time() - start) * 1000)
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Linter execution failed: {str(e)}",
                exit_code=1,
                duration_ms=int((time.time() - start) * 1000)
            )

    async def run_tests(
        self,
        workspace_path: str,
        test_pattern: str = "tests/"
    ) -> ExecutionResult:
        """
        Run pytest on workspace.

        This executes the test suite in an isolated container.

        Args:
            workspace_path: Path to the code
            test_pattern: Pattern for test discovery

        Returns:
            ExecutionResult with test output
        """
        import time
        start = time.time()

        try:
            container = await self._create_base_container(workspace_path)

            # Run pytest with verbose output and coverage
            try:
                test_output = await (
                    container
                    .with_exec([
                        "pytest",
                        test_pattern,
                        "-v",
                        "--tb=short",
                        "--no-header",
                        "-q"
                    ])
                    .stdout()
                )

                return ExecutionResult(
                    success=True,
                    stdout=test_output,
                    stderr="",
                    exit_code=0,
                    duration_ms=int((time.time() - start) * 1000)
                )

            except Exception as e:
                # Pytest failed - capture output
                return ExecutionResult(
                    success=False,
                    stdout="",
                    stderr=f"TESTS FAILED:\n{str(e)}",
                    exit_code=1,
                    duration_ms=int((time.time() - start) * 1000)
                )

        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Test execution failed: {str(e)}",
                exit_code=1,
                duration_ms=int((time.time() - start) * 1000)
            )

    async def run_command(
        self,
        workspace_path: str,
        command: List[str]
    ) -> ExecutionResult:
        """
        Run arbitrary command in container.

        Use this for custom build steps or domain-specific tools.

        Args:
            workspace_path: Path to mount
            command: Command and arguments

        Returns:
            ExecutionResult
        """
        import time
        start = time.time()

        try:
            container = await self._create_base_container(workspace_path)

            try:
                output = await container.with_exec(command).stdout()
                return ExecutionResult(
                    success=True,
                    stdout=output,
                    stderr="",
                    exit_code=0,
                    duration_ms=int((time.time() - start) * 1000)
                )
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    stdout="",
                    stderr=str(e),
                    exit_code=1,
                    duration_ms=int((time.time() - start) * 1000)
                )

        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Command execution failed: {str(e)}",
                exit_code=1,
                duration_ms=int((time.time() - start) * 1000)
            )


class DaggerExecutorFallback:
    """
    Fallback executor using subprocess when Dagger is unavailable.

    This provides compatibility for development environments without
    Docker/Dagger, but should NOT be used in production.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()

    async def connect(self) -> None:
        """No-op for fallback."""
        pass

    async def disconnect(self) -> None:
        """No-op for fallback."""
        pass

    async def run_linter(self, workspace_path: str) -> ExecutionResult:
        """Run linter using subprocess (fallback)."""
        import subprocess
        import time

        start = time.time()

        try:
            # Run ruff
            ruff_result = subprocess.run(
                ["ruff", "check", workspace_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            if ruff_result.returncode != 0:
                return ExecutionResult(
                    success=False,
                    stdout=ruff_result.stdout,
                    stderr=f"RUFF FAILED:\n{ruff_result.stderr}",
                    exit_code=ruff_result.returncode,
                    duration_ms=int((time.time() - start) * 1000)
                )

            # Run mypy
            mypy_result = subprocess.run(
                ["mypy", workspace_path, "--strict", "--ignore-missing-imports"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if mypy_result.returncode != 0:
                return ExecutionResult(
                    success=False,
                    stdout=mypy_result.stdout,
                    stderr=f"MYPY FAILED:\n{mypy_result.stderr}",
                    exit_code=mypy_result.returncode,
                    duration_ms=int((time.time() - start) * 1000)
                )

            return ExecutionResult(
                success=True,
                stdout=f"{ruff_result.stdout}\n{mypy_result.stdout}",
                stderr="",
                exit_code=0,
                duration_ms=int((time.time() - start) * 1000)
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=1,
                duration_ms=int((time.time() - start) * 1000)
            )

    async def run_tests(
        self,
        workspace_path: str,
        test_pattern: str = "tests/"
    ) -> ExecutionResult:
        """Run tests using subprocess (fallback)."""
        import subprocess
        import time

        start = time.time()
        test_path = os.path.join(workspace_path, test_pattern)

        try:
            result = subprocess.run(
                ["pytest", test_path, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=120
            )

            return ExecutionResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                duration_ms=int((time.time() - start) * 1000)
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=1,
                duration_ms=int((time.time() - start) * 1000)
            )


def create_executor(use_dagger: bool = True) -> "DaggerExecutor | DaggerExecutorFallback":
    """
    Factory function to create appropriate executor.

    Args:
        use_dagger: Whether to use Dagger (requires Docker)

    Returns:
        DaggerExecutor or DaggerExecutorFallback
    """
    if use_dagger:
        try:
            import dagger
            return DaggerExecutor()
        except ImportError:
            print("Warning: Dagger not available, using subprocess fallback")
            return DaggerExecutorFallback()
    return DaggerExecutorFallback()


__all__ = [
    "DaggerExecutor",
    "DaggerExecutorFallback",
    "ExecutionResult",
    "PipelineConfig",
    "create_executor",
]
