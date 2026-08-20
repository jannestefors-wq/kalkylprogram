from __future__ import annotations

import pytest

from adapters.provider import LLMProvider, NullProvider, StubEchoProvider


def run_with_provider(provider: LLMProvider, prompt: str) -> str:
    """A stand-in for any Core Engine call site: it only depends on LLMProvider."""
    return provider.complete(prompt)


def test_null_provider_refuses_without_needing_a_vendor():
    provider: LLMProvider = NullProvider()
    with pytest.raises(RuntimeError):
        run_with_provider(provider, "hello")


def test_stub_provider_is_swappable_with_no_code_change_at_call_site():
    provider: LLMProvider = StubEchoProvider()
    assert run_with_provider(provider, "hello") == "[stub-echo] hello"


def test_two_providers_satisfy_the_same_interface():
    providers = [NullProvider(), StubEchoProvider()]
    names = {p.provider_name for p in providers}
    assert names == {"null", "stub_echo"}
    for p in providers:
        assert isinstance(p, LLMProvider)
