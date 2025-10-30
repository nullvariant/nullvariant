#!/usr/bin/env python3
"""
INDEX.md 自動生成スクリプト

ADR、PRD、運用手順書の INDEX.md を自動生成します。
手動編集された INDEX.md も上書き可能（--force オプション）。

Usage:
    python scripts/generate_index.py                    # 全INDEX生成
    python scripts/generate_index.py --target adr       # ADRのみ
    python scripts/generate_index.py --force            # 手動編集を上書き
    python scripts/generate_index.py --dry-run          # プレビューのみ
"""

import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

# ディレクトリ定義
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent

# INDEX生成対象
TARGETS = {
    "adr": ROOT / "docs" / "decisions",
    "prd": ROOT / "docs" / "prd",
    "operations": ROOT / "docs" / "operations",
}

# ADRカテゴリ定義
ADR_CATEGORIES = {
    "architecture": "🏗️ アーキテクチャ変更",
    "process": "📋 プロセス・手順変更",
    "tooling": "🔧 ツール・インフラ変更",
    "documentation": "📚 ドキュメント構造変更",
    "security": "🔒 セキュリティ関連",
    "performance": "⚡ パフォーマンス最適化",
    "integration": "🔗 外部連携",
    "governance": "🏛️ ガバナンス・ポリシー",
}


def parse_adr_filename(filename: str) -> dict:
    """
    ADRファイル名をパース
    形式: YYYYMMDD_NNNN_slug_category.md
    """
    match = re.match(
        r"(\d{8})_(\d{4})_([a-z0-9-]+)(?:_([a-z]+))?\.md", filename
    )
    if not match:
        return None

    date_str, number, slug, category = match.groups()
    return {
        "date": datetime.strptime(date_str, "%Y%m%d"),
        "number": int(number),
        "slug": slug,
        "category": category or "other",
        "filename": filename,
    }


