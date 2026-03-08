"""RevenueCat MCP server integration."""

from __future__ import annotations

import os

import httpx
import structlog

logger = structlog.get_logger()

MCP_URL = "https://mcp.revenuecat.ai/mcp"


async def call_mcp_tool(tool_name: str, arguments: dict | None = None) -> dict:
    """Call a tool on the RevenueCat MCP server."""
    api_key = os.environ["REVENUECAT_API_KEY"]

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {},
        },
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(MCP_URL, json=payload, headers=headers)
        resp.raise_for_status()
        result = resp.json()

    logger.info("mcp_tool_called", tool=tool_name, status="success")
    return result.get("result", result)


async def list_projects() -> dict:
    """List all RevenueCat projects."""
    return await call_mcp_tool("list_projects")


async def get_project(project_id: str) -> dict:
    """Get details for a specific RevenueCat project."""
    return await call_mcp_tool("get_project", {"project_id": project_id})


async def list_apps(project_id: str) -> dict:
    """List apps in a RevenueCat project."""
    return await call_mcp_tool("list_apps", {"project_id": project_id})


async def list_products(project_id: str, app_id: str) -> dict:
    """List products for an app."""
    return await call_mcp_tool(
        "list_products", {"project_id": project_id, "app_id": app_id}
    )


async def list_entitlements(project_id: str) -> dict:
    """List entitlements in a project."""
    return await call_mcp_tool("list_entitlements", {"project_id": project_id})


async def list_offerings(project_id: str) -> dict:
    """List offerings in a project."""
    return await call_mcp_tool("list_offerings", {"project_id": project_id})
