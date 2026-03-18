"""Buffer API integration for social media distribution."""

from __future__ import annotations

import os

import httpx
import structlog

logger = structlog.get_logger()

BUFFER_API_URL = "https://api.buffer.com"


def _get_token() -> str | None:
    """Get Buffer API token from environment."""
    return os.environ.get("BUFFER_API_TOKEN")


async def get_channels() -> list[dict]:
    """Fetch connected channels (X, LinkedIn, etc.) from Buffer."""
    token = _get_token()
    if not token:
        logger.warning("buffer_token_missing")
        return []

    query = """
    query GetChannels {
        channels {
            id
            name
            service
            avatar
        }
    }
    """

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            BUFFER_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            json={"query": query},
        )
        logger.info("buffer_channels_response", status=resp.status_code, body=resp.text[:500])
        resp.raise_for_status()
        data = resp.json()

    channels = data.get("data", {}).get("channels", [])
    logger.info("buffer_channels_fetched", count=len(channels))
    return channels


async def create_draft(channel_id: str, text: str) -> dict | None:
    """Create a draft post on Buffer for a specific channel.

    Uses 'queue' mode so MK can review in Buffer before publishing.
    """
    token = _get_token()
    if not token:
        logger.warning("buffer_token_missing")
        return None

    query = """
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
    """

    variables = {
        "input": {
            "text": text,
            "channelId": channel_id,
            "schedulingType": "automatic",
            "mode": "queue",
        }
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            BUFFER_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            json={"query": query, "variables": variables},
        )
        logger.info("buffer_create_response", status=resp.status_code, body=resp.text[:500])
        resp.raise_for_status()
        data = resp.json()

    result = data.get("data", {}).get("createPost", {})

    if "post" in result:
        logger.info("buffer_draft_created", channel=channel_id, post_id=result["post"]["id"])
        return result["post"]
    else:
        error = result.get("message", "Unknown error")
        logger.error("buffer_draft_failed", channel=channel_id, error=error)
        return None


async def distribute_social(social_posts: dict[str, str], published_url: str) -> list[str]:
    """Send social posts to Buffer for all connected channels.

    Replaces [GIST_URL] with the actual published URL.
    Returns list of Buffer post IDs created.
    """
    token = _get_token()
    if not token:
        logger.info("buffer_skipped_no_token")
        return []

    if not social_posts:
        return []

    # Get connected channels
    try:
        channels = await get_channels()
    except Exception as e:
        logger.error("buffer_channels_error", error=str(e))
        return []
    if not channels:
        logger.warning("buffer_no_channels")
        return []

    # Map platform names to Buffer service names
    platform_to_service = {
        "x": "twitter",
        "linkedin": "linkedin",
    }

    post_ids = []
    for platform, text in social_posts.items():
        service = platform_to_service.get(platform)
        if not service:
            continue

        # Replace placeholder with real URL
        text = text.replace("[GIST_URL]", published_url)

        # Find matching channel
        channel = next((c for c in channels if c["service"] == service), None)
        if not channel:
            logger.warning("buffer_channel_not_found", service=service)
            continue

        result = await create_draft(channel["id"], text)
        if result:
            post_ids.append(result["id"])

    logger.info("buffer_distribution_done", posts_created=len(post_ids))
    return post_ids
