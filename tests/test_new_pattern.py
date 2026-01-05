#!/usr/bin/env python3
"""
Test script to verify the new Arc Forge secret path pattern.

Tests:
1. build_mcp_secret_path() generates correct paths
2. Auto-detection of identifier works
3. Dev mode fallback works
4. New pattern matches expected format
"""

import os
import sys
import socket

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.openbao_secrets import (
    build_mcp_secret_path,
    _get_git_email,
    _detect_identifier,
    get_mcp_token,
    ARC_CLIENT,
    ARC_ENVIRONMENT
)


def test_path_building():
    """Test the path building function."""
    print("=" * 70)
    print("TEST 1: Path Building")
    print("=" * 70)

    # Get expected values
    git_email = _get_git_email()
    hostname = socket.gethostname().split('.')[0]

    print(f"\nEnvironment:")
    print(f"  ARC_CLIENT: {ARC_CLIENT}")
    print(f"  ARC_ENVIRONMENT: {ARC_ENVIRONMENT}")
    print(f"  Git email: {git_email}")
    print(f"  Hostname: {hostname}")

    # Test Vikunja (user-scoped)
    vikunja_path = build_mcp_secret_path("vikunja")
    print(f"\nVikunja path (auto-detected):")
    print(f"  {vikunja_path}")

    expected_identifier = git_email.split('@')[0] if git_email else os.getenv("USER", "default")
    expected_path = f"{ARC_CLIENT}/{ARC_ENVIRONMENT}-mcp-vikunja-{expected_identifier}"
    print(f"  Expected: {expected_path}")
    print(f"  Match: {'✓' if vikunja_path == expected_path else '✗'}")

    # Test Joplin (machine-scoped)
    joplin_path = build_mcp_secret_path("joplin")
    print(f"\nJoplin path (auto-detected):")
    print(f"  {joplin_path}")

    expected_joplin = f"{ARC_CLIENT}/{ARC_ENVIRONMENT}-mcp-joplin-{hostname}"
    print(f"  Expected: {expected_joplin}")
    print(f"  Match: {'✓' if joplin_path == expected_joplin else '✗'}")

    # Test explicit identifier override
    custom_path = build_mcp_secret_path("vikunja", identifier="kayla")
    print(f"\nCustom identifier (kayla):")
    print(f"  {custom_path}")
    print(f"  Expected: {ARC_CLIENT}/{ARC_ENVIRONMENT}-mcp-vikunja-kayla")
    print(f"  Match: {'✓' if custom_path == f'{ARC_CLIENT}/{ARC_ENVIRONMENT}-mcp-vikunja-kayla' else '✗'}")


def test_identifier_detection():
    """Test the identifier auto-detection."""
    print("\n" + "=" * 70)
    print("TEST 2: Identifier Detection")
    print("=" * 70)

    vikunja_id = _detect_identifier("vikunja")
    joplin_id = _detect_identifier("joplin")
    default_id = _detect_identifier("unknown_service")

    print(f"\nVikunja (user-scoped): {vikunja_id}")
    print(f"Joplin (machine-scoped): {joplin_id}")
    print(f"Unknown service (default): {default_id}")


def test_dev_mode():
    """Test dev mode fallback."""
    print("\n" + "=" * 70)
    print("TEST 3: Dev Mode Fallback")
    print("=" * 70)

    # Check if dev mode is enabled
    dev_mode = os.getenv("OPENBAO_DEV_MODE", "").lower() in ("1", "true", "yes")
    print(f"\nOPENBAO_DEV_MODE: {dev_mode}")

    # Check if token env vars are set
    vikunja_token_env = os.getenv("VIKUNJA_TOKEN")
    print(f"VIKUNJA_TOKEN set: {bool(vikunja_token_env)}")

    if dev_mode and vikunja_token_env:
        print("\n✓ Dev mode is enabled and token is available")
        print("  Attempting to get token with dev fallback...")
        try:
            token = get_mcp_token("vikunja", dev_fallback="VIKUNJA_TOKEN", required=True)
            print(f"  Token retrieved: {token[:20]}..." if token else "  Failed")
        except Exception as e:
            print(f"  Error: {e}")
    else:
        print("\n! Dev mode not fully configured")
        print("  To test dev mode fallback, run:")
        print("    export OPENBAO_DEV_MODE=1")
        print("    export VIKUNJA_TOKEN=your-token-here")


def test_full_path_format():
    """Test that the full path format is correct."""
    print("\n" + "=" * 70)
    print("TEST 4: Full Path Format Validation")
    print("=" * 70)

    path = build_mcp_secret_path("vikunja")
    parts = path.split('/')

    print(f"\nPath: secret/{path}")
    print(f"Parts: {parts}")
    print(f"  [0] Namespace: {parts[0]}")
    if len(parts) > 1:
        env_parts = parts[1].split('-', 1)
        print(f"  [1] Environment prefix: {env_parts[0]}")
        print(f"  [1] Remaining: {env_parts[1] if len(env_parts) > 1 else 'N/A'}")

    # Validate format: {client}/{environment}-mcp-{service}-{identifier}
    valid = (
        len(parts) == 2 and
        parts[0] == ARC_CLIENT and
        parts[1].startswith(f"{ARC_ENVIRONMENT}-mcp-")
    )
    print(f"\nFormat validation: {'✓ Valid' if valid else '✗ Invalid'}")


if __name__ == "__main__":
    print("\nArc Forge Secret Path Pattern Test Suite")
    print("=" * 70)

    test_path_building()
    test_identifier_detection()
    test_dev_mode()
    test_full_path_format()

    print("\n" + "=" * 70)
    print("Tests complete!")
    print("=" * 70)
