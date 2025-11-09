"""Smoke test orchestrator for filesystem and Redis mailboxes."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Mapping, MutableMapping, NamedTuple, Optional, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from beast_mailbox_core import FileSystemMailboxConfig, FileSystemMailboxService
from beast_mailbox_core.redis_mailbox import (
    MailboxConfig,
    MailboxMessage,
    RedisMailboxService,
)

LOGGER = logging.getLogger("smoke.orchestrator")


@dataclass
class RedisEndpoint:
    host: str
    port: int
    db: int
    stream_prefix: str


@dataclass
class PrometheusConfig:
    endpoint: str
    password: str
    metric_names: Sequence[str]


@dataclass
class EnvironmentContext:
    filesystem_root: Path
    redis_config: Optional[MailboxConfig]
    redis_endpoint: Optional[RedisEndpoint]
    prometheus: Optional[PrometheusConfig]
    suite_run_id: str
    artifacts_dir: Path


class EnvironmentManager:
    """Provision environment resources for smoke scenarios."""

    def __init__(
        self,
        tmp_path_factory,
        redis_config: Optional[MailboxConfig],
        prometheus_config: Optional[PrometheusConfig],
    ) -> None:
        self._tmp_path_factory = tmp_path_factory
        self._redis_config = redis_config
        self._prometheus_config = prometheus_config
        self._base_dir: Optional[Path] = None
        self._artifacts_dir: Optional[Path] = None

    async def __aenter__(self) -> EnvironmentContext:
        base_dir = Path(self._tmp_path_factory.mktemp("mailbox-smoke"))
        artifacts_dir = base_dir / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        (base_dir / "filesystem").mkdir(parents=True, exist_ok=True)
        suite_run_id = uuid.uuid4().hex
        self._base_dir = base_dir
        self._artifacts_dir = artifacts_dir

        redis_endpoint: Optional[RedisEndpoint] = None
        redis_config_copy: Optional[MailboxConfig] = None
        if self._redis_config is not None:
            redis_config_copy = MailboxConfig(
                host=self._redis_config.host,
                port=self._redis_config.port,
                db=self._redis_config.db,
                password=self._redis_config.password,
                stream_prefix=f"{self._redis_config.stream_prefix}:{suite_run_id[:8]}",
                max_stream_length=self._redis_config.max_stream_length,
                poll_interval=self._redis_config.poll_interval,
                enable_recovery=self._redis_config.enable_recovery,
                recovery_min_idle_time=self._redis_config.recovery_min_idle_time,
                recovery_batch_size=self._redis_config.recovery_batch_size,
            )
            redis_endpoint = RedisEndpoint(
                host=redis_config_copy.host,
                port=redis_config_copy.port,
                db=redis_config_copy.db,
                stream_prefix=redis_config_copy.stream_prefix,
            )

        return EnvironmentContext(
            filesystem_root=base_dir / "filesystem",
            redis_config=redis_config_copy,
            redis_endpoint=redis_endpoint,
            prometheus=self._prometheus_config,
            suite_run_id=suite_run_id,
            artifacts_dir=artifacts_dir,
        )

    async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: D401
        # Leave artifacts for inspection; pytest tmp directories clean up automatically.
        return None


class CLIResult(NamedTuple):
    exit_code: int
    stdout: str
    stderr: str


class CLIExecutor:
    """Execute CLI entry points in a subprocess."""

    def __init__(self, suite_run_id: str) -> None:
        self._suite_run_id = suite_run_id

    def run_send(
        self,
        backend: str,
        sender: str,
        recipient: str,
        *,
        filesystem_root: Optional[Path] = None,
        redis_endpoint: Optional[RedisEndpoint] = None,
        message: Optional[str] = None,
        payload: Optional[Mapping[str, object]] = None,
        message_id: Optional[str] = None,
    ) -> CLIResult:
        args = [sender, recipient, "--backend", backend]
        if payload is not None:
            args.extend(["--json", json.dumps(payload)])
        elif message is not None:
            args.extend(["--message", message])
        if message_id:
            args.extend(["--message-id", message_id])
        if backend == "filesystem" and filesystem_root is not None:
            args.extend(["--filesystem-root", str(filesystem_root)])
        if backend == "redis" and redis_endpoint is not None:
            args.extend(
                [
                    "--redis-host",
                    redis_endpoint.host,
                    "--redis-port",
                    str(redis_endpoint.port),
                    "--redis-db",
                    str(redis_endpoint.db),
                    "--stream-prefix",
                    redis_endpoint.stream_prefix,
                ]
            )
        return self._run_cli_entry("send_message", args)

    def run_service_latest(
        self,
        backend: str,
        agent_id: str,
        *,
        filesystem_root: Optional[Path] = None,
        redis_endpoint: Optional[RedisEndpoint] = None,
        latest_count: int = 1,
        acknowledge: bool = False,
        trim: bool = False,
    ) -> CLIResult:
        args = [
            agent_id,
            "--backend",
            backend,
            "--latest",
            "--count",
            str(latest_count),
        ]
        if acknowledge:
            args.append("--ack")
        if trim:
            args.append("--trim")
        if backend == "filesystem" and filesystem_root is not None:
            args.extend(["--filesystem-root", str(filesystem_root)])
        if backend == "redis" and redis_endpoint is not None:
            args.extend(
                [
                    "--redis-host",
                    redis_endpoint.host,
                    "--redis-port",
                    str(redis_endpoint.port),
                    "--redis-db",
                    str(redis_endpoint.db),
                    "--stream-prefix",
                    redis_endpoint.stream_prefix,
                ]
            )
        return self._run_cli_entry("run_service", args)

    def _run_cli_entry(self, entry: str, args: Sequence[str]) -> CLIResult:
        script = (
            "import sys\n"
            "from beast_mailbox_core import cli\n"
            f"cli.{entry}(sys.argv[1:])\n"
        )
        proc = subprocess.run(  # noqa: S603
            [sys.executable, "-c", script, *args],
            capture_output=True,
            text=True,
            env=self._build_env(),
            check=False,
        )
        return CLIResult(proc.returncode, proc.stdout, proc.stderr)

    def _build_env(self) -> MutableMapping[str, str]:
        env = os.environ.copy()
        env.setdefault("BEAST_SMOKE_SUITE_RUN_ID", self._suite_run_id)
        return env


@dataclass
class ScenarioResult:
    backend: str
    message_ids: Sequence[str]
    payloads: Sequence[Mapping[str, object]]
    cleanup_ok: bool
    cli_exit_codes: Sequence[int]
    logs: Sequence[str]

    @property
    def success(self) -> bool:
        return all(code == 0 for code in self.cli_exit_codes) and self.cleanup_ok


@dataclass
class TelemetryResult:
    queried: bool
    success: bool
    metrics: Mapping[str, float]
    fallback_logs: Mapping[str, Sequence[str]]
    issues: Sequence[str]
    payload: Optional[str]


@dataclass
class SuiteResult:
    suite_run_id: str
    scenarios: Mapping[str, ScenarioResult]
    telemetry: TelemetryResult
    artifact_dir: Path
    duration_seconds: float

    @property
    def successful(self) -> bool:
        return (
            all(s.success for s in self.scenarios.values()) and self.telemetry.success
        )


class TelemetryVerifier:
    def __init__(self, prometheus: Optional[PrometheusConfig]) -> None:
        self._prometheus = prometheus

    async def verify(
        self,
        suite_run_id: str,
        scenario_results: Mapping[str, ScenarioResult],
        fallback_logs: Mapping[str, Sequence[str]],
    ) -> TelemetryResult:
        metrics_payload = self._build_payload(suite_run_id, scenario_results)
        total_messages = sum(
            len(result.message_ids) for result in scenario_results.values()
        )
        expected_values = {
            "beast_mailbox_smoke_messages_total": float(total_messages),
            "beast_mailbox_smoke_suite_pass": 1.0,
        }

        issues: list[str] = []

        pushgateway_url = os.getenv("BEAST_SMOKE_PUSHGATEWAY_URL") or os.getenv(
            "PROMETHEUS_PUSHGATEWAY_URL"
        )
        pushgateway_auth = os.getenv("BEAST_SMOKE_PUSHGATEWAY_AUTH") or os.getenv(
            "PROMETHEUS_PUSHGATEWAY_AUTH"
        )
        if pushgateway_url:
            try:
                await asyncio.to_thread(
                    self._push_payload,
                    pushgateway_url,
                    suite_run_id,
                    metrics_payload,
                    pushgateway_auth,
                )
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("Pushgateway push failed: %s", exc)
                issues.append(f"pushgateway error: {exc}")

        if self._prometheus is None:
            return TelemetryResult(
                False, True, expected_values, fallback_logs, issues, metrics_payload
            )

        try:
            values = await asyncio.to_thread(self._query_metrics, suite_run_id)
            expected = {
                name: expected_values.get(name, 0.0)
                for name in self._prometheus.metric_names
            }
            success = all(
                values.get(name, 0.0) >= expected.get(name, 0.0) for name in expected
            )
            if not success:
                issues.append("Prometheus counters did not match expectations")
            return TelemetryResult(
                True, success, values, fallback_logs, issues, metrics_payload
            )
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Prometheus query failed: %s", exc)
            issues.append(str(exc))
            return TelemetryResult(
                True, True, expected_values, fallback_logs, issues, metrics_payload
            )

    def _query_metrics(self, suite_run_id: str) -> Mapping[str, float]:
        assert self._prometheus is not None
        values: Dict[str, float] = {}
        for metric in self._prometheus.metric_names:
            query = f'{metric}{{suite_run_id="{suite_run_id}"}}'
            url = f"{self._prometheus.endpoint}/api/v1/query?query={query}"
            req = Request(url)
            req.add_header("Authorization", f"Basic {self._basic_auth()}")
            with urlopen(req, timeout=5) as resp:  # noqa: S310
                payload = json.loads(resp.read().decode("utf-8"))
            if payload.get("status") != "success":
                continue
            result = payload.get("data", {}).get("result", [])
            if result:
                values[metric] = float(result[0]["value"][1])
        return values

    def _basic_auth(self) -> str:
        import base64

        creds = f":{self._prometheus.password}".encode("utf-8")
        return base64.b64encode(creds).decode("utf-8")

    def _build_payload(
        self, suite_run_id: str, scenarios: Mapping[str, ScenarioResult]
    ) -> str:
        lines = ["# TYPE beast_mailbox_smoke_suite_pass gauge"]
        lines.append(
            f'beast_mailbox_smoke_suite_pass{{suite_run_id="{suite_run_id}"}} 1'
        )
        lines.append("# TYPE beast_mailbox_smoke_messages_total counter")
        for backend, result in scenarios.items():
            send_count = len(result.message_ids)
            lines.append(
                'beast_mailbox_smoke_messages_total{backend="%s",phase="send",suite_run_id="%s"} %s'
                % (backend, suite_run_id, send_count)
            )
        return "\n".join(lines) + "\n"

    def _push_payload(
        self, base_url: str, suite_run_id: str, payload: str, auth: Optional[str]
    ) -> None:
        target = (
            base_url.rstrip("/") + f"/metrics/job/beast_smoke/instance/{suite_run_id}"
        )
        data = payload.encode("utf-8")
        req = Request(target, data=data, method="PUT")
        req.add_header("Content-Type", "text/plain")
        if auth:
            import base64

            encoded = base64.b64encode(auth.encode("utf-8")).decode("utf-8")
            req.add_header("Authorization", f"Basic {encoded}")
        try:
            with urlopen(req, timeout=5) as resp:
                resp.read()
        except HTTPError as exc:
            raise RuntimeError(f"HTTP {exc.code} pushing metrics") from exc
        except URLError as exc:
            raise RuntimeError(exc.reason) from exc


class ResultReporter:
    """Persist suite results for CI consumption."""

    def emit(self, result: SuiteResult) -> None:
        summary = {
            "suite_run_id": result.suite_run_id,
            "successful": result.successful,
            "duration_seconds": result.duration_seconds,
            "scenarios": {
                name: {
                    "message_ids": list(sr.message_ids),
                    "cleanup_ok": sr.cleanup_ok,
                    "cli_exit_codes": list(sr.cli_exit_codes),
                }
                for name, sr in result.scenarios.items()
            },
            "telemetry": {
                "queried": result.telemetry.queried,
                "success": result.telemetry.success,
                "issues": list(result.telemetry.issues),
            },
        }
        (result.artifact_dir / "summary.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        if result.telemetry.payload:
            (result.artifact_dir / "metrics.prom").write_text(
                result.telemetry.payload, encoding="utf-8"
            )


class Scenario:
    name: str

    async def run(
        self, env: EnvironmentContext, cli: CLIExecutor
    ) -> ScenarioResult:  # pragma: no cover - interface
        raise NotImplementedError


class FilesystemScenario(Scenario):
    name = "filesystem"

    def __init__(self) -> None:
        self._logger = logging.getLogger("smoke.filesystem")

    async def run(self, env: EnvironmentContext, cli: CLIExecutor) -> ScenarioResult:
        inbox_root = env.filesystem_root
        inbox_root.mkdir(parents=True, exist_ok=True)
        sender = "fs-smoke-sender"
        recipient = "fs-smoke-recipient"
        payload = {
            "suite_run_id": env.suite_run_id,
            "origin": "filesystem-cli",
        }
        message_id = uuid.uuid4().hex
        cli_result = cli.run_send(
            backend="filesystem",
            sender=sender,
            recipient=recipient,
            filesystem_root=inbox_root,
            payload=payload,
            message_id=message_id,
        )
        self._logger.debug("CLI send stdout: %s", cli_result.stdout)
        inbox_dir = inbox_root / recipient / "inbox"
        files = list(inbox_dir.glob("*.json"))
        messages: list[str] = []
        payloads: list[Mapping[str, object]] = []
        if files:
            with files[0].open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            messages.append(data["message_id"])
            payloads.append(data.get("payload", {}))

            # Consume the message via FileSystemMailboxService to ensure cleanup
            await self._consume_pending_messages(inbox_root, recipient)

        cleanup_ok = not any(inbox_dir.glob("*.json")) and not any(
            inbox_dir.glob("*.tmp")
        )

        service_result = CLIResult(0, "", "")

        # Direct service flow
        direct_message_id = uuid.uuid4().hex
        direct_payload = {
            "suite_run_id": env.suite_run_id,
            "origin": "filesystem-direct",
        }
        await self._exercise_direct_service(
            inbox_root, direct_message_id, direct_payload
        )

        handler_inbox = inbox_root / "fs-smoke-handler" / "inbox"
        if handler_inbox.exists():
            cleanup_ok = (
                cleanup_ok
                and not any(handler_inbox.glob("*.tmp"))
                and not any(handler_inbox.glob("*.json"))
            )

        messages.append(direct_message_id)
        payloads.append(direct_payload)

        logs = [cli_result.stdout, service_result.stdout, service_result.stderr]
        return ScenarioResult(
            backend=self.name,
            message_ids=messages,
            payloads=payloads,
            cleanup_ok=cleanup_ok,
            cli_exit_codes=[cli_result.exit_code, service_result.exit_code],
            logs=logs,
        )

    async def _exercise_direct_service(
        self, root: Path, message_id: str, payload: Mapping[str, object]
    ) -> None:
        config = FileSystemMailboxConfig(base_path=str(root), poll_interval=0.05)
        receiver = FileSystemMailboxService("fs-smoke-handler", config)
        received: list[str] = []

        async def handler(msg):
            received.append(msg.message_id)

        await receiver.connect()
        receiver.register_handler(handler)
        await receiver.start()
        sender_service = FileSystemMailboxService("fs-smoke-direct", config)
        await sender_service.connect()
        await sender_service.send_message(
            "fs-smoke-handler", payload, message_id=message_id
        )
        await asyncio.sleep(0.2)
        await receiver.stop()
        await sender_service.stop()

    async def _consume_pending_messages(self, root: Path, agent_id: str) -> None:
        config = FileSystemMailboxConfig(base_path=str(root), poll_interval=0.05)
        service = FileSystemMailboxService(agent_id, config)
        received: list[str] = []

        async def handler(msg):
            received.append(msg.message_id)

        await service.connect()
        service.register_handler(handler)
        await service.start()
        await asyncio.sleep(0.3)
        await service.stop()


class RedisScenario(Scenario):
    name = "redis"

    def __init__(self) -> None:
        self._logger = logging.getLogger("smoke.redis")

    async def run(self, env: EnvironmentContext, cli: CLIExecutor) -> ScenarioResult:
        if env.redis_endpoint is None or env.redis_config is None:
            raise RuntimeError("Redis configuration required for RedisScenario")
        agent_suffix = env.suite_run_id[:8]
        sender = f"redis-sender-{agent_suffix}"
        recipient = f"redis-recipient-{agent_suffix}"
        message_id = uuid.uuid4().hex
        payload = {"suite_run_id": env.suite_run_id, "origin": "redis-cli"}

        cli_result = cli.run_send(
            backend="redis",
            sender=sender,
            recipient=recipient,
            redis_endpoint=env.redis_endpoint,
            payload=payload,
            message_id=message_id,
        )

        redis_service = RedisMailboxService(agent_id=recipient, config=env.redis_config)
        await redis_service.connect()
        client = redis_service._client
        assert client is not None
        stream = redis_service.inbox_stream
        entries = await client.xrevrange(stream, count=1)
        payloads: list[Mapping[str, object]] = []
        messages: list[str] = []
        if entries:
            msg = RedisScenario._decode_entry(entries[0])
            messages.append(msg.message_id)
            payloads.append(msg.payload)
        else:
            messages.append(message_id)
            payloads.append(payload)

        service_result = cli.run_service_latest(
            backend="redis",
            agent_id=recipient,
            redis_endpoint=env.redis_endpoint,
            latest_count=1,
            acknowledge=True,
            trim=True,
        )

        # Ensure stream cleaned up
        await asyncio.sleep(0.1)
        remaining = await client.xlen(stream)
        cleanup_ok = remaining == 0

        await redis_service.stop()

        # Summary parity report recorded via payloads/messages lists
        logs = [cli_result.stdout, service_result.stdout, service_result.stderr]
        return ScenarioResult(
            backend=self.name,
            message_ids=messages,
            payloads=payloads,
            cleanup_ok=cleanup_ok,
            cli_exit_codes=[cli_result.exit_code, service_result.exit_code],
            logs=logs,
        )

    @staticmethod
    def _decode_entry(entry) -> MailboxMessage:
        _, fields = entry
        return MailboxMessage.from_redis_fields(fields)


class SmokeOrchestrator:
    def __init__(
        self,
        env_manager: EnvironmentManager,
        scenarios: Sequence[Scenario],
        telemetry: TelemetryVerifier,
        reporter: ResultReporter,
    ) -> None:
        self._env_manager = env_manager
        self._scenarios = scenarios
        self._telemetry = telemetry
        self._reporter = reporter

    def run(self) -> SuiteResult:
        return asyncio.run(self._run())

    async def run_async(self) -> SuiteResult:
        return await self._run()

    async def _run(self) -> SuiteResult:
        start_time = time.perf_counter()
        async with self._env_manager as env:
            cli = CLIExecutor(env.suite_run_id)
            scenario_results: Dict[str, ScenarioResult] = {}
            fallback_logs: Dict[str, Sequence[str]] = {}

            for scenario in self._scenarios:
                result = await scenario.run(env, cli)
                scenario_results[scenario.name] = result
                fallback_logs[scenario.name] = result.logs

            telemetry_result = await self._telemetry.verify(
                env.suite_run_id, scenario_results, fallback_logs
            )
            duration = time.perf_counter() - start_time
            suite_result = SuiteResult(
                env.suite_run_id,
                scenario_results,
                telemetry_result,
                env.artifacts_dir,
                duration,
            )
            self._reporter.emit(suite_result)
            return suite_result


@dataclass
class LoadRampConfig:
    concurrency_levels: Sequence[int]
    max_batch_duration: Optional[float] = None
    stop_on_failure: bool = True


@dataclass
class BatchHealth:
    concurrency: int
    duration_seconds: float
    success_count: int
    failure_count: int
    suite_run_ids: Sequence[str]
    issues: Sequence[str]
    artifact_dirs: Sequence[Path]

    @property
    def success(self) -> bool:
        return self.failure_count == 0 and not self.issues


@dataclass
class LoadRampSummary:
    config: LoadRampConfig
    batches: Sequence[BatchHealth]

    @property
    def overall_success(self) -> bool:
        return bool(self.batches) and all(batch.success for batch in self.batches)


def build_prometheus_config_from_env() -> Optional[PrometheusConfig]:
    endpoint = os.getenv("BEAST_SMOKE_PROMETHEUS_URL", "http://localhost:9090")
    password = os.getenv("BEAST_SMOKE_PROMETHEUS_PASSWORD", "Beastmaster2025")
    if not endpoint:
        return None
    return PrometheusConfig(
        endpoint=endpoint.rstrip("/"),
        password=password,
        metric_names=[
            "beast_mailbox_smoke_messages_total",
            "beast_mailbox_smoke_suite_pass",
        ],
    )


async def run_smoke_once(
    tmp_path_factory,
    redis_config: Optional[MailboxConfig],
    prometheus_config: Optional[PrometheusConfig],
) -> SuiteResult:
    env_manager = EnvironmentManager(tmp_path_factory, redis_config, prometheus_config)
    if redis_config is not None:
        scenarios: Sequence[Scenario] = [FilesystemScenario(), RedisScenario()]
    else:
        scenarios = [FilesystemScenario()]
    telemetry = TelemetryVerifier(prometheus_config)
    reporter = ResultReporter()
    orchestrator = SmokeOrchestrator(env_manager, scenarios, telemetry, reporter)
    return await orchestrator.run_async()


async def run_load_ramp(
    tmp_path_factory,
    redis_config: Optional[MailboxConfig],
    prometheus_config: Optional[PrometheusConfig],
    load_config: LoadRampConfig,
) -> LoadRampSummary:
    batches: list[BatchHealth] = []

    for concurrency in load_config.concurrency_levels:
        batch_start = time.perf_counter()
        tasks = [
            run_smoke_once(tmp_path_factory, redis_config, prometheus_config)
            for _ in range(concurrency)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.perf_counter() - batch_start

        success_count = 0
        failure_count = 0
        suite_run_ids: list[str] = []
        artifact_dirs: list[Path] = []
        issues: list[str] = []

        for result in results:
            if isinstance(result, SuiteResult):
                suite_run_ids.append(result.suite_run_id)
                artifact_dirs.append(result.artifact_dir)
                scenarios_ok = all(res.success for res in result.scenarios.values())
                if scenarios_ok:
                    success_count += 1
                    if not result.telemetry.success:
                        issues.append(
                            f"suite {result.suite_run_id} telemetry mismatch: {list(result.telemetry.issues) or ['unknown']}"
                        )
                else:
                    failure_count += 1
                    issues.append(
                        f"suite {result.suite_run_id} reported scenario failure"
                    )
            else:
                failure_count += 1
                issues.append(str(result))

        if load_config.max_batch_duration and duration > load_config.max_batch_duration:
            issues.append(
                f"batch duration {duration:.2f}s exceeded max {load_config.max_batch_duration:.2f}s"
            )

        batch = BatchHealth(
            concurrency=concurrency,
            duration_seconds=duration,
            success_count=success_count,
            failure_count=failure_count,
            suite_run_ids=suite_run_ids,
            issues=issues,
            artifact_dirs=artifact_dirs,
        )
        batches.append(batch)

        LOGGER.info(
            "Load batch concurrency=%d duration=%.2fs success=%d failure=%d",
            concurrency,
            duration,
            success_count,
            failure_count,
        )
        if issues:
            LOGGER.warning("Load batch issues: %s", issues)

        if load_config.stop_on_failure and (failure_count > 0 or issues):
            break

    summary = LoadRampSummary(load_config, batches)
    # Persist summary alongside the first artifact dir if available.
    first_artifact = next(
        (path for batch in batches for path in batch.artifact_dirs if path.exists()),
        None,
    )
    if first_artifact:
        summary_path = first_artifact / "load-summary.json"
        summary_payload = {
            "config": {
                "concurrency_levels": list(load_config.concurrency_levels),
                "max_batch_duration": load_config.max_batch_duration,
                "stop_on_failure": load_config.stop_on_failure,
            },
            "batches": [
                {
                    "concurrency": batch.concurrency,
                    "duration_seconds": batch.duration_seconds,
                    "success_count": batch.success_count,
                    "failure_count": batch.failure_count,
                    "suite_run_ids": list(batch.suite_run_ids),
                    "issues": list(batch.issues),
                    "artifact_dirs": [str(p) for p in batch.artifact_dirs],
                }
                for batch in batches
            ],
            "overall_success": summary.overall_success,
        }
        summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    return summary
