#!/usr/bin/env python3
"""Vendor Validation Script — runs in CI to enforce vendor conventions.

Usage:
    python scripts/validate-vendor.py [vendor_name]

If vendor_name is provided, validates that vendor only.
If omitted, validates ALL vendors under plugins/.

Exit code 0 = all checks passed. Non-zero = violation found.
Designed to be called from GitHub Actions CI.
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"

# ── Vendor naming convention ──
# Directory must be "vendor_<name>", e.g. "vendor_ticketmaster"
VENDOR_DIR_PREFIX = "vendor_"


class ValidationError(Exception):
    pass


def fail(msg: str):
    print(f"  ❌ {msg}")
    raise ValidationError(msg)


def ok(msg: str):
    print(f"  ✅ {msg}")


def warn(msg: str):
    print(f"  ⚠️  {msg}")


# ═══════════════════════════════════════════════════════════════
# A. Directory Structure Check
# ═══════════════════════════════════════════════════════════════

def check_directory_structure(vendor_dir: Path) -> list[str]:
    """Check that all required directories exist."""
    errors = []

    required_dirs = [
        vendor_dir,
        vendor_dir / "mock",
        vendor_dir / "mock" / "vendor",
        vendor_dir / "mock" / "business",
        vendor_dir / "fixtures",
        vendor_dir / "schema",
        vendor_dir / "schema" / "migrations",
        vendor_dir / "tests",
    ]

    for d in required_dirs:
        if d.is_dir():
            ok(f"Directory exists: {d.relative_to(REPO_ROOT)}")
        else:
            errors.append(f"Missing directory: {d.relative_to(REPO_ROOT)}")

    return errors


# ═══════════════════════════════════════════════════════════════
# B. Required Files Check
# ═══════════════════════════════════════════════════════════════

def check_required_files(vendor_dir: Path) -> list[str]:
    """Check that all required files exist."""
    errors = []

    required_files = [
        vendor_dir / "plugin.py",
        vendor_dir / "mock" / "vendor" / "server.py",
        vendor_dir / "mock" / "business" / "server.py",
        vendor_dir / "mock" / "business" / "scenarios.py",
        vendor_dir / "fixtures" / "normal.json",
        vendor_dir / "fixtures" / "empty.json",
        vendor_dir / "fixtures" / "malformed.json",
        vendor_dir / "tests" / "test_contract.py",
        vendor_dir / "tests" / "test_vendor_mock.py",
        vendor_dir / "tests" / "test_business_mock.py",
        vendor_dir / "tests" / "test_integration.py",
    ]

    for f in required_files:
        if f.is_file():
            ok(f"File exists: {f.relative_to(REPO_ROOT)}")
        else:
            errors.append(f"Missing file: {f.relative_to(REPO_ROOT)}")

    return errors


# ═══════════════════════════════════════════════════════════════
# C. Plugin Contract Check (static analysis)
# ═══════════════════════════════════════════════════════════════

def check_plugin_contract(vendor_name: str, vendor_dir: Path) -> list[str]:
    """Check that plugin.py implements all required methods and properties."""
    errors = []
    plugin_path = vendor_dir / "plugin.py"

    if not plugin_path.is_file():
        return ["plugin.py not found — cannot check contract"]

    content = plugin_path.read_text()

    # Check required attributes
    required_attrs = [
        ("plugin_id", f'plugin_id = "{vendor_name}"'),
        ("plugin_name", "plugin_name = "),
        ("version", "version = "),
    ]

    for attr_name, pattern in required_attrs:
        if pattern in content:
            ok(f"Attribute defined: {attr_name}")
        else:
            errors.append(f"Missing attribute: {attr_name}")

    # Check required methods
    required_methods = [
        "async def start",
        "async def stop",
        "async def health",
        "def get_mock_server",
        "def get_business_mock_server",
        "def get_fixtures",
        "async def run_tests",
    ]

    for method in required_methods:
        if method in content:
            ok(f"Method defined: {method}")
        else:
            errors.append(f"Missing method: {method}")

    # Check data isolation properties
    isolation_props = [
        ("db_schema", "def db_schema"),
        ("redis_prefix", "def redis_prefix"),
    ]

    for prop_name, pattern in isolation_props:
        if pattern in content:
            ok(f"Isolation property: {prop_name}")
        else:
            errors.append(f"Missing isolation property: {prop_name}")

    # Check business API handlers
    business_handlers = [
        "handle_search",
        "handle_create_order",
        "handle_get_order",
        "handle_poll_order",
        "handle_inventory",
    ]

    for handler in business_handlers:
        if handler in content:
            ok(f"Business handler: {handler}")
        else:
            warn(f"Business handler not yet implemented: {handler} — implement before production")

    return errors


# ═══════════════════════════════════════════════════════════════
# D. Fixtures Validation
# ═══════════════════════════════════════════════════════════════

def check_fixtures(vendor_dir: Path) -> list[str]:
    """Validate fixture JSON files are valid JSON."""
    errors = []
    fixtures_dir = vendor_dir / "fixtures"

    for f in sorted(fixtures_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            ok(f"Valid JSON: {f.name} ({len(json.dumps(data))} bytes)")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in {f.name}: {e}")

    # Check at least 3 fixtures exist
    json_files = list(fixtures_dir.glob("*.json"))
    if len(json_files) >= 3:
        ok(f"Fixture count: {len(json_files)} (≥3)")
    else:
        errors.append(f"Only {len(json_files)} fixtures found (need ≥3)")

    return errors


# ═══════════════════════════════════════════════════════════════
# E. Mock Server Smoke Test
# ═══════════════════════════════════════════════════════════════

def check_mock_servers(vendor_dir: Path) -> list[str]:
    """Verify mock servers can be imported (not necessarily started)."""
    errors = []

    # Check vendor mock
    vendor_mock = vendor_dir / "mock" / "vendor" / "server.py"
    if vendor_mock.is_file():
        try:
            # Syntax check
            compile(vendor_mock.read_text(), str(vendor_mock), "exec")
            ok("Vendor mock server: syntax OK")
        except SyntaxError as e:
            errors.append(f"Vendor mock server syntax error: {e}")

    # Check business mock
    business_mock = vendor_dir / "mock" / "business" / "server.py"
    if business_mock.is_file():
        try:
            compile(business_mock.read_text(), str(business_mock), "exec")
            ok("Business mock server: syntax OK")
        except SyntaxError as e:
            errors.append(f"Business mock server syntax error: {e}")

    return errors


# ═══════════════════════════════════════════════════════════════
# F. Schema Migration Isolation
# ═══════════════════════════════════════════════════════════════

def check_schema_isolation(vendor_name: str, vendor_dir: Path) -> list[str]:
    """Check that migrations only target the vendor's own schema."""
    errors = []
    migrations_dir = vendor_dir / "schema" / "migrations"

    if not migrations_dir.is_dir():
        errors.append("No migrations directory — create schema/migrations/ with at least an empty __init__.py")
        return errors

    expected_schema = f"plugin_{vendor_name}"
    migration_files = list(migrations_dir.glob("*.sql")) + list(migrations_dir.glob("*.py"))

    if not migration_files:
        warn("No migration files found — add at least an initial migration")
        return errors

    for mf in migration_files:
        content = mf.read_text()
        # Check for foreign schema references (heuristic)
        # Look for schema names that look like other vendor schemas
        import re
        schemas = set(re.findall(r'plugin_(\w+)', content))
        foreign = schemas - {vendor_name}
        if foreign:
            errors.append(
                f"{mf.name} references foreign schemas: {foreign}. "
                f"Each vendor must only use plugin_{vendor_name}"
            )
        else:
            ok(f"Schema isolation OK: {mf.name} only uses plugin_{vendor_name}")

    return errors


