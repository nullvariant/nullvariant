#!/usr/bin/env python3
"""
ADR自動生成スクリプト

Usage:
    # 対話型モード
    python scripts/record_decision.py

    # コマンドラインオプション
    python scripts/record_decision.py \
      --title "決定のタイトル" \
      --context "背景・理由" \
      --category architecture \
      --author "GitHub Copilot"

Options:
    --title       : 決定のタイトル（必須）
    --context     : 背景・理由（必須）
    --category    : カテゴリタグ（必須）
    --decision    : 決定内容（任意）
    --author      : 決定者（デフォルト: "AI"）
    --related     : 関連ファイル（複数指定可能）
    --output-dir  : 出力ディレクトリ（デフォルト: docs/decisions/active/YYYY/MM）
    --date        : 決定日（デフォルト: 今日、YYYYMMDD形式）
    --interactive : 対話型モード有効化
"""

import argparse
from pathlib import Path
from datetime import datetime
import re
import sys

# ディレクトリ定義
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
DECISIONS_DIR = ROOT / "docs" / "decisions"

# カテゴリ定義（ADR-0002で確立）
CATEGORIES = [
    "architecture",
    "process",
    "tooling",
    "documentation",
    "security",
    "performance",
    "integration",
    "governance",
]

TEMPLATE = """# ADR-{number}: {title}

## Status
- **提案日**: {date_formatted}
- **状態**: Draft
- **決定者**: {author}

## Context

### 背景
{context}

### 検討した選択肢（任意）
1. **選択肢A**: （記入してください）
2. **選択肢B**: （記入してください）

## Decision

{decision}

## Consequences

### ✅ メリット
- （具体的なメリットを記入してください）

### ⚠️ デメリット
- （具体的なデメリットを記入してください）

### 📋 TODO
- [ ] （必要なタスクを記入してください）

## Related

### 関連するファイル
{related_files}

### 関連する ADR
- （関連するADRがあれば記入してください）

### 関連する Issue/PR
- （GitHubのIssue/PRがあれば記入してください）

### 関連する Commit
- （主要なコミットSHAを記入してください）

---

**Status**: Draft  
**次のアクション**: human によるレビュー・承認
"""


def get_next_number(decisions_dir: Path) -> int:
    """既存ADRから次の番号を取得（月別ディレクトリ対応）"""
    numbers = []
    
    # active/, deprecated/, superseded/ 配下を走査
    for status_dir in ["active", "deprecated", "superseded"]:
        status_path = decisions_dir / status_dir
        if not status_path.exists():
            continue
        
        # YYYY/MM/ 配下のファイルを取得
        for md_file in status_path.rglob("*.md"):
            # ファイル名: YYYYMMDD_NNNN_slug_category.md
            match = re.match(r"\d{8}_(\d{4})_", md_file.name)
            if match:
                numbers.append(int(match.group(1)))
    
    if not numbers:
        return 1
    
    return max(numbers) + 1


def get_output_dir(decisions_dir: Path, date: datetime, status: str = "active") -> Path:
    """月別ディレクトリを取得（自動作成）"""
    year_month_dir = decisions_dir / status / date.strftime("%Y") / date.strftime("%m")
    year_month_dir.mkdir(parents=True, exist_ok=True)
    return year_month_dir


def sanitize_filename(title: str) -> str:
    """タイトルをファイル名に適した形式に変換"""
    # 小文字化
    filename = title.lower()
    # スペースをハイフンに
    filename = filename.replace(" ", "-")
    # 日本語はそのまま、特殊文字を除去
    filename = re.sub(r"[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF-]", "", filename)
    # 連続するハイフンを1つに
    filename = re.sub(r"-+", "-", filename)
    # 前後のハイフンを除去
    filename = filename.strip("-")
    # 長すぎる場合は30文字でカット
    if len(filename) > 30:
        filename = filename[:30].rstrip("-")
    return filename


def interactive_input(prompt: str, default: str = "") -> str:
    """対話型入力"""
    if default:
        user_input = input(f"{prompt} (デフォルト: {default}): ").strip()
        return user_input if user_input else default
    else:
        while True:
            user_input = input(f"{prompt} (必須): ").strip()
            if user_input:
                return user_input
            print("  ❌ 入力は必須です")


