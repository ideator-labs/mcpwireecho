# McpWireEcho

Agents and contributors, read [AGENTS.md](AGENTS.md) before you change anything.

## What it proves

Offering `protocolVersion` `2026-07-28` classifies a target as `old_only`, `echo_negotiator`, or `discover_ok`. A server that echoes the requested version is not the same as one that implements `server/discover`.

- PATH A: old fixture returns `2025-06-18` on initialize and `-32601` on discover. Class `old_only`.
- PATH B: echo fixture mirrors the offered version on initialize and still returns `-32601` on discover. Class `echo_negotiator`.
- PATH C: discover fixture returns `DiscoverResult` with `supportedVersions` including `2026-07-28`. Class `discover_ok`.

## Run

Needs Python 3.10+. Stdlib only.

```bash
bash demo.sh
```

Exit 0 means all three classifications matched. Exit non-zero means a class drifted.

## Data shape

`DialectClass` and `ProbeReport` in `src/dialect.py`:

- `DialectClass`: `old_only` | `echo_negotiator` | `discover_ok`
- `ProbeReport`: `target`, `class`, `offeredVersion`, `initializeEcho`, `discover` (`ok` / `errorCode` / `supportedVersions`), `evidence`

## Wire shape

Simulated MCP JSON-RPC (not an SDK server):

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2026-07-28","capabilities":{},"clientInfo":{"name":"mcpwireecho","version":"0.1"}}}
```

```json
{"jsonrpc":"2.0","id":2,"method":"server/discover","params":{}}
```

## Limits

- In-process fake servers only. No MCP SDK, no real network listener.
- Three fixed dialect fixtures. Not a scanner for live servers.
- Classification is a local decision table, not a full protocol conformance suite.
- Does not implement the full 2026-07-28 discover surface beyond `supportedVersions`.

## Sources

- https://dev.to/pennyforgehq/the-mcp-ecosystem-is-speaking-five-revisions-at-once-here-is-the-dated-count-3amd
- https://modelcontextprotocol.io/specification/2026-07-28/server/discover
- https://modelcontextprotocol.io/specification/2026-07-28/changelog
- https://earendil.com/posts/pi-1-0/
