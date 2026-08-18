"""
Shared word-overlap helper for classification.py and comparison.py.

Deliberately dumb: lowercase, strip punctuation, drop short/stopword
tokens, exact set intersection. No stemming, no fuzzy matching, no
external NLP library, no embeddings -- see engine/classification.py's
module docstring for why (order sections 9/24: transparent, no
vector/semantic retrieval in V1A).
"""

from __future__ import annotations

STOPWORDS = {
    "och", "det", "den", "de", "att", "som", "inte", "eller", "ett", "en",
    "kan", "ar", "for", "med", "pa", "av", "till", "vid", "har", "hade",
    "blir", "blev", "kommer", "detta", "denna", "dessa", "vad", "hur",
    "vem", "var", "ska", "far", "fick", "ger", "gav", "sin", "sina", "sitt",
    "man", "allt", "alla", "over", "under", "utan", "mer", "mest",
    "sig", "in", "ut", "upp", "ner", "sa", "nar", "om", "da",
}


def normalize_words(text: str) -> set[str]:
    cleaned = "".join(ch.lower() if ch.isalnum() or ch.isspace() else " " for ch in text)
    return {w for w in cleaned.split() if len(w) > 2 and w not in STOPWORDS}