def select_category(categories: list) -> str:
    """カテゴリ選択（対話型）"""
    print("\n📂 カテゴリを選択してください:")
    for i, cat in enumerate(categories, 1):
        print(f"   {i}. {cat}")
    
    while True:
        try:
            choice = int(input(f"\n選択 (1-{len(categories)}): ").strip())
            if 1 <= choice <= len(categories):
                return categories[choice - 1]
            print(f"  ❌ 1-{len(categories)} の範囲で入力してください")
        except ValueError:
            print("  ❌ 数値で入力してください")


def main():
    parser = argparse.ArgumentParser(
        description="ADR (Architecture Decision Record) 自動生成スクリプト"
    )
    parser.add_argument("--title", default=None, help="決定のタイトル")
    parser.add_argument("--context", default=None, help="背景・理由")
    parser.add_argument(
        "--category",
        default=None,
        choices=CATEGORIES,
        help=f"カテゴリタグ（必須）: {', '.join(CATEGORIES)}",
    )
    parser.add_argument(
        "--decision", default="（記入してください）", help="決定内容（任意）"
    )
    parser.add_argument("--author", default="AI", help="決定者（デフォルト: AI）")
    parser.add_argument("--related", nargs="*", default=[], help="関連ファイル")
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="決定日（YYYYMMDD形式、デフォルト: 今日）",
    )
    parser.add_argument(
        "--status",
        default="active",
        choices=["active", "deprecated", "superseded"],
        help="ステータス（デフォルト: active）",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="対話型モード有効化（オプション指定なしの場合は自動有効）",
    )
    args = parser.parse_args()

    # 対話型モード判定：必須オプションなし or --interactive フラグ
    is_interactive = (
        not args.title or not args.context or not args.category
    ) or args.interactive

    if is_interactive:
        print("\n" + "=" * 60)
        print("🤖 ADR自動生成スクリプト（対話型）")
        print("=" * 60)

        args.title = interactive_input("📝 ADRのタイトル")
        args.context = interactive_input("📚 背景・理由（複数行の場合は改行で入力）")
        args.category = select_category(CATEGORIES)
        args.author = interactive_input("👤 決定者", default="AI")

        related_input = interactive_input("🔗 関連ファイル（スペース区切り、なければEnter）", default="")
        args.related = related_input.split() if related_input else []

    # 日付パース
    if args.date:
        decision_date = datetime.strptime(args.date, "%Y%m%d")
    else:
        decision_date = datetime.now()

    # 出力ディレクトリ取得（月別ディレクトリ自動作成）
    output_dir = get_output_dir(DECISIONS_DIR, decision_date, args.status)

    # 次の番号を取得
    number = get_next_number(DECISIONS_DIR)

    # ファイル名生成（新命名規則: YYYYMMDD_NNNN_slug_category.md）
    sanitized_title = sanitize_filename(args.title)
    date_str = decision_date.strftime("%Y%m%d")
    filename = f"{date_str}_{number:04d}_{sanitized_title}_{args.category}.md"
    filepath = output_dir / filename

    # 関連ファイルのフォーマット
    if args.related:
        related_files = "\n".join(f"- `{f}`" for f in args.related)
    else:
        related_files = "- （関連ファイルがあれば記入してください）"

    # テンプレート展開
    content = TEMPLATE.format(
        number=f"{number:04d}",
        title=args.title,
        date_formatted=decision_date.strftime("%Y-%m-%d"),
        author=args.author,
        context=args.context,
        decision=args.decision,
        related_files=related_files,
    )

    # ファイル書き込み
    filepath.write_text(content, encoding="utf-8")

    print(f"\n✅ ADR作成完了: {filepath}")
    print(f"\n📝 次のステップ:")
    print(f"   1. {filepath} を編集してください")
    print(f"   2. Status を 'Draft' → 'Accepted' に変更してください")
    print(f"   3. 関連ドキュメントを更新してください")
    print(f"   4. python scripts/generate_index.py  # INDEX.md更新")
    print(f"   5. git add {filepath}")
    print(f"   6. git commit -m 'docs: Add ADR-{number:04d} for {args.title}'")


if __name__ == "__main__":
    main()
