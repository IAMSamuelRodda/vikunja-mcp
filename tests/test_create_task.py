#!/usr/bin/env python3
"""
Quick test script to create a task in Vikunja INBOX using the MCP server's client.
"""
import asyncio
import sys
from src.client.vikunja_client import VikunjaClient

async def main():
    # Initialize client (retrieves credentials from environment variables)
    print("Initializing Vikunja client...")
    try:
        client = VikunjaClient()
        print(f"✓ Client initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize client: {e}")
        return 1

    try:
        # List projects to find INBOX
        print("\nFetching projects...")
        projects = await client.request("GET", "projects")

        inbox_project = None
        for project in projects:
            print(f"  - {project.get('title')} (ID: {project.get('id')})")
            if project.get('title', '').upper() == 'INBOX':
                inbox_project = project

        if not inbox_project:
            print("\n✗ INBOX project not found!")
            return 1

        inbox_id = inbox_project['id']
        print(f"\n✓ Found INBOX (ID: {inbox_id})")

        # Create test task
        print("\nCreating test task...")
        task_data = {
            "title": "Test task from vikunja-mcp server",
            "description": "Created via the vikunja-mcp server"
        }

        task = await client.request("PUT", f"projects/{inbox_id}/tasks", json_data=task_data)
        print(f"✓ Task created successfully!")
        print(f"  ID: {task.get('id')}")
        print(f"  Title: {task.get('title')}")
        print(f"  Project: {task.get('project_id')}")

        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        await client.close()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
