"""Buffer API integration for social media distribution."""

from __future__ import annotations

import os

import httpx
import structlog

logger = structlog.get_logger()

BUFFER_API_URL = "https://api.buffer.com"


def _get_token() -> str | None:
    return os.environ.get("BUFFER_API_TOKEN")


async def _graphql(query: str, variables: dict | None = None) -> dict:
    """Execute a Buffer GraphQL request."""
    token = _get_token()
    if not token:
        raise ValueError("BUFFER_API_TOKEN not set")

    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            BUFFER_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            json=payload,
        )
        if resp.status_code != 200:
            logger.error("buffer_api_error", status=resp.status_code, body=resp.text[:500])
            resp.raise_for_status()
        return resp.json()


async def get_organization_id() -> str | None:
    """Fetch the first organization ID from Buffer."""
    data = await _graphql("""
        query GetOrganizations {
            account {
                organizations {
                    id
                }
            }
        }
    """)

    orgs = data.get("data", {}).get("account", {}).get("organizations", [])
    if orgs:
        org_id = orgs[0]["id"]
        logger.info("buffer_org_found", org_id=org_id)
        return org_id

    logger.warning("buffer_no_orgs")
    return None


async def get_channels(org_id: str) -> list[dict]:
    """Fetch connected channels from Buffer."""
    data = await _graphql("""
        query GetChannels($input: ChannelsInput!) {
            channels(input: $input) {
                id
                name
                service
            }
        }
    """, variables={"input": {"organizationId": org_id}})

    channels = data.get("data", {}).get("channels", [])
    logger.info("buffer_channels_fetched", count=len(channels), channels=[c["service"] for c in channels])
    return channels


async def create_draft(channel_id: str, text: str) -> dict | None:
    """Create a queued post on Buffer for a specific channel."""
    data = await _graphql("""
        mutation CreatePost($input: CreatePostInput!) {
            createPost(input: $input) {
                ... on PostActionSuccess {
                    post {
                        id
                        text
                    }
                }
                ... on MutationError {
                    message
                }
            }
        }
    """, variables={
        "input": {
            "text": text,
            "channelId": channel_id,
            "schedulingType": "automatic",
            "mode": "addToQueue",
        }
    })

    result = data.get("data", {}).get("createPost", {})

    if "post" in result:
        logger.info("buffer_draft_created", channel=channel_id, post_id=result["post"]["id"])
        return result["post"]
    else:
        error = result.get("message", str(data.get("errors", "Unknown error")))
        logger.error("buffer_draft_failed", channel=channel_id, error=error)
        return None


async def distribute_social(
    social_posts: dict[str, str],
    published_url: str,
) -> list[str]:
    """Send social posts to Buffer for all connected channels."""
    token = _get_token()
    if not token:
        logger.info("buffer_skipped_no_token")
        return []

    if not social_posts:
        return []

    # Get org ID first
    try:
        org_id = await get_organization_id()
        if not org_id:
            return []
    except Exception as e:
        logger.error("buffer_org_error", error=str(e))
        return []

    # Get connected channels
    try:
        channels = await get_channels(org_id)
    except Exception as e:
        logger.error("buffer_channels_error", error=str(e))
        return []

    if not channels:
        logger.warning("buffer_no_channels")
        return []

    # Map platform names to Buffer service names
    # X disabled — focusing on LinkedIn for now
    platform_to_service = {
        "linkedin": "linkedin",
    }

    post_ids = []
    for platform, text in social_posts.items():
        service = platform_to_service.get(platform)
        if not service:
            continue

        text = text.replace("[GIST_URL]", published_url)

        channel = next((c for c in channels if c["service"] == service), None)
        if not channel:
            logger.warning("buffer_channel_not_found", service=service)
            continue

        try:
            result = await create_draft(channel["id"], text)
            if result:
                post_ids.append(result["id"])
        except Exception as e:
            logger.error("buffer_post_error", service=service, error=str(e))

    logger.info("buffer_distribution_done", posts_created=len(post_ids))
    return post_ids
