"""TicketMaster Plugin — ticket vendor integration.

This is a reference implementation showing the complete plugin structure:
  - plugin.py      ← implements Plugin ABC
  - mock/          ← fake API server for isolated testing
  - fixtures/      ← test data files
  - schema/        ← DB migrations (PostgreSQL schema)
  - tests/         ← self-tests (run against mock, not real API)

Once CI passes, this plugin can be enabled in plugin-hub.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from platform_plugin_sdk import Plugin, HealthStatus, TestReport, TestResult, Fixture

_HERE = Path(__file__).parent


class TicketmasterPlugin(Plugin):
    """TicketMaster ticket vendor integration."""

    plugin_id = "ticketmaster"
    plugin_name = "TicketMaster"
    version = "0.1.0"

    def __init__(self):
        self._started = False
        self._api_base = "https://api.ticketmaster.com"  # real API
        self._api_key = ""

    # ── Lifecycle ─────────────────────────────────────────────

    async def start(self) -> None:
        """Start the plugin: connect to real API, begin scheduler."""
        self._api_key = self._load_api_key()
        # In production: self._start_scheduler()
        self._started = True
        print(f"[ticketmaster] Started (API: {self._api_base})")

    async def stop(self) -> None:
        """Stop the plugin: disconnect, stop scheduler."""
        self._started = False
        print("[ticketmaster] Stopped")

    async def health(self) -> HealthStatus:
        """Check if the real API is reachable."""
        if not self._started:
            return HealthStatus(healthy=False, latency_ms=0, message="not started")

        start = time.monotonic()
        try:
            # In production: do a real API ping
            await self._ping()
            latency = (time.monotonic() - start) * 1000
            return HealthStatus(healthy=True, latency_ms=latency, message="OK")
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            return HealthStatus(healthy=False, latency_ms=latency, message=str(e))

    # ── Testing Support ───────────────────────────────────────

    def get_mock_server(self):
        """Return a mock TicketMaster API server."""
        from vendor_ticketmaster.mock.server import TicketmasterMockServer

        fixtures_dir = _HERE / "fixtures"
        return TicketmasterMockServer(fixtures_dir)

    def get_fixtures(self) -> list[Fixture]:
        """List all test fixtures."""
        fixtures_dir = _HERE / "fixtures"
        result = []
        for f in sorted(fixtures_dir.glob("*.json")):
            data = json.loads(f.read_text())
            result.append(Fixture(
                name=f.stem,
                description=data.get("_description", f.stem),
                data=data,
            ))
        return result

    async def run_tests(self, mock_port: int) -> TestReport:
        """Run self-tests against mock server."""
        import asyncio
        import importlib

        # Point at mock instead of real API
        self._api_base = f"http://127.0.0.1:{mock_port}"

        results: list[TestResult] = []
        test_files = sorted((_HERE / "tests").glob("test_*.py"))

        for tf in test_files:
            module_name = f"vendor_ticketmaster.tests.{tf.stem}"
            try:
                mod = importlib.import_module(module_name)
                for name in dir(mod):
                    if name.startswith("test_"):
                        fn = getattr(mod, name)
                        if callable(fn):
                            start = time.monotonic()
                            try:
                                if asyncio.iscoroutinefunction(fn):
                                    await fn(self)
                                else:
                                    fn(self)
                                elapsed = (time.monotonic() - start) * 1000
                                results.append(TestResult(name=name, passed=True, duration_ms=elapsed))
                            except Exception as e:
                                elapsed = (time.monotonic() - start) * 1000
                                results.append(TestResult(name=name, passed=False, duration_ms=elapsed, error=str(e)))
            except Exception as e:
                results.append(TestResult(name=tf.stem, passed=False, duration_ms=0, error=str(e)))

        total = len(results)
        passed = sum(1 for r in results if r.passed)
        return TestReport(
            plugin_id=self.plugin_id,
            plugin_version=self.version,
            passed=(passed == total and total > 0),
            total=total,
            passed_count=passed,
            results=results,
        )

    # ── Internal ──────────────────────────────────────────────

    def _load_api_key(self) -> str:
        """Load API key from environment."""
        import os
        return os.environ.get("TICKETMASTER_API_KEY", "")

    async def _ping(self) -> None:
        """Ping the real API."""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._api_base}/ping", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"API returned {resp.status}")
# trigger CI
