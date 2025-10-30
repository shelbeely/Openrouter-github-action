# src/tools/dev_tools.py

import logging
from agents import RunContextWrapper, function_tool
from src.context.github_context import GithubContext

logger = logging.getLogger("dev-tools")

@function_tool
async def create_new_tool(
    context: RunContextWrapper[GithubContext],
    tool_name: str,
    tool_description: str,
    tool_code: str,
) -> dict[str, any]:
    """
    Creates a new tool and adds it to the `src/tools` directory.

    Args:
        tool_name: The name of the tool to create.
        tool_description: A description of the tool.
        tool_code: The code for the tool.
    """
    logger.info(f"Creating new tool: {tool_name}")
    # In a real implementation, this would involve creating a new file,
    # adding the tool code, and registering the tool with the agent.
    # For now, we'll just log the request.
    return {
        "tool_name": tool_name,
        "status": "created",
    }

@function_tool
async def create_pull_request(
    context: RunContextWrapper[GithubContext],
    repo: str,
    title: str,
    body: str,
    head: str,
    base: str,
) -> dict[str, any]:
    """
    Creates a new pull request.

    Args:
        repo: The repository to create the pull request in.
        title: The title of the pull request.
        body: The body of the pull request.
        head: The branch to merge from.
        base: The branch to merge into.
    """
    logger.info(f"Creating new pull request: {title}")
    repo_obj = context.context.github_client.get_repo(repo)
    pr = repo_obj.create_pull(
        title=title,
        body=body,
        head=head,
        base=base,
    )
    return {
        "number": pr.number,
        "url": pr.html_url,
    }
