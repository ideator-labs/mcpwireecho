"""Probe a FakeServer by offering protocolVersion 2026-07-28."""

from __future__ import annotations

from typing import Any, Optional

from dialect import (
    OFFERED_VERSION,
    DiscoverOutcome,
    ProbeReport,
    classify,
)
from servers import FakeServer


def _initialize_echo(response: dict[str, Any]) -> Optional[str]:
    result = response.get("result") or {}
    version = result.get("protocolVersion")
    return version if isinstance(version, str) else None


def _discover_outcome(response: dict[str, Any]) -> DiscoverOutcome:
    if "result" in response and isinstance(response["result"], dict):
        versions = response["result"].get("supportedVersions") or []
        if not isinstance(versions, list):
            versions = []
        clean = tuple(v for v in versions if isinstance(v, str))
        return DiscoverOutcome(ok=True, supported_versions=clean)
    error = response.get("error") or {}
    code = error.get("code")
    return DiscoverOutcome(
        ok=False,
        error_code=code if isinstance(code, int) else None,
    )


def probe(server: FakeServer, offered_version: str = OFFERED_VERSION) -> ProbeReport:
    init_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": offered_version,
            "capabilities": {},
            "clientInfo": {"name": "mcpwireecho", "version": "0.1"},
        },
    }
    discover_msg = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "server/discover",
        "params": {},
    }
    init_resp = server.handle(init_msg)
    discover_resp = server.handle(discover_msg)
    echo = _initialize_echo(init_resp)
    discover = _discover_outcome(discover_resp)
    return classify(
        target=server.name,
        offered_version=offered_version,
        initialize_echo=echo,
        discover=discover,
    )
