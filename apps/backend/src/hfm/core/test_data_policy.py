"""Test-data isolation policy.

Customer-provided files may be used by engineering only against an explicitly
isolated test database. This policy does not make any publication or rights
decision; it prevents an import-mode configuration mistake from targeting a
production database.
"""

from __future__ import annotations

from enum import StrEnum
from urllib.parse import urlparse


class ImportMode(StrEnum):
    PUBLIC = "public"
    CUSTOMER_TEST_DATA = "customer_test_data"


def _database_name(database_url: str) -> str:
    name = urlparse(database_url).path.rsplit("/", 1)[-1]
    return name.split("?", 1)[0]


def customer_test_data_enabled(*, environment: str, import_mode: str) -> bool:
    """Return whether the explicit customer-test mode is enabled."""
    return environment == "test" and import_mode == ImportMode.CUSTOMER_TEST_DATA


def assert_customer_test_target(*, environment: str, import_mode: str, database_url: str) -> None:
    """Fail closed unless customer test data targets an isolated test DB."""
    if not customer_test_data_enabled(environment=environment, import_mode=import_mode):
        raise RuntimeError("customer test data requires HFM_ENV=test and customer_test_data mode")
    database_name = _database_name(database_url)
    if database_name != "hfm_test" and not database_name.endswith("_test"):
        raise RuntimeError(
            "customer test data requires an isolated database named hfm_test or *_test"
        )
