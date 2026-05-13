"""Contract tests — verify TicketmasterPlugin implements Plugin ABC correctly."""

import asyncio
from platform_plugin_sdk import Plugin


async def test_plugin_metadata(plugin: Plugin):
    """Plugin must declare plugin_id, plugin_name, version."""
    assert plugin.plugin_id == "ticketmaster"
    assert plugin.plugin_name == "TicketMaster"
    assert plugin.version > "0"


async def test_db_schema(plugin: Plugin):
    """Schema name must follow convention."""
    assert plugin.db_schema == "plugin_ticketmaster"


async def test_redis_prefix(plugin: Plugin):
    """Redis prefix must follow convention."""
    assert plugin.redis_prefix == "plugin:ticketmaster:"


async def test_has_mock_server(plugin: Plugin):
    """Plugin must provide a mock server."""
    mock = plugin.get_mock_server()
    assert mock is not None
    assert hasattr(mock, "start")
    assert hasattr(mock, "stop")


async def test_has_fixtures(plugin: Plugin):
    """Plugin must provide test fixtures."""
    fixtures = plugin.get_fixtures()
    assert len(fixtures) > 0
    names = [f.name for f in fixtures]
    assert "events" in names
    assert "tickets" in names
