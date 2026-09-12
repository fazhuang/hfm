from __future__ import annotations

import pytest

from hfm.core.test_data_policy import (
    assert_customer_test_target,
    customer_test_data_enabled,
)


def test_customer_test_mode_requires_test_environment() -> None:
    assert customer_test_data_enabled(environment="test", import_mode="customer_test_data")
    assert not customer_test_data_enabled(environment="prod", import_mode="customer_test_data")
    assert not customer_test_data_enabled(environment="test", import_mode="public")


def test_customer_test_mode_accepts_only_isolated_database() -> None:
    assert_customer_test_target(
        environment="test",
        import_mode="customer_test_data",
        database_url="postgresql+asyncpg://u:p@localhost:5432/hfm_test",
    )
    assert_customer_test_target(
        environment="test",
        import_mode="customer_test_data",
        database_url="postgresql+asyncpg://u:p@localhost:5432/hfm_verify_test",
    )


@pytest.mark.parametrize(
    ("environment", "import_mode", "database_url"),
    [
        ("prod", "customer_test_data", "postgresql+asyncpg://u:p@localhost:5432/hfm_test"),
        ("test", "public", "postgresql+asyncpg://u:p@localhost:5432/hfm_test"),
        ("test", "customer_test_data", "postgresql+asyncpg://u:p@localhost:5432/hfm_prod"),
    ],
)
def test_customer_test_mode_fails_closed(
    environment: str, import_mode: str, database_url: str
) -> None:
    with pytest.raises(RuntimeError):
        assert_customer_test_target(
            environment=environment,
            import_mode=import_mode,
            database_url=database_url,
        )
