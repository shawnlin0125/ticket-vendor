"""ibon Plugin — stub."""
from platform_plugin_sdk import Plugin, HealthStatus, TestReport, Fixture

class IbonPlugin(Plugin):
    plugin_id = "ibon"
    plugin_name = "ibon"
    version = "0.1.0"
    async def start(self) -> None: pass
    async def stop(self) -> None: pass
    async def health(self) -> HealthStatus: return HealthStatus(healthy=True, latency_ms=0, message="stub")
    def get_mock_server(self): return None
    def get_fixtures(self) -> list[Fixture]: return []
    async def run_tests(self, mock_port: int) -> TestReport:
        return TestReport(plugin_id=self.plugin_id, plugin_version=self.version, passed=True, total=0, passed_count=0, results=[])
