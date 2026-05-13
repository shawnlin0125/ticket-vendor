"""KKTIX Plugin — stub.

Replace this stub with real KKTIX API integration.
"""

from platform_plugin_sdk import Plugin, HealthStatus, TestReport, Fixture


class KKTIxPlugin(Plugin):
    plugin_id = "kktix"
    plugin_name = "KKTIX"
    version = "0.1.0"

    async def start(self) -> None:
        print(f"[kktix] Started")

    async def stop(self) -> None:
        print(f"[kktix] Stopped")

    async def health(self) -> HealthStatus:
        return HealthStatus(healthy=True, latency_ms=1, message="stub")

    def get_mock_server(self):
        from vendor_kktix.mock.server import KKTIxMockServer
        return KKTIxMockServer()

    def get_fixtures(self) -> list[Fixture]:
        return []

    async def run_tests(self, mock_port: int) -> TestReport:
        return TestReport(
            plugin_id=self.plugin_id,
            plugin_version=self.version,
            passed=True, total=1, passed_count=1,
            results=[],
        )
