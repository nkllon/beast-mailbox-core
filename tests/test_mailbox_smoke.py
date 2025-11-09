"""End-to-end smoke tests for filesystem and Redis mailboxes."""

import json
import subprocess

import pytest

from tests.smoke.orchestrator import (
    LoadRampConfig,
    run_load_ramp,
    run_smoke_once,
    build_prometheus_config_from_env,
)


def _ensure_docker_available() -> None:
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"Docker is required for smoke tests: {exc}")
    if result.returncode != 0:  # pragma: no cover - environment dependent
        pytest.skip(f"Docker command failed: {result.stderr.strip()}")


@pytest.mark.asyncio
async def test_filesystem_and_redis_smoke(
    tmp_path_factory, redis_available, redis_config
):
    """Run smoke scenarios across filesystem and Redis backends."""

    _ensure_docker_available()

    if not redis_available:
        pytest.skip("Redis is required for smoke tests")

    prometheus_config = build_prometheus_config_from_env()

    result = await run_smoke_once(tmp_path_factory, redis_config, prometheus_config)

    assert result.scenarios["filesystem"].success
    assert result.scenarios["redis"].success
    assert result.telemetry.payload is not None
    summary_path = result.artifact_dir / "summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["suite_run_id"] == result.suite_run_id


@pytest.mark.asyncio
async def test_smoke_load_ramp(tmp_path_factory, redis_available, redis_config):
    """Execute a geometric load ramp with minimal concurrency for health reporting."""

    _ensure_docker_available()

    if not redis_available:
        pytest.skip("Redis is required for smoke tests")

    prometheus_config = build_prometheus_config_from_env()
    load_config = LoadRampConfig(
        concurrency_levels=[1], max_batch_duration=30.0, stop_on_failure=True
    )

    summary = await run_load_ramp(
        tmp_path_factory, redis_config, prometheus_config, load_config
    )

    assert summary.batches
    assert summary.batches[0].success_count >= 1
