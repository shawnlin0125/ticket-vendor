"""Integration tests — end-to-end: business mock → proxy → vendor mock.

These tests wire up both mock servers (business + vendor) and the proxy,
then run complete business scenarios to verify the full pipeline works.
"""

import pytest


async def test_scenarios_exist():
    """All required business scenarios must be defined."""
    from vendor_ticketmaster.mock.business.scenarios import SCENARIOS

    assert "happy_path" in SCENARIOS
    assert "vendor_timeout" in SCENARIOS
    assert "empty_results" in SCENARIOS
    assert "invalid_request" in SCENARIOS


async def test_happy_path_scenario_structure():
    """Happy path scenario must cover: search → order → get → poll → inventory."""
    from vendor_ticketmaster.mock.business.scenarios import HAPPY_PATH

    actions = [step[0] for step in HAPPY_PATH]
    assert "search" in actions
    assert "create_order" in actions
    assert "get_order" in actions
    assert "poll_order" in actions
    assert "check_inventory" in actions


# ── Full E2E integration tests will be implemented ──
# when the proxy's unified API handlers are wired up.
# These tests will:
#   1. Start vendor mock server (simulates TicketMaster API)
#   2. Start business mock client (simulates 業務系統)
#   3. Point proxy at vendor mock
#   4. Run business scenarios through proxy
#   5. Verify responses match expected unified API format
