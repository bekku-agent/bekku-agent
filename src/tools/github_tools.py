"""GitHub API integration for publishing content."""

from __future__ import annotations

import os

from github import Github, InputFileContent
import structlog

logger = structlog.get_logger()


def get_github_client() -> Github:
    """Create an authenticated GitHub client."""
    token = os.environ["GITHUB_TOKEN"]
    return Github(token)


def create_gist(
    title: str,
    content: str,
    description: str = "",
    public: bool = True,
) -> str:
    """Create a GitHub Gist and return its URL."""
    gh = get_github_client()
    user = gh.get_user()

    filename = title.lower().replace(" ", "-").replace(":", "") + ".md"
    gist = user.create_gist(
        public=public,
        files={filename: InputFileContent(content)},
        description=description or title,
    )

    logger.info("gist_created", url=gist.html_url, filename=filename)
    return gist.html_url


def commit_to_repo(
    repo_name: str,
    file_path: str,
    content: str,
    commit_message: str,
) -> str:
    """Commit a file to a GitHub repository. Returns the commit SHA."""
    gh = get_github_client()
    user = gh.get_user()
    repo = user.get_repo(repo_name)

    try:
        # Update existing file
        existing = repo.get_contents(file_path)
        result = repo.update_file(
            file_path, commit_message, content, existing.sha
        )
    except Exception:
        # Create new file
        result = repo.create_file(file_path, commit_message, content)

    sha = result["commit"].sha
    logger.info("file_committed", repo=repo_name, path=file_path, sha=sha)
    return sha
