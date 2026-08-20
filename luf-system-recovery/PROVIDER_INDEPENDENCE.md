# Provider Independence -- 2026-08-20

Direktorder S24: map any external generative-AI usage in any accessible
component; change nothing.

## Findings

- **Kalkylprogram**: no AI usage of any kind found.
- **Editorial Engine**: no generative-AI call, no vendor SDK import, no
  API key reference anywhere in `editorial-engine/`. Its `Actor.AI_SYSTEM`
  enum value records WHO produced a piece of provenance data, but nothing
  in the engine invokes an actual AI model at runtime.
- **LUF Core Engine**: same -- `adapters/provider.py` defines a
  vendor-neutral `LLMProvider` interface with no concrete vendor bound to
  it (`NullProvider` and a deterministic `StubEchoProvider` only).
- **Website / House Engine / Adam / Dilemma Bank**: `NOT_ASSESSABLE` --
  none of these are reachable from this session, so no statement can be
  made about whether they call an external AI provider, what adapter they
  use, what prompts they hold, what their data flow is, or whether a
  fallback/provider-swap path exists. This is a real gap, not a "no."

## What this means for S23/S24's acceptance criteria

> Vi accepterar att framtida generativ AI kan kräva en extern
> modellprovider. Vi accepterar inte att LUF-metodiken endast finns hos
> providern.

Within what's visible: satisfied. LUF methodology (schema, canonical data,
Tool Registry, Human Review rules) lives entirely in git-tracked
Python/JSON, not inside any AI provider or session. Whether the same is
true of the website/Adam/House Engine cannot be confirmed or denied from
here.

No changes were made to any provider configuration, prompt, or adapter --
mapping only, per S24.
