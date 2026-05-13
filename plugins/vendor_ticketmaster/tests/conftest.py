"""Pytest fixtures for ticketmaster plugin tests."""

import pytest
from vendor_ticketmaster.plugin import TicketmasterPlugin


@pytest.fixture
def plugin():
    """Return a TicketmasterPlugin instance for testing."""
    return TicketmasterPlugin()
