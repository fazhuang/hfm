"""Public/research access boundary and customer ledger linkage

Revision ID: 0018
Revises: 0017

The platform has two sections with different audiences: the public portal
(information display) and the research platform (the project's core). Until
now ``media_assets`` could only say ``draft`` or ``published`` — it had no
way to express "ready, but only for researchers". 585 of the 681 customer
assets are exactly that state: modern academic papers and modern published
books that belong to researchers, not to a public portal. Marking them
``draft`` would have been wrong: they are not unfinished, they are scoped.

This revision adds two columns.

``access_scope`` — which section an asset belongs to. It is **orthogonal**
to ``publication_state``: scope says who the audience is, state says whether
it is ready for that audience. The 67 非遗佐证 assets are therefore
``access_scope='public'`` while still ``draft``, because they are portal
material that has not been redacted yet. Publication gating is unchanged
and still protects them.

The default is ``'research'``, not ``'public'``, so the boundary fails
closed: a newly inserted asset is invisible to the public portal until
someone deliberately marks it public. This matches the fail-closed posture
already used for media publication (P2-05-AC-01).

``ledger_id`` — the customer's asset register identifier (``HFM-A000013``).
``documents.source_asset_id`` already speaks this language, but
``media_assets.id`` is a UUID, so nothing could join a document to the media
object it was extracted from. Without that join the research platform cannot
connect its material to its provenance.

This revision creates the column but **does not fill it**. The register is
the authority for those identifiers and it lives in
``content-production/07-review/rights-review.csv``, not in the database, so
guessing them here would be both wrong and invisible. Run
``scripts/backfill-ledger-ids.py`` after upgrading; it reads the register and
reports any row it cannot resolve.

An earlier draft derived the ids from the position of ``object_key`` in
code-point order, on the theory that the register numbered its rows that way.
It does not: the register holds 689 rows, eight of which are non-media files
(``.DS_Store``, ``.videothumbnail.db``, ``.lnk``, a ``.zip``) that occupy
positions and push every later id along by five to seven. All 681 derived
ids were wrong. The column is left nullable so a mis-set value is visible as
a gap rather than silently plausible.

Backfill counts, asserted below:

  access_scope='public'    96   (22 public-domain imprints + 1 lineage image
                                 + 67 非遗佐证 + 4 皇甫谧 documents and
                                 portrait + 2 皇甫谧 films)
  access_scope='research' 585   (515 papers + 70 modern publications)
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None

#: Portal-side prefixes. Order does not matter here because every rule is
#: additive; an object matching none of them stays at the 'research' default.
_PORTAL_PREFIX_RULES = (
    "object_key LIKE '非遗佐证/%'",
    "object_key LIKE '皇甫谧%'",
    "object_key LIKE '针灸甲乙经/%' "
    "AND object_key NOT LIKE '针灸甲乙经/论文/%' "
    "AND object_key NOT LIKE '针灸甲乙经/论著/%'",
)

#: The four public-domain imprint groups inside 针灸甲乙经/论著/. Everything
#: else under that prefix is a modern in-copyright publication and stays on
#: the research side. LIKE is used rather than a regex so the same statement
#: runs on the SQLite databases the migration tests use.
_PUBLIC_DOMAIN_IMPRINTS = (
    "四库全书本清乾隆",
    "五车楼藏板",
    "行素草堂藏板",
    "医统正脉全书",
)

_EXPECTED_PUBLIC = 96
_EXPECTED_TOTAL = 681


def upgrade() -> None:
    op.add_column(
        "media_assets",
        sa.Column(
            "access_scope",
            sa.String(8),
            nullable=False,
            server_default="research",
        ),
    )
    op.add_column(
        "media_assets",
        sa.Column("ledger_id", sa.String(16), nullable=True),
    )

    # --- access_scope: portal-side objects only -----------------------------
    where = " OR ".join(_PORTAL_PREFIX_RULES)
    for imprint in _PUBLIC_DOMAIN_IMPRINTS:
        where += f" OR object_key LIKE '%{imprint}%'"
    op.execute(f"UPDATE media_assets SET access_scope = 'public' WHERE {where}")

    # --- ledger_id: column only, no backfill --------------------------------
    # The register in content-production/07-review/rights-review.csv owns these
    # identifiers. Deriving them here produced 681 wrong values; see the
    # module docstring. scripts/backfill-ledger-ids.py fills them.

    with op.batch_alter_table("media_assets") as batch:
        batch.create_check_constraint(
            "ck_media_assets_access_scope",
            "access_scope IN ('public', 'research')",
        )
        batch.create_unique_constraint("uq_media_assets_ledger_id", ["ledger_id"])

    op.create_index("ix_media_assets_access_scope", "media_assets", ["access_scope"])

    _assert_backfill()


def _assert_backfill() -> None:
    """Fail the migration rather than leave a wrong boundary behind.

    A silent mis-scope would either hide portal content or expose research
    material, and neither shows up as an error anywhere downstream.

    Runs against whatever dataset the target database holds. A schema-only
    database (the migration tests) has no rows to reconcile and returns
    early; the exact 96/681 split is only asserted when the customer dataset
    is actually present, as identified by its total row count.
    """
    conn = op.get_bind()
    total = conn.execute(sa.text("SELECT count(*) FROM media_assets")).scalar_one()
    if total != _EXPECTED_TOTAL:
        return
    public = conn.execute(
        sa.text("SELECT count(*) FROM media_assets WHERE access_scope = 'public'")
    ).scalar_one()
    if public != _EXPECTED_PUBLIC:
        raise RuntimeError(
            f"0018 access_scope mismatch on the customer dataset: "
            f"public={public} (want {_EXPECTED_PUBLIC}), total={total}"
        )


def downgrade() -> None:
    op.drop_index("ix_media_assets_access_scope", table_name="media_assets")
    with op.batch_alter_table("media_assets") as batch:
        batch.drop_constraint("uq_media_assets_ledger_id", type_="unique")
        batch.drop_constraint("ck_media_assets_access_scope", type_="check")
    op.drop_column("media_assets", "ledger_id")
    op.drop_column("media_assets", "access_scope")
