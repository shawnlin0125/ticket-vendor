"""Contract tests for KKTIX plugin."""
from platform_plugin_sdk import Plugin


async def test_plugin_metadata(plugin: Plugin):
    assert plugin.plugin_id == "kktix"
    assert plugin.plugin_name == "KKTIX"


async def test_has_mock_server(plugin: Plugin):
    mock = plugin.get_mock_server()
    assert mock is not None
    assert hasattr(mock, "start")
    assert hasattr(mock, "stop")
