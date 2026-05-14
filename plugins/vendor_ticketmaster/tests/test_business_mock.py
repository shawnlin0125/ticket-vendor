"""Business mock tests — verify the proxy's unified API works correctly.

These tests simulate the 業務系統（主系統）making calls to the proxy's
unified API (/api/v1/search, /orders, ...) and verify the proxy
handles them correctly against the vendor mock.
"""

import pytest


async def test_business_mock_client_exists(plugin):
    """Business mock client factory must be importable."""
    client_class = plugin.get_business_mock_server()
    assert client_class is not None
    assert hasattr(client_class, "search")
    assert hasattr(client_class, "create_order")
    assert hasattr(client_class, "get_order")
    assert hasattr(client_class, "poll_order")
    assert hasattr(client_class, "check_inventory")


# ── Full integration with mock servers will be implemented ──
# when the proxy's unified API handlers are wired up.
# These are placeholder tests that validate the structure is correct.
# See test_integration.py for end-to-end tests.
