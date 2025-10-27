"""MCP server exposing Aula tools.

This module provides a simple Model Context Protocol (MCP) server that
wraps the existing :class:`AulaClient` utilities.  The server exposes a
handful of stateless tools that authenticate with Aula.dk for each call
and return structured JSON payloads that are easy for an MCP client to
consume.

Usage:

    python -m mcp_server

The module uses the ``fastmcp`` helper library which implements the MCP
protocol over stdio.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from aula_client import AulaClient


server = FastMCP("aula-service")


@dataclass
class WeeklyNotesRequest:
    """Request payload for retrieving weekly notes."""

    username: str
    password: str
    week_offset: int = 0


@dataclass
class ChildrenInfoRequest:
    """Request payload for retrieving children information."""

    username: str
    password: str


def _create_client(username: str, password: str) -> AulaClient:
    """Authenticate a new :class:`AulaClient` instance.

    Args:
        username: UNI-Login username.
        password: UNI-Login password.

    Returns:
        An authenticated ``AulaClient`` instance.

    Raises:
        ValueError: If authentication fails.
    """

    client = AulaClient()
    if not client.login(username, password):
        raise ValueError("Login mislykkedes. Kontroller brugernavn og adgangskode.")
    return client


@server.tool()
def get_weekly_notes(request: WeeklyNotesRequest) -> Dict[str, Any]:
    """Retrieve weekly notes for the specified week.

    Args:
        request: ``WeeklyNotesRequest`` payload containing credentials and
            week offset.  ``week_offset`` follows the same semantics as
            :meth:`AulaClient.get_weekly_notes`.

    Returns:
        A JSON-serialisable dictionary describing the requested week,
        including the list of calendar events.  The returned value mirrors
        the structure produced by :meth:`AulaClient.get_weekly_notes`.
    """

    client = _create_client(request.username, request.password)
    week_data = client.get_weekly_notes(week_offset=request.week_offset)
    if week_data is None:
        raise ValueError("Kunne ikke hente ugenoter for den ønskede uge.")
    return week_data


@server.tool()
def get_children_info(request: ChildrenInfoRequest) -> List[Dict[str, Optional[str]]]:
    """Retrieve information about the authenticated user's children."""

    client = _create_client(request.username, request.password)
    return client.get_children_info()


def main() -> None:
    """Entry point for running the MCP server over stdio."""

    server.run()


if __name__ == "__main__":
    main()
