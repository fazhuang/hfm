"""P2 redaction pipeline: privacy class + derivative publication grant

Revision ID: 0017
Revises: 0016

The 67 ``非遗佐证`` assets are privacy-classified P2 (certificate numbers,
signatures, private contact details) and P3 (法人证照 / 不动产证明 /
考评员名单 / 内部申报表). Policy ``HFM-ASSET-PRESENTATION-POLICY.md`` §4
requires P2 material to be published only as a redacted public derivative
(§4.1) and P3 material never to enter the public projection at all.

Before this revision those rules lived only in prose and in a
script-level clearance manifest. Two schema gaps made them unenforceable:

  1. there was no privacy class on a media row, so nothing could tell a P2
     certificate from an ordinary paper;
  2. ``publication_permission`` is inherited by a derivative from its
     original, and a P2 original must keep it false — so a redacted
     derivative could never satisfy ``rights_sufficient()`` and the
     pipeline was locked shut the moment it was written.

This revision adds ``privacy_class`` and a derivative-only publication
grant, plus check constraints that make the policy a database invariant:

  - P3 is never published, derivative or not;
  - a P2 *original* is never published (only a P2 derivative may be);
  - a P2/P3 row never carries ``publication_permission``;
  - the derivative grant can only be set on a row that has an original.

Backfill follows the signed clearance manifest
(``07-review/media-publication-clearance.json``): ``针灸甲乙经/`` → P0,
``皇甫谧/`` and ``皇甫谧画像.jpeg`` → P1. ``非遗佐证/`` is backfilled P2 —
the conservative class, refined to P3 per asset by the classification
stage before anything is redacted. No existing row changes publication
state, and no row acquires a grant.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "media_assets",
        sa.Column(
            "privacy_class",
            sa.String(2),
            nullable=False,
            server_default="P0",
        ),
    )
    op.add_column(
        "media_assets",
        sa.Column(
            "derivative_publication_permission",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    # Backfill from the signed clearance manifest. Order matters: the most
    # specific keys are matched first so the portrait is not swallowed by
    # the 皇甫谧/ prefix rule.
    op.execute(
        """
        UPDATE media_assets SET privacy_class = 'P1' WHERE object_key = '皇甫谧画像.jpeg'
        """
    )
    op.execute(
        """
        UPDATE media_assets SET privacy_class = 'P1' WHERE object_key LIKE '皇甫谧/%'
        """
    )
    op.execute(
        """
        UPDATE media_assets SET privacy_class = 'P2' WHERE object_key LIKE '非遗佐证/%'
        """
    )

    # Constraints go through batch mode: SQLite has no ALTER TABLE ADD
    # CONSTRAINT, so the plain op.create_check_constraint path fails under
    # `alembic upgrade head` on the SQLite databases the migration tests use.
    # Batch mode recreates the table on SQLite and is a no-op passthrough on
    # PostgreSQL, so one code path serves both.
    with op.batch_alter_table("media_assets") as batch:
        batch.create_check_constraint(
            "ck_media_assets_privacy_class",
            "privacy_class IN ('P0', 'P1', 'P2', 'P3')",
        )
        batch.create_check_constraint(
            "ck_media_assets_p3_never_published",
            "privacy_class <> 'P3' OR publication_state <> 'published'",
        )
        batch.create_check_constraint(
            "ck_media_assets_p2_original_never_published",
            "privacy_class <> 'P2' OR original_object_key IS NOT NULL "
            "OR publication_state <> 'published'",
        )
        batch.create_check_constraint(
            "ck_media_assets_gated_never_permitted",
            "privacy_class NOT IN ('P2', 'P3') OR NOT publication_permission",
        )
        batch.create_check_constraint(
            "ck_media_assets_derivative_grant",
            "NOT derivative_publication_permission OR original_object_key IS NOT NULL",
        )

    op.create_index("ix_media_assets_privacy_class", "media_assets", ["privacy_class"])


def downgrade() -> None:
    op.drop_index("ix_media_assets_privacy_class", table_name="media_assets")
    with op.batch_alter_table("media_assets") as batch:
        batch.drop_constraint("ck_media_assets_derivative_grant", type_="check")
        batch.drop_constraint("ck_media_assets_gated_never_permitted", type_="check")
        batch.drop_constraint("ck_media_assets_p2_original_never_published", type_="check")
        batch.drop_constraint("ck_media_assets_p3_never_published", type_="check")
        batch.drop_constraint("ck_media_assets_privacy_class", type_="check")
    op.drop_column("media_assets", "derivative_publication_permission")
    op.drop_column("media_assets", "privacy_class")
