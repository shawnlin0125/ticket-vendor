"""Pytest fixtures for ticketmaster plugin tests.

Provides the plugin instance to all test functions.
Tests are run against the plugin's mock server (isolated — no real API).
"""

import pytest
from vendor_ticketmaster.plugin import TicketmasterPlugin


@pytest.fixture
async def plugin():
    """Return a TicketmasterPlugin instance for testing."""
    return TicketmasterPlugin()