# ═══════════════════════════════════════════════════════════════
# G. Entry Point Registration
# ═══════════════════════════════════════════════════════════════

def check_entry_point(vendor_name: str) -> list[str]:
    """Check pyproject.toml has correct entry_point registration."""
    errors = []
    pyproject = REPO_ROOT / "pyproject.toml"

    if not pyproject.is_file():
        return ["pyproject.toml not found"]

    content = pyproject.read_text()

    # Check the vendor is registered
    expected_entry = f'{vendor_name} = "vendor_{vendor_name}.plugin:'
    if expected_entry in content:
        ok(f"Entry point registered: {vendor_name}")
    else:
        errors.append(
            f"Entry point not found in pyproject.toml. "
            f"Expected: {expected_entry}<ClassName>\""
        )

    return errors


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def discover_vendors() -> list[str]:
    """Find all vendor directories under plugins/."""
    vendors = []
    if not PLUGINS_DIR.is_dir():
        print("No plugins/ directory found")
        return vendors

    for d in sorted(PLUGINS_DIR.iterdir()):
        if d.is_dir() and d.name.startswith(VENDOR_DIR_PREFIX):
            vendor_name = d.name[len(VENDOR_DIR_PREFIX):]  # strip "vendor_"
            vendors.append(vendor_name)

    return vendors


def validate_vendor(vendor_name: str) -> bool:
    """Run all checks for a single vendor. Returns True if all passed."""
    vendor_dir = PLUGINS_DIR / f"{VENDOR_DIR_PREFIX}{vendor_name}"

    print(f"\n{'='*60}")
    print(f"Validating vendor: {vendor_name}")
    print(f"Directory: {vendor_dir.relative_to(REPO_ROOT)}")
    print(f"{'='*60}")

    checks = [
        ("A. Directory Structure", check_directory_structure(vendor_dir)),
        ("B. Required Files", check_required_files(vendor_dir)),
        ("C. Plugin Contract", check_plugin_contract(vendor_name, vendor_dir)),
        ("D. Fixtures", check_fixtures(vendor_dir)),
        ("E. Mock Servers", check_mock_servers(vendor_dir)),
        ("F. Schema Isolation", check_schema_isolation(vendor_name, vendor_dir)),
        ("G. Entry Point", check_entry_point(vendor_name)),
    ]

    all_errors = []
    for check_name, errors in checks:
        if errors:
            print(f"\n  [{check_name}] FAILED:")
            for e in errors:
                print(f"    ❌ {e}")
            all_errors.extend(errors)

    if all_errors:
        print(f"\n  ❌ {vendor_name}: {len(all_errors)} violation(s) found")
        return False
    else:
        print(f"\n  ✅ {vendor_name}: ALL CHECKS PASSED")
        return True


def main():
    args = sys.argv[1:]

    if args:
        vendor_name = args[0]
        vendors = [vendor_name] if vendor_name else []
    else:
        vendors = discover_vendors()

    if not vendors:
        print("No vendors found under plugins/")
        sys.exit(0)

    print(f"Found {len(vendors)} vendor(s): {', '.join(vendors)}")

    all_passed = True
    for v in vendors:
        if not validate_vendor(v):
            all_passed = False

    if all_passed:
        print(f"\n{'='*60}")
        print("🎉 ALL VENDORS VALIDATED SUCCESSFULLY")
        sys.exit(0)
    else:
        print(f"\n{'='*60}")
        print("❌ VALIDATION FAILED — fix the violations above before merging")
        sys.exit(1)


if __name__ == "__main__":
    main()
