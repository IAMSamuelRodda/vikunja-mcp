#!/usr/bin/env python3
"""Test error messages when dev mode is OFF and secret doesn't exist."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.openbao_secrets import get_mcp_token, build_mcp_secret_path

# Ensure dev mode is OFF
if 'OPENBAO_DEV_MODE' in os.environ:
    del os.environ['OPENBAO_DEV_MODE']

print("Testing with dev mode OFF (no fallback)")
print("=" * 70)

expected_path = build_mcp_secret_path("vikunja")
print(f"\nExpected path: secret/{expected_path}")

try:
    token = get_mcp_token("vikunja", required=True)
    print(f"\n✓ Token retrieved: {token[:20]}...")
except Exception as e:
    print(f"\n✗ Error type: {type(e).__name__}")
    print(f"✗ Error message:\n{e}")

print("\n" + "=" * 70)
