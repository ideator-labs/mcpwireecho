"""DialectClass and classify logic for MCP protocol-version probes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional

DialectClass = Literal["old_only", "echo_negotiator", "discover_ok"]

OFFERED_VERSION = "2026-07-28"
OLD_VERSION = "2025-06-18"
METHOD_NOT_FOUND = -32601


@dataclass(frozen=True)
class DiscoverOutcome:
    ok: bool
    error_code: Optional[int] = None
    supported_versions: tuple[str, ...] = ()


@dataclass
class ProbeReport:
    target: str
    class_: DialectClass
    offered_version: str
    initialize_echo: Optional[str]
    discover: DiscoverOutcome
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "class": self.class_,
            "offeredVersion": self.offered_version,
            "initializeEcho": self.initialize_echo,
            "discover": {
                "ok": self.discover.ok,
                "errorCode": self.discover.error_code,
                "supportedVersions": list(self.discover.supported_versions),
            },
            "evidence": list(self.evidence),
        }


def classify(
    target: str,
    offered_version: str,
    initialize_echo: Optional[str],
    discover: DiscoverOutcome,
) -> ProbeReport:
    """Map initialize + discover evidence to a DialectClass.

    discover_ok wins when discover reports the offered version.
    Echoing the offered version on initialize alone is echo_negotiator.
    Returning an older initialize version with no discover is old_only.
    """
    evidence: list[str] = []
    evidence.append(f"offered={offered_version}")
    evidence.append(f"initializeEcho={initialize_echo!r}")
    evidence.append(
        f"discover.ok={discover.ok} errorCode={discover.error_code} "
        f"supportedVersions={list(discover.supported_versions)}"
    )

    if discover.ok and offered_version in discover.supported_versions:
        class_: DialectClass = "discover_ok"
        evidence.append("rule: discover lists offered version -> discover_ok")
    elif (
        initialize_echo == offered_version
        and not discover.ok
        and discover.error_code == METHOD_NOT_FOUND
    ):
        class_ = "echo_negotiator"
        evidence.append(
            "rule: initialize echoed offered version but discover missing -> echo_negotiator"
        )
    elif (
        initialize_echo is not None
        and initialize_echo != offered_version
        and not discover.ok
        and discover.error_code == METHOD_NOT_FOUND
    ):
        class_ = "old_only"
        evidence.append(
            "rule: initialize kept older version and discover missing -> old_only"
        )
    else:
        # Ambiguous wire. Prefer old_only when discover is absent and echo is not offered.
        if not discover.ok and initialize_echo == offered_version:
            class_ = "echo_negotiator"
            evidence.append("fallback: echoed offered version without discover -> echo_negotiator")
        elif not discover.ok:
            class_ = "old_only"
            evidence.append("fallback: no discover support -> old_only")
        else:
            class_ = "discover_ok"
            evidence.append("fallback: discover ok without listed version -> discover_ok")

    return ProbeReport(
        target=target,
        class_=class_,
        offered_version=offered_version,
        initialize_echo=initialize_echo,
        discover=discover,
        evidence=evidence,
    )
