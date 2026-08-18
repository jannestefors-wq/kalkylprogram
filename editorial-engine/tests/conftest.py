from __future__ import annotations

import pytest

from fixtures.fixture_dataset import build_fixture_dataset


@pytest.fixture(scope="session")
def dataset() -> dict[str, list]:
    return build_fixture_dataset()
