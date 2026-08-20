"""
Generative-AI provider abstraction (Direktorder S15).

LUF Core Engine's methodology (schema/, canonical_data/, human_review/)
never imports this module and never imports any specific AI vendor SDK.
If/when generative AI is used, it sits behind `LLMProvider`, so the vendor
can change (e.g. one hosted model to another) without touching the methods
that encode LUF methodology.

No concrete provider bound to a specific commercial vendor is implemented
here by design -- wiring a real provider is a deployment-time decision, not
a Core Engine Foundation concern (Direktorder S33: don't build ahead of
what's asked). `NullProvider` and `StubEchoProvider` below exist only to
prove the abstraction is swappable in tests.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Minimal surface every generative backend must implement."""

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Return a text completion for `prompt`. Implementations own their own auth/config."""
        raise NotImplementedError

    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError


class NullProvider(LLMProvider):
    """Refuses to generate anything. Useful for proving the engine runs with no AI backend at all."""

    def complete(self, prompt: str) -> str:
        raise RuntimeError("NullProvider: no generative backend configured.")

    @property
    def provider_name(self) -> str:
        return "null"


class StubEchoProvider(LLMProvider):
    """Deterministic, offline stand-in used by tests to prove provider-swap without any live vendor."""

    def complete(self, prompt: str) -> str:
        return f"[stub-echo] {prompt}"

    @property
    def provider_name(self) -> str:
        return "stub_echo"
