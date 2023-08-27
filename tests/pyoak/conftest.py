from contextlib import AbstractContextManager, contextmanager
from typing import Generator, Protocol

import pytest
from pyoak import config


@pytest.fixture(scope="module", autouse=True)
def auto_clean_ser_types():
    """Automatically cleans all new types added to pyoak.serialize.TYPES by a
    test."""
    import pyoak.serialize

    cached = pyoak.serialize.TYPES.copy()
    yield
    pyoak.serialize.TYPES = cached


@pytest.fixture
def clean_ser_types():
    """Cleans all new types added to pyoak.serialize.TYPES by a single test."""
    import pyoak.serialize

    cached = pyoak.serialize.TYPES.copy()
    yield
    pyoak.serialize.TYPES = cached


class ConfigFixtureProtocol(Protocol):
    def __call__(
        self,
        *,
        logging: bool = config.TRACE_LOGGING,
        id_digest_size: int = config.ID_DIGEST_SIZE,
        runtime_checks: bool = config.RUNTIME_TYPE_CHECK
    ) -> AbstractContextManager[None]:
        ...


@pytest.fixture
def pyoak_config() -> ConfigFixtureProtocol:
    @contextmanager
    def _with_config(
        *,
        logging: bool = config.TRACE_LOGGING,
        id_digest_size: int = config.ID_DIGEST_SIZE,
        runtime_checks: bool = config.RUNTIME_TYPE_CHECK
    ) -> Generator[None, None, None]:
        old_logging = config.TRACE_LOGGING
        old_id_digest_size = config.ID_DIGEST_SIZE
        old_runtime_checks = config.RUNTIME_TYPE_CHECK
        config.TRACE_LOGGING = logging
        config.ID_DIGEST_SIZE = id_digest_size
        config.RUNTIME_TYPE_CHECK = runtime_checks
        yield
        config.TRACE_LOGGING = old_logging
        config.ID_DIGEST_SIZE = old_id_digest_size
        config.RUNTIME_TYPE_CHECK = old_runtime_checks

    return _with_config


def pytest_runtest_setup(item: pytest.Item):
    test_dep_marks = set(
        mark.name[4:] for mark in item.iter_markers() if mark.name.startswith("dep_")
    )
    assert len(test_dep_marks) <= 1, "Only one or no dep_ mark can be used"

    request_dep_marks = set(
        mark_name[4:]
        for mark_name in item.config.getoption("-m", "").split()
        if mark_name.startswith("dep_")
    )
    assert len(request_dep_marks) <= 1, "Only one or no dep_ mark can be used"

    if test_dep_marks and test_dep_marks != request_dep_marks and request_dep_marks != {"all"}:
        pytest.skip("Skipped test that should run only when optional deps are installed")