def extract_title_from_adr(filepath: Path) -> str:
    """ADRファイルから見出しを抽出"""
    try:
        content = filepath.read_text(encoding="utf-8")
        # "# ADR-NNNN: タイトル" の形式を想定
        match = re.search(r"^#\s+ADR-\d+:\s*(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return "（タイトル不明）"


def generate_adr_index(decisions_dir: Path, dry_run: bool = False) -> str:
    """ADRのINDEX.mdを生成"""
    print(f"\n📋 ADR INDEX.md 生成中...")

    # 月別ディレクトリを走査
    adr_files = []
    status_dirs = ["active", "deprecated", "superseded"]

    for status_dir in status_dirs:
        status_path = decisions_dir / status_dir
        if not status_path.exists():
            continue

        # YYYY/MM/ 配下のファイルを取得
        for year_dir in sorted(status_path.glob("*")):
            if not year_dir.is_dir() or not year_dir.name.isdigit():
                continue

            for month_dir in sorted(year_dir.glob("*")):
                if not month_dir.is_dir() or not month_dir.name.isdigit():
                    continue

                for md_file in sorted(month_dir.glob("*.md")):
                    parsed = parse_adr_filename(md_file.name)
                    if parsed:
                        parsed["status"] = status_dir
                        parsed["path"] = md_file.relative_to(decisions_dir)
                        parsed["title"] = extract_title_from_adr(md_file)
                        adr_files.append(parsed)

    if not adr_files:
        print("  ⚠️  ADRファイルが見つかりません")
        return ""

    # 統計
    total = len(adr_files)
    by_status = defaultdict(int)
    for adr in adr_files:
        by_status[adr["status"]] += 1

    # カテゴリ別グループ化
    by_category = defaultdict(list)
    for adr in adr_files:
        by_category[adr["category"]].append(adr)

    # 時系列グループ化（年月）
    by_yearmonth = defaultdict(list)
    for adr in adr_files:
        key = adr["date"].strftime("%Y年%m月")
        by_yearmonth[key].append(adr)

    # ステータス別グループ化
    by_status_list = defaultdict(list)
    for adr in adr_files:
        by_status_list[adr["status"]].append(adr)

    # INDEX.md 本文生成
    lines = [
        "# Architecture Decision Records (ADR) Index",
        "",
        f"**最終更新**: {datetime.now().strftime('%Y-%m-%d')}",
        f"**総件数**: {total}件（Active: {by_status['active']}, Deprecated: {by_status['deprecated']}, Superseded: {by_status['superseded']}）",
        "",
        "---",
        "",
        "## 📊 カテゴリ別",
        "",
    ]

    # カテゴリ別セクション
    for category in sorted(by_category.keys()):
        category_label = ADR_CATEGORIES.get(category, f"📌 {category}")
        lines.append(f"### {category_label}")

        for adr in sorted(by_category[category], key=lambda x: x["number"]):
            lines.append(
                f"- [ADR-{adr['number']:04d}]({adr['path']}) - {adr['title']} "
                f"({adr['date'].strftime('%Y-%m-%d')})"
            )

        lines.append("")

    # 時系列セクション
    lines.extend(["---", "", "## 📅 時系列", ""])

    for yearmonth in sorted(by_yearmonth.keys(), reverse=True):
        lines.append(f"### {yearmonth}")

        for adr in sorted(
            by_yearmonth[yearmonth], key=lambda x: x["date"], reverse=True
        ):
            lines.append(
                f"- {adr['date'].strftime('%Y-%m-%d')}: "
                f"[ADR-{adr['number']:04d}]({adr['path']}) - {adr['title']}"
            )

        lines.append("")

    # ステータス別セクション
    lines.extend(["---", "", "## 🔍 ステータス別", ""])

    for status in status_dirs:
        status_label = {
            "active": "Active (現行有効)",
            "deprecated": "Deprecated (非推奨)",
            "superseded": "Superseded (上書き済み)",
        }[status]

        lines.append(f"### {status_label}")

        adr_list = sorted(by_status_list[status], key=lambda x: x["number"])
        if adr_list:
            numbers = [f"ADR-{a['number']:04d}" for a in adr_list]
            lines.append(f"- {', '.join(numbers)}")
        else:
            lines.append("- なし")

        lines.append("")

    content = "\n".join(lines)

    if dry_run:
        print(f"\n{'='*60}")
        print("プレビュー:")
        print(f"{'='*60}")
        print(content)
        print(f"{'='*60}")
    else:
        output_path = decisions_dir / "INDEX.md"
        output_path.write_text(content, encoding="utf-8")
        print(f"  ✅ 生成完了: {output_path}")

    return content


def generate_prd_index(prd_dir: Path, dry_run: bool = False) -> str:
    """PRDのINDEX.mdを生成"""
    print(f"\n💡 PRD INDEX.md 生成中...")

    # active/, implemented/, deprecated/ 配下のファイルを取得
    prd_files = []
    status_dirs = ["active", "implemented", "deprecated"]

    for status_dir in status_dirs:
        status_path = prd_dir / status_dir
        if not status_path.exists():
            continue

        for md_file in sorted(status_path.glob("*.md")):
            # ファイル名: YYYYMMDD_slug.ja.md
            match = re.match(r"(\d{8})_([a-z0-9-]+)\.ja\.md", md_file.name)
            if match:
                date_str, slug = match.groups()
                prd_files.append(
                    {
                        "date": datetime.strptime(date_str, "%Y%m%d"),
                        "slug": slug,
                        "status": status_dir,
                        "path": md_file.relative_to(prd_dir),
                        "filename": md_file.name,
                    }
                )

    if not prd_files:
        print("  ⚠️  PRDファイルが見つかりません")
        return ""

    # INDEX.md 本文生成
    lines = [
        "# Product Requirements Documents (PRD) Index",
        "",
        f"**最終更新**: {datetime.now().strftime('%Y-%m-%d')}",
        f"**総件数**: {len(prd_files)}件",
        "",
        "---",
        "",
        "## 📋 ステータス別",
        "",
    ]

    for status in status_dirs:
        status_label = {
            "active": "Active (策定中・未実装)",
            "implemented": "Implemented (実装完了)",
            "deprecated": "Deprecated (不要・中止)",
        }[status]

        lines.append(f"### {status_label}")

        status_prds = [p for p in prd_files if p["status"] == status]
        for prd in sorted(status_prds, key=lambda x: x["date"], reverse=True):
            lines.append(
                f"- [{prd['date'].strftime('%Y-%m-%d')}]({prd['path']}) - {prd['slug']}"
            )

        lines.append("")

    content = "\n".join(lines)

    if dry_run:
        print(f"\n{'='*60}")
        print("プレビュー:")
        print(f"{'='*60}")
        print(content)
        print(f"{'='*60}")
    else:
        output_path = prd_dir / "INDEX.md"
        output_path.write_text(content, encoding="utf-8")
        print(f"  ✅ 生成完了: {output_path}")

    return content


def generate_governance_index(governance_dir: Path, dry_run: bool = False) -> str:
    """governance のINDEX.mdを生成（メタドキュメント一覧）"""
    print(f"\n🏛️  governance INDEX.md 生成中...")

    # governance/ 直下のドキュメントファイル（README.md, INDEX.md 除外）
    # Markdown (.md) と YAML (.yml) の両方を対象
    doc_files = []
    for file_path in sorted(governance_dir.glob("*")):
        if file_path.is_file() and file_path.suffix in [".md", ".yml", ".yaml"]:
            if file_path.name not in ["README.md", "INDEX.md"]:
                doc_files.append(file_path)

    if not doc_files:
        print("  ⚠️  ドキュメントが見つかりません")
        return ""

    # 権威文書（SSOT）と説明文書を分類
    ssot_files = []
    guide_files = []
    
    for doc_file in doc_files:
        # DOCUMENTATION_STRUCTURE.yml, AI_GUIDELINES.md, SSOT_PRIORITY_MATRIX.md は権威文書
        if doc_file.name in ["DOCUMENTATION_STRUCTURE.yml", "AI_GUIDELINES.md", "SSOT_PRIORITY_MATRIX.md"]:
            ssot_files.append(doc_file)
        else:
            guide_files.append(doc_file)

    # INDEX.md 本文生成
    lines = [
        "# Governance & Documentation Rules",
        "",
        f"**最終更新**: {datetime.now().strftime('%Y-%m-%d')}",
        f"**ドキュメント数**: {len(doc_files)}個",
        "",
        "ドキュメント管理とガバナンスの基準ドキュメント一覧です。",
        "",
        "---",
        "",
        "## 📚 参照ドキュメント",
        "",
    ]

    # 権威文書（SSOT）セクション
    if ssot_files:
        lines.append("### 権威文書（SSOT）")
        lines.append("")
        
        for doc_file in sorted(ssot_files):
            relative_path = doc_file.relative_to(governance_dir)
            
            # ファイルから最初の見出しを抽出（Markdownの場合のみ）
            try:
                if doc_file.suffix == ".md":
                    content = doc_file.read_text(encoding="utf-8")
                    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                    title = match.group(1).strip() if match else relative_path.stem
                else:
                    # YAMLファイルの場合は説明文を追加
                    title = "ドキュメント構造定義（機械可読形式）" if "STRUCTURE" in doc_file.name else relative_path.stem
            except Exception:
                title = relative_path.stem

            lines.append(f"- [{title}]({relative_path})")
        
        lines.append("")

    # 説明・ガイド文書セクション
    if guide_files:
        lines.append("### 説明・ガイド文書")
        lines.append("")
        
        for doc_file in sorted(guide_files):
            relative_path = doc_file.relative_to(governance_dir)
            
            # ファイルから最初の見出しを抽出
            try:
                content = doc_file.read_text(encoding="utf-8")
                match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                title = match.group(1).strip() if match else relative_path.stem
            except Exception:
                title = relative_path.stem

            lines.append(f"- [{title}]({relative_path})")
        
        lines.append("")

    lines.extend(["", "---", "", "## 🗺️ 初めての方へ", ""])
    lines.append("このディレクトリに初めて来た方は、[README.md](README.md) から始めてください。")
    lines.append("ユースケース別の導線が記載されています。")
    lines.extend(["", "---", "", "**注記**: このディレクトリは大文字メタドキュメント専用です。"])
    lines.append("時系列記録は `docs/log/` に管理されます。")

    content = "\n".join(lines)

    if dry_run:
        print(f"\n{'='*60}")
        print("プレビュー:")
        print(f"{'='*60}")
        print(content)
        print(f"{'='*60}")
    else:
        output_path = governance_dir / "INDEX.md"
        output_path.write_text(content, encoding="utf-8")
        print(f"  ✅ 生成完了: {output_path}")

    return content


def generate_operations_index(operations_dir: Path, dry_run: bool = False) -> str:
    """operations のINDEX.mdを生成（現在版 + 過去ログ索引）"""
    print(f"\n📋 operations INDEX.md 生成中...")

    current_dir = operations_dir / "current"
    archive_dir = operations_dir / "archive"

    # 現在の運用手順
    current_files = []
    if current_dir.exists():
        for md_file in sorted(current_dir.glob("*.md")):
            if md_file.name != "README.md":
                current_files.append(md_file)

    # アーカイブ（年月別）
    archive_files = {}  # {year-month: [files]}
    if archive_dir.exists():
        for year_dir in sorted(archive_dir.glob("*"), reverse=True):
            if year_dir.is_dir():
                for month_dir in sorted(year_dir.glob("*"), reverse=True):
                    if month_dir.is_dir():
                        key = f"{year_dir.name}/{month_dir.name}"
                        archive_files[key] = sorted(month_dir.glob("*.md"))

    if not current_files and not archive_files:
        print("  ⚠️  ドキュメントが見つかりません")
        return ""

    # INDEX.md 本文生成
    lines = [
        "# Operations Manual Index",
        "",
        f"**最終更新**: {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "---",
        "",
        "## 📌 現在の運用手順",
        "",
    ]

    if current_files:
        for md_file in current_files:
            # ファイルから最初の見出しを抽出
            try:
                content = md_file.read_text(encoding="utf-8")
                match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                title = match.group(1).strip() if match else md_file.stem
            except Exception:
                title = md_file.stem

            relative_path = md_file.relative_to(operations_dir)
            lines.append(f"- [{title}]({relative_path})")
    else:
        lines.append("*なし*")

    if archive_files:
        lines.extend(["", "---", "", "## 📚 過去ログ（アーカイブ）", ""])

        for key in sorted(archive_files.keys(), reverse=True):
            lines.append(f"### {key}")

            for md_file in sorted(archive_files[key]):
                # ファイルから最初の見出しを抽出
                try:
                    content = md_file.read_text(encoding="utf-8")
                    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                    title = match.group(1).strip() if match else md_file.stem
                except Exception:
                    title = md_file.stem

                relative_path = md_file.relative_to(operations_dir)
                lines.append(f"- [{title}]({relative_path})")

            lines.append("")

    content = "\n".join(lines)

    if dry_run:
        print(f"\n{'='*60}")
        print("プレビュー:")
        print(f"{'='*60}")
        print(content)
        print(f"{'='*60}")
    else:
        output_path = operations_dir / "INDEX.md"
        output_path.write_text(content, encoding="utf-8")
        print(f"  ✅ 生成完了: {output_path}")

    return content


def main():
    parser = argparse.ArgumentParser(description="INDEX.md 自動生成スクリプト")
    parser.add_argument(
        "--target",
        choices=["adr", "prd", "governance", "operations", "all"],
        default="all",
        help="生成対象（デフォルト: all）",
    )
    parser.add_argument(
        "--force", action="store_true", help="手動編集されたINDEX.mdを上書き"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="プレビューのみ（ファイル書き込みなし）"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("📝 INDEX.md 自動生成")
    print("=" * 60)

    if args.target in ["adr", "all"]:
        generate_adr_index(TARGETS["adr"], dry_run=args.dry_run)

    if args.target in ["prd", "all"]:
        if TARGETS["prd"].exists():
            generate_prd_index(TARGETS["prd"], dry_run=args.dry_run)
        else:
            print(f"\n⚠️  {TARGETS['prd']} が存在しません（スキップ）")

    if args.target in ["governance", "all"]:
        governance_dir = ROOT / "docs" / "governance"
        if governance_dir.exists():
            generate_governance_index(governance_dir, dry_run=args.dry_run)
        else:
            print(f"\n⚠️  {governance_dir} が存在しません（スキップ）")

    if args.target in ["operations", "all"]:
        operations_dir = ROOT / "docs" / "operations"
        if operations_dir.exists():
            generate_operations_index(operations_dir, dry_run=args.dry_run)
        else:
            print(f"\n⚠️  {operations_dir} が存在しません（スキップ）")

    print("\n" + "=" * 60)
    if args.dry_run:
        print("✅ プレビュー完了（ファイルは変更されていません）")
    else:
        print("✅ INDEX.md 生成完了")
    print("=" * 60)


if __name__ == "__main__":
    main()
