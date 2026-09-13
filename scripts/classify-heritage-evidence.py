#!/usr/bin/env python3
"""HFM P2 redaction pipeline — stage 0: privacy classification.

Assigns a privacy class (``HFM-ASSET-PRESENTATION-POLICY.md`` §4) to every
``非遗佐证/`` media asset and writes it to ``media_assets.privacy_class``.

Why this exists (audit finding, 2026-09-14): the roadmap recorded the 67
``非遗佐证`` assets as one undifferentiated P2 set. The client's own policy
§4 is narrower — it names 法人证照原件, 不动产证明, 考评员名单 and 内部申报表
as **P3**, which "不进入公共投影". Publishing those as "redacted P2" would
have put material the policy forbids into the public projection. The class
must therefore be decided per asset before anything is redacted, and the
decision needs a signed artifact rather than a rule buried in a script.

Class meanings (policy §4):
  P0  ordinary public content            → publishable directly
  P1  professional / academic / public
      identity information               → publishable directly
  P2  personal information needing
      redaction (certificate numbers,
      signatures, ID numbers, private
      contact details)                   → published only as a redacted
                                           public derivative (§4.1)
  P3  material that must never enter
      the public projection              → archived; RBAC-restricted

Fail-closed: an asset matched by no rule is classified **P3**, never P1/P0.
An unrecognised file must not become publishable by omission.

Operator-only, dry-run first, one transaction. ``--emit-csv`` writes the
classification sheet that is the artifact to be signed; ``--commit`` applies
it. Lowering a class (P2 → P1) is a de-gating action, so the run refuses to
apply a class that the policy rule table does not actually support.

Usage:
    HFM_ENV=prod HFM_DATABASE_URL=<postgres DSN to /hfm_prod> \
    python classify-heritage-evidence.py --env-file ~/.hfm/secrets/prod.env \
        --emit-csv content-production/07-review/heritage-evidence-classification.csv
    # add --commit to write privacy_class; default is --dry-run (report + rollback)

Exit codes: 0 = PASS, 1 = FAIL, 2 = usage.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import importlib.util
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent
BACKEND_DIR = REPO_ROOT / "apps" / "backend"

GATED_PREFIX = "非遗佐证/"


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validator = _load_module("validate_production_env", _SCRIPT_DIR / "validate-production-env.py")

sys.path.insert(0, str(BACKEND_DIR / "src"))

from hfm.phase2.media.models import MediaAsset  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


@dataclass(frozen=True)
class Rule:
    """One classification rule. ``prefix`` matches by path prefix, ``key`` exactly."""

    privacy_class: str
    rationale: str
    prefix: str | None = None
    key: str | None = None

    def matches(self, object_key: str) -> bool:
        if self.key is not None:
            return object_key == self.key
        assert self.prefix is not None
        return object_key.startswith(self.prefix)


#: Ordered rule table — FIRST MATCH WINS, so specific keys precede folders.
#: Every rationale cites where the class comes from; this table is the thing
#: the classification sheet is derived from and should be reviewed alongside it.
RULES: tuple[Rule, ...] = (
    # ---------------------------------------------------------------- P3
    # Policy §4 P3 examples, verbatim in this folder's contents.
    Rule(
        "P3",
        "申报单位资质：事业单位法人证书复印件、不动产证明 —— 政策 §4 明列 P3",
        prefix="非遗佐证/08申报单位资质/",
    ),
    Rule(
        "P3",
        "职业技能等级认定资质：考评员名单、机构备案信息采集表/认定函/承诺书 —— 政策 §4 明列 P3",
        prefix="非遗佐证/09职业技能等级认定资质/",
    ),
    # ---------------------------------------------------------------- P2
    Rule(
        "P2",
        "领办人荣誉及获奖证书：含证书编号与签发签字",
        prefix="非遗佐证/02 领办人荣誉及获奖/",
    ),
    Rule(
        "P2",
        "非遗代表性传承人认定文件：含身份信息与文号",
        prefix="非遗佐证/03 非遗传承人资质/",
    ),
    Rule(
        "P2",
        "学术兼职聘书：含聘书编号与签发签字",
        prefix="非遗佐证/04 学术兼职/",
    ),
    # P1 entry must precede the folder's P2 rule (first match wins).
    Rule(
        "P1",
        "科研列表：公开学术成就清单，无证书编号",
        key="非遗佐证/05 技术成果/1、市级科研成果奖证书复印件/刘君奇 科研列表.docx",
    ),
    Rule(
        "P2",
        "科技进步奖证书：含证书编号与签发签字",
        prefix="非遗佐证/05 技术成果/1、市级科研成果奖证书复印件/",
    ),
    Rule(
        "P1",
        "已公开发表的期刊论文（封面/目录/首页/正文）",
        prefix="非遗佐证/05 技术成果/2、刘君奇发表论文/",
    ),
    Rule(
        "P2",
        "课题立项/结题证明：含文号与负责人身份信息",
        prefix="非遗佐证/05 技术成果/3、",
    ),
    Rule(
        "P2",
        "带教名单：含第三方（学生/基层医生）姓名、单位、手机号",
        prefix="非遗佐证/07 带徒传技与工作室成果/4、",
    ),
    Rule(
        "P2",
        "师承教育拜师大会新闻稿：机构新闻稿点名教职人员（属 P1 公开学术身份），"
        "但内嵌 3 张未复核图片，在人工看图确认前按 fail-closed 保持 P2。"
        "注：本文件曾因去标签提取把 <wp:posOffset> 图像定位值误读为手机号而判为 P2，"
        "该依据不成立，已更正 —— 当前分类依据的是未复核图片，不是手机号",
        key=(
            "非遗佐证/07 带徒传技与工作室成果/5、皇甫谧学院师承教育拜师大会相关材料/"
            "师承教育拜师大会新闻稿.docx"
        ),
    ),
    Rule(
        "P2",
        "名中医工作室成立及运行证明材料：含名单与签字",
        prefix="非遗佐证/07 带徒传技与工作室成果/1、",
    ),
    Rule(
        "P2",
        "中医工作室相关证明材料：含名单与签字",
        prefix="非遗佐证/07 带徒传技与工作室成果/2、",
    ),
    Rule(
        "P2",
        "传承工作室及国医馆名单及基本情况：名单类材料，须逐条核对第三方个人信息",
        prefix="非遗佐证/07 带徒传技与工作室成果/3、",
    ),
    # ---------------------------------------------------------------- P1
    Rule(
        "P1",
        "媒体报道：已公开发布的报道与播出证明",
        prefix="非遗佐证/06 媒体报道/",
    ),
    Rule(
        "P1",
        "师承教育教学制度、大纲与讲座安排：公开学术/教学信息",
        prefix="非遗佐证/07 带徒传技与工作室成果/5、",
    ),
    Rule(
        "P1",
        "场地及设施设备：公开的场地条件信息",
        prefix="非遗佐证/10场地及设施设备/",
    ),
)

#: Fail-closed default for anything the rule table does not recognise.
DEFAULT_CLASS = "P3"


def classify(object_key: str) -> tuple[str, str]:
    """Return ``(privacy_class, rationale)`` for one object key."""
    for rule in RULES:
        if rule.matches(object_key):
            return rule.privacy_class, rule.rationale
    return DEFAULT_CLASS, "未匹配任何分级规则 —— 按 fail-closed 默认归入 P3"


async def _run(
    db_url: str, emit_csv: Path | None, dry_run: bool
) -> tuple[dict[str, Any], list[str], list[str]]:
    engine = create_async_engine(db_url)
    lines: list[str] = []
    errors: list[str] = []
    summary: dict[str, Any] = {"scanned": 0, "changed": 0, "unchanged": 0, "by_class": {}}
    try:
        factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with factory() as session:
            try:
                assets = list(
                    (
                        await session.execute(
                            select(MediaAsset)
                            .where(MediaAsset.object_key.startswith(GATED_PREFIX))
                            .order_by(MediaAsset.object_key)
                        )
                    )
                    .scalars()
                    .all()
                )
                summary["scanned"] = len(assets)
                if not assets:
                    errors.append(f"no media assets found under {GATED_PREFIX}")

                rows: list[dict[str, str]] = []
                by_class: dict[str, int] = {}
                unmatched = 0
                for asset in assets:
                    object_key = str(asset.object_key)
                    previous = str(asset.privacy_class)
                    privacy_class, rationale = classify(object_key)
                    if not any(r.matches(object_key) for r in RULES):
                        unmatched += 1
                    by_class[privacy_class] = by_class.get(privacy_class, 0) + 1
                    if previous == privacy_class:
                        summary["unchanged"] += 1
                        lines.append(f"KEEP {privacy_class} {object_key}")
                    else:
                        summary["changed"] += 1
                        lines.append(f"SET  {previous} -> {privacy_class} {object_key}")
                        asset.privacy_class = privacy_class
                    rows.append(
                        {
                            "object_key": object_key,
                            "privacy_class": privacy_class,
                            "previous_privacy_class": previous,
                            "rationale": rationale,
                            "publication_route": {
                                "P0": "直接公开",
                                "P1": "直接公开",
                                "P2": "脱敏 derivative 后公开（政策 §4.1）",
                                "P3": "归档，不进入公共投影",
                            }[privacy_class],
                        }
                    )

                summary["by_class"] = dict(sorted(by_class.items()))
                summary["unmatched_defaulting_to_p3"] = unmatched

                if emit_csv is not None:
                    emit_csv.parent.mkdir(parents=True, exist_ok=True)
                    with emit_csv.open("w", encoding="utf-8", newline="") as handle:
                        writer = csv.DictWriter(
                            handle,
                            fieldnames=[
                                "object_key",
                                "privacy_class",
                                "previous_privacy_class",
                                "rationale",
                                "publication_route",
                            ],
                        )
                        writer.writeheader()
                        writer.writerows(rows)
                    lines.append(f"CSV_WRITTEN {emit_csv}")

                if dry_run:
                    await session.rollback()
                    lines.append("DRY_RUN=ROLLED_BACK (no commit)")
                else:
                    await session.commit()
            except BaseException:
                await session.rollback()
                raise
    finally:
        await engine.dispose()
    return summary, lines, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit-csv",
        type=Path,
        default=None,
        help="write the classification sheet to this path (the artifact to sign)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="report only; roll back (default)",
    )
    parser.add_argument(
        "--commit", dest="dry_run", action="store_false", help="apply privacy_class (operator action)"
    )
    parser.add_argument("--env-file", type=Path, default=None)
    parser.add_argument("--test-mode", action="store_true", help="isolated test runs only")
    parser.add_argument("--allow-sqlite", action="store_true", help="isolated test runs only")
    args = parser.parse_args(argv)

    env: dict[str, str] = dict(os.environ)
    if args.env_file is not None:
        if not args.env_file.is_file():
            print(f"ENV_FILE=FAIL (not found: {args.env_file.name})")
            return 1
        env.update(validator.parse_env_file(args.env_file))

    environment = "prod" if not args.test_mode else env.get("HFM_ENV", "test")
    errors = validator.validate_env(env, environment=environment, allow_sqlite=args.allow_sqlite)
    if errors:
        for error in errors:
            print(f"ENV=FAIL ({error})")
        return 1

    db_url = env.get("HFM_DATABASE_URL")
    if not db_url:
        print("ENV=FAIL (HFM_DATABASE_URL missing)")
        return 1

    summary, lines, run_errors = asyncio.run(_run(db_url, args.emit_csv, args.dry_run))
    for line in lines:
        print(line)
    for error in run_errors:
        print(f"ERROR {error}")

    print(f"MODE={'DRY_RUN' if args.dry_run else 'COMMIT'}")
    print(f"SCANNED={summary['scanned']}")
    print(f"CHANGED={summary['changed']} UNCHANGED={summary['unchanged']}")
    print(f"BY_CLASS={summary['by_class']}")
    print(f"UNMATCHED_DEFAULTED_TO_P3={summary['unmatched_defaulting_to_p3']}")

    if run_errors:
        print("RESULT=FAIL")
        return 1
    print("RESULT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
