"""WR00-B2-R1 — password-policy single-source parity tests.

Proves that the RUNTIME change-password validator
(hfm.phase1.auth.password_policy_reasons — used by the
/api/v1/auth/change-password endpoint) and the PRODUCTION BOOTSTRAP validator
(scripts/initialize-production.py::validate_bootstrap_password — used by the
first-SYSTEM_ADMIN initializer) are the SAME policy:

    PASSWORD_POLICY_SINGLE_SOURCE=YES
    PASSWORD_POLICY_PARITY=PASS

Every password in the VALID / INVALID / BOUNDARY corpus is accepted or
rejected identically at both entry points. No consumer maintains its own
MIN_PASSWORD_LENGTH / character rules / common-password list / validation
logic — the shared module owns them and both entry points delegate to it.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "apps" / "backend"
INIT_SCRIPT = REPO_ROOT / "scripts" / "initialize-production.py"

#: Load the runtime validator (hfm package is installed editable in the venv).
from hfm.phase1.auth import (  # noqa: E402
    FORBIDDEN_PASSWORDS,
    MIN_PASSWORD_LENGTH,
    password_policy_reasons,
)

#: Load the bootstrap validator module by path (same technique the
#: initializer uses for validate-production-env.py).
_spec = importlib.util.spec_from_file_location("initialize_production", INIT_SCRIPT)
assert _spec is not None and _spec.loader is not None
bootstrap_mod = importlib.util.module_from_spec(_spec)
sys.modules["initialize_production"] = bootstrap_mod
_spec.loader.exec_module(bootstrap_mod)
validate_bootstrap_password = bootstrap_mod.validate_bootstrap_password

PARITY_USERNAME = "parity-researcher"


def runtime_accepts(password: str) -> bool:
    return not password_policy_reasons(password, username=PARITY_USERNAME)


def bootstrap_accepts(password: str) -> bool:
    return not validate_bootstrap_password(PARITY_USERNAME, password)


# ------------------------------------------------------------- policy corpus

VALID_PASSWORDS = (
    "Hfm-parity-valid-passphrase-2026!",
    "correct horse battery staple-42",
    "A0b1C2d3E4f5G6h7I8j9!",  # 12+ chars, not a default, no username
)

INVALID_PASSWORDS = (
    "",                      # required
    "short",                 # too short
    "password",              # known default
    "admin123",              # known default
    "123456",                # known default
    "changeme123",           # known default
    "qwerty123",             # known default
    f"{PARITY_USERNAME}-tail-extra",  # embeds the username
    "  ",                    # whitespace-only is still too short
)

BOUNDARY_PASSWORDS = (
    "Abcdefgh1234",   # exactly MIN_PASSWORD_LENGTH -> accept
    "Abcdefgh123",    # MIN_PASSWORD_LENGTH - 1   -> reject
    f"{'X' * (MIN_PASSWORD_LENGTH + 5)}",  # strong random-ish -> accept
    f"{'X' * (MIN_PASSWORD_LENGTH - 1)}",  # just below -> reject
)


def test_single_source_constants_are_shared() -> None:
    """The bootstrap never defines its own length or common-password list."""
    assert MIN_PASSWORD_LENGTH == 12
    assert "password" in FORBIDDEN_PASSWORDS
    assert "admin123" in FORBIDDEN_PASSWORDS
    assert "123456" in FORBIDDEN_PASSWORDS
    # The bootstrap module references the shared constants/functions rather
    # than maintaining private duplicates.
    source = INIT_SCRIPT.read_text(encoding="utf-8")
    assert "password_policy_reasons" in source
    assert "_FORBIDDEN_PASSWORDS" not in source
    assert "MIN_PASSWORD_LENGTH = " not in source.split("hfm.phase1.auth")[0]


def test_valid_passwords_accepted_by_both() -> None:
    for password in VALID_PASSWORDS:
        assert runtime_accepts(password), password
        assert bootstrap_accepts(password), password
        assert runtime_accepts(password) is bootstrap_accepts(password)


def test_invalid_passwords_rejected_by_both() -> None:
    for password in INVALID_PASSWORDS:
        assert not runtime_accepts(password), password
        assert not bootstrap_accepts(password), password
        assert runtime_accepts(password) is bootstrap_accepts(password)


def test_boundary_passwords_parity() -> None:
    for password in BOUNDARY_PASSWORDS:
        assert runtime_accepts(password) is bootstrap_accepts(password), password


def test_bootstrap_renders_same_decision_for_every_forbidden_default() -> None:
    for password in FORBIDDEN_PASSWORDS:
        assert not runtime_accepts(password), password
        assert not bootstrap_accepts(password), password


def test_policy_parity_full_corpus() -> None:
    corpus = VALID_PASSWORDS + INVALID_PASSWORDS + BOUNDARY_PASSWORDS
    disagreements = [
        password
        for password in corpus
        if runtime_accepts(password) is not bootstrap_accepts(password)
    ]
    assert disagreements == []
