"""Three in-process fake MCP servers with distinct dialect behavior."""

from __future__ import annotations

from typing import Any

from dialect import METHOD_NOT_FOUND, OFFERED_VERSION, OLD_VERSION


def _rpc_error(code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "error": {"code": code, "message": message}}


def _rpc_result(result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "result": result}


class FakeServer:
    name: str

    def handle(self, message: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class OldOnlyServer(FakeServer):
    """Speaks only the older revision. Rejects server/discover."""

    name = "old_only"

    def handle(self, message: dict[str, Any]) -> dict[str, Any]:
        method = message.get("method")
        if method == "initialize":
            return _rpc_result(
                {
                    "protocolVersion": OLD_VERSION,
                    "capabilities": {},
                    "serverInfo": {"name": self.name, "version": "0.1"},
                }
            )
        if method == "server/discover":
            return _rpc_error(METHOD_NOT_FOUND, "Method not found")
        return _rpc_error(METHOD_NOT_FOUND, f"unknown method {method}")


class EchoNegotiatorServer(FakeServer):
    """Echoes whatever protocolVersion the client offered. Still no discover."""

    name = "echo_negotiator"

    def handle(self, message: dict[str, Any]) -> dict[str, Any]:
        method = message.get("method")
        if method == "initialize":
            params = message.get("params") or {}
            offered = params.get("protocolVersion") or OLD_VERSION
            return _rpc_result(
                {
                    "protocolVersion": offered,
                    "capabilities": {},
                    "serverInfo": {"name": self.name, "version": "0.1"},
                }
            )
        if method == "server/discover":
            return _rpc_error(METHOD_NOT_FOUND, "Method not found")
        return _rpc_error(METHOD_NOT_FOUND, f"unknown method {method}")


class DiscoverOkServer(FakeServer):
    """Implements server/discover with supportedVersions including 2026-07-28."""

    name = "discover_ok"

    def handle(self, message: dict[str, Any]) -> dict[str, Any]:
        method = message.get("method")
        if method == "initialize":
            return _rpc_result(
                {
                    "protocolVersion": OFFERED_VERSION,
                    "capabilities": {"discover": True},
                    "serverInfo": {"name": self.name, "version": "0.1"},
                }
            )
        if method == "server/discover":
            return _rpc_result(
                {
                    "supportedVersions": [OLD_VERSION, OFFERED_VERSION],
                    "serverInfo": {"name": self.name, "version": "0.1"},
                }
            )
        return _rpc_error(METHOD_NOT_FOUND, f"unknown method {method}")


FIXTURES: dict[str, FakeServer] = {
    "old_only": OldOnlyServer(),
    "echo_negotiator": EchoNegotiatorServer(),
    "discover_ok": DiscoverOkServer(),
}
