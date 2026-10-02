# AGENTS.md - McpWireEcho

Cold-start handoff for a coding agent with no prior context.

## Claim proved

Offering `protocolVersion` `2026-07-28` classifies a target as `old_only`, `echo_negotiator`, or `discover_ok`. Echoing the requested version on initialize is not the same as implementing `server/discover`.

Evidence from `bash demo.sh`:

1. PATH A: `old_only` fixture returns initialize `protocolVersion` `2025-06-18` and discover JSON-RPC `-32601`. Class `old_only`.
2. PATH B: `echo_negotiator` fixture echoes offered `2026-07-28` on initialize and still returns discover `-32601`. Class `echo_negotiator`.
3. PATH C: `discover_ok` fixture returns discover `supportedVersions` including `2026-07-28`. Class `discover_ok`.

## Status: real vs stubbed

Real:

- `DialectClass` + `ProbeReport` + classify decision table
- Three in-process fake servers with distinct wire behavior
- Probe that offers `2026-07-28` then calls `server/discover`
- Self-proving `demo.sh` with exit codes and `report.json`

Stubbed / not built:

- Live MCP SDK server or HTTP / stdio transport
- Full discover schema beyond `supportedVersions`
- Scanning remote MCP endpoints for dialect mix
- Workflow Core or Hivemind integration
- Automatic remediation or upgrade advice

## Data shape (with paths)

Primary types in `src/dialect.py`:

| Name | Meaning |
| --- | --- |
| `DialectClass` | `old_only` \| `echo_negotiator` \| `discover_ok` |
| `DiscoverOutcome` | `ok`, optional `error_code`, `supported_versions` |
| `ProbeReport` | `target`, `class_`, `offered_version`, `initialize_echo`, `discover`, `evidence` |

Constants: `OFFERED_VERSION = "2026-07-28"`, `OLD_VERSION = "2025-06-18"`, `METHOD_NOT_FOUND = -32601`.

Side-effect oracle: `report.json` (array of probe dicts written by `demo.sh`).

## Repo map

| Path | Role |
| --- | --- |
| `src/dialect.py` | `DialectClass`, `ProbeReport`, `classify` |
| `src/servers.py` | three in-process fake servers |
| `src/probe.py` | offer `2026-07-28`, call discover, classify |
| `src/__init__.py` | package marker |
| `demo.sh` | proof runner (PATH A/B/C) |
| `README.md` | short human summary |
| `AGENTS.md` | this file |
| `requirements.txt` | notes stdlib-only |
| `.gitignore` | ignores `report.json`, caches |
| `LICENSE` | MIT |
| `BRIEF.txt` | original build brief (may remain in the tree) |

## Setup / run / verify (fresh clone)

```bash
git clone https://github.com/ideator-labs/mcpwireecho.git
cd mcpwireecho
bash demo.sh
```

Needs Python 3.10+ on PATH. No pip install.

Expected pass (abridged):

```
PATH A (old_only): PASS
PATH B (echo_negotiator): PASS
PATH C (discover_ok): PASS
SUMMARY: 3 passed, 0 failed
ALL CLAIMS PASSED
```

Exit code 0. `report.json` lists three targets with matching `class` values.

What failure looks like:

- Wrong class prints `FAIL` for that path and exit 1.
- Example: if echo fixture started implementing discover, PATH B fails because class becomes `discover_ok`.
- Example: if old fixture echoed `2026-07-28`, PATH A fails on `class` / `initializeEcho`.

## Design decisions

1. **Discover wins over echo.** If discover lists the offered version, class is `discover_ok` even when initialize also echoes. Matches the claim that discover is the real capability signal.
2. **Echo alone is not support.** `echo_negotiator` proves a server can mirror `protocolVersion` without implementing `server/discover`. Do not collapse this into `discover_ok`.
3. **In-process fakes.** No network. The claim is about classification of wire behavior, not transport.
4. **No MCP SDK.** JSON-RPC-shaped dicts are enough to prove the dialect split today.
5. **Fixed offered version.** The probe always offers `2026-07-28`. Do not "fix" this into a multi-version matrix inside the POC.

## Known limits

- Three hand-written fixtures. Not a corpus of real servers.
- Discover result only asserts `supportedVersions`. Other discover fields are ignored.
- Ambiguous responses fall back to a simple rule. Not a full state machine for every illegal combination.
- Does not reproduce the ecosystem revision-count survey; it only proves the local classifier.

## Prioritized next steps (done-when)

1. **Stdio smoke.** Wrap one fixture behind a stdio JSON-RPC loop. Done-when: an external client offering `2026-07-28` gets the same class as the in-process probe.
2. **Live probe CLI.** Accept a URL or command for a real server. Done-when: probing a known old server yields `old_only` with recorded evidence.
3. **Hivemind plug.** Expose dialect class as a gateway advisory before tool calls. Done-when: a Hivemind integration test skips tools when class is `old_only` under a strict policy.
4. **Workflow Core plug.** Record ProbeReport as an external event. Done-when: a WC sample workflow branches on `echo_negotiator` vs `discover_ok`.
5. **Pair with McpAuthGate.** Run dialect probe before auth checks on a remote target. Done-when: demo prints dialect class then auth path for one combined fixture.

## Working rules

- Name data shapes before adding branches.
- Keep `demo.sh` green before claiming done. Break one assertion on purpose once when changing proof logic, then restore.
- No em-dashes in docs.
- Do not fabricate source links.
- Prefer deleting code over adding layers.

## Context + checked sources

Built 2026-10-02 for Ideator Labs after notes that the MCP ecosystem is speaking multiple dated revisions at once, and that `server/discover` landed in the 2026-07-28 revision. Sibling POC: McpAuthGate (auth gate, different claim).

- https://dev.to/pennyforgehq/the-mcp-ecosystem-is-speaking-five-revisions-at-once-here-is-the-dated-count-3amd
- https://modelcontextprotocol.io/specification/2026-07-28/server/discover
- https://modelcontextprotocol.io/specification/2026-07-28/changelog
- https://earendil.com/posts/pi-1-0/
