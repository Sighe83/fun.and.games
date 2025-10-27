"""Aula MCP Server.

This module exposes an MCP (Model Context Protocol) server that wraps the
existing :class:`AulaClient` helper used by the Flask web application. The
server provides a minimal tool surface that allows clients to log in, inspect
children connected to the account and fetch weekly notes using the Aula API.

The implementation intentionally keeps state on the process level. This keeps
things straightforward for local usage which is currently the main deployment
scenario for this project. If needed, the implementation can be extended to
handle multiple concurrent clients by maintaining per-connection state inside a
lookup keyed by the MCP connection metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from aula_client import AulaClient

try:  # pragma: no cover - Optional dependency for MCP runtime
    from mcp.server.fastmcp import FastMCPServer
    from mcp.server.stdio import stdio_server
except ModuleNotFoundError as exc:  # pragma: no cover - keep import error informative
    raise ModuleNotFoundError(
        "The 'mcp' package is required to run the Aula MCP server. Install it "
        "with 'pip install mcp'."
    ) from exc


@dataclass
class AulaState:
    """Mutable state used by the MCP tools."""

    client: Optional[AulaClient] = None

    def ensure_client(self) -> AulaClient:
        """Return the active :class:`AulaClient` instance.

        Raises:
            RuntimeError: If no user is logged in.
        """

        if not self.client or not self.client.logged_in:
            raise RuntimeError(
                "Ingen aktiv Aula session. Kør 'login' værktøjet først."
            )
        return self.client


server = FastMCPServer("aula")
state = AulaState()


@server.tool()
async def login(username: str, password: str) -> Dict[str, Any]:
    """Authenticate against Aula using UNI-Login credentials.

    Returns a simple status dictionary that reflects whether the credentials
    were accepted by Aula.
    """

    client = AulaClient()
    success = client.login(username, password)
    if success:
        state.client = client
        return {
            "success": True,
            "message": "Login lykkedes",
        }

    return {
        "success": False,
        "message": "Login mislykkedes. Tjek brugernavn og adgangskode.",
    }


@server.tool()
async def logout() -> Dict[str, Any]:
    """Clear the cached Aula session."""

    if state.client:
        state.client = None
        return {"success": True, "message": "Logget ud."}

    return {"success": False, "message": "Ingen aktiv session."}


@server.tool()
async def list_children() -> Dict[str, Any]:
    """Return information about the children attached to the Aula profile."""

    client = state.ensure_client()
    return {
        "success": True,
        "children": client.get_children_info(),
    }


@server.tool()
async def get_weekly_notes(week_offset: int = 0) -> Dict[str, Any]:
    """Fetch weekly notes for the requested week.

    Args:
        week_offset: Week offset relative to the current week. ``0`` is the
            current week and ``1`` is next week.
    """

    client = state.ensure_client()
    notes = client.get_weekly_notes(week_offset=week_offset)
    if not notes:
        return {
            "success": False,
            "message": "Ingen noter fundet for den angivne uge.",
        }

    return {
        "success": True,
        "notes": notes,
    }


def main() -> None:
    """Entrypoint used when running the module as a script."""

    handler_factory = getattr(server, "create_handler", None)
    if handler_factory is None:
        handler_factory = getattr(server, "create_app", None)
    if handler_factory is None:
        raise RuntimeError(
            "Inkompatibel MCP version: kunne ikke finde en handler fabrik."  # noqa: E501
        )

    stdio_server.run(handler_factory())


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    main()
