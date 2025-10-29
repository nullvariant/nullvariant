# ADR-0009: テストファイル管理規則：tests/fixtures/配下に集約

## Status
- **提案日**: 2025-10-29
- **状態**: Accepted
- **決定者**: Claude Code + human

## Context

### 背景
archive_conversation.pyのテスト中、test_conversation.txtがプロジェクトrootに作成され、ファイル配置が散らかった。一時的なテストファイルの配置ルールが不明確だったため、今後の再発防止として明文化が必要。

### 問題点
- スクリプトテスト時に一時ファイルがプロジェクトroot直下に散乱
- `.gitignore` 管理が不明確
- 人間・AIともに同じミスを繰り返すリスク

### 検討した選択肢
1. **選択肢A: tests/fixtures/ に集約 + .gitignore**
   - 標準的なテストディレクトリ構造に従う
   - `.gitignore` でバージョン管理から除外
   
2. **選択肢B: 各スクリプトディレクトリ内にtest/を作成**
   - `scripts/test/` のような構造
   - 分散管理でメンテナンス困難

3. **選択肢C: ルールなし・各自判断**
   - 現状維持
   - 再発必至

## Decision

**選択肢A を採用：すべてのテストファイルは `tests/fixtures/` 配下に配置**

### 具体的なルール

#### 1. ディレクトリ構造
```
tests/
├── README.md              # テストルール説明（このADRへのリンク含む）
├── test_*.py              # ユニットテスト（将来的に作成）→ Git管理
└── fixtures/              # テストデータ
    ├── permanent/         # 固定テストデータ（回帰テスト用）→ Git管理
    │   ├── .gitkeep
    │   └── sample_conversation.md
    └── temporary/         # 一時的な動作確認用 → .gitignore
        ├── .gitkeep
        └── *.test.txt
```

#### 2. ファイル配置規則

**A. 恒久的なテストデータ（Git管理）**
- 配置先: `tests/fixtures/permanent/`
- 用途: ユニットテストの固定データ、回帰テスト用参照データ
- 特徴: Git管理、内容は基本的に変更しない
- 例: `sample_conversation.md`, `expected_frontmatter.yml`

**B. 一時的な動作確認用（.gitignore）**
- 配置先: `tests/fixtures/temporary/`
- 用途: 開発中の手動動作確認、その場限りのテスト
- 特徴: Git管理されない、削除しても問題ない
- 例: `quick_test.test.txt`, `debug_output.test.md`

**判断基準:**
- テストコード（test_*.py）から使う → `permanent/`
- その場限りの確認 → `temporary/`
- 迷ったらまず `temporary/`、後で必要なら昇格

**共通ルール:**
- ✅ **すべてのテストデータは `tests/fixtures/` 配下に配置**
- ❌ **プロジェクトrootに一時ファイルを作成しない**
- ✅ **一時ファイル名は `*.test.txt` または `*.test.md` 推奨**

#### 3. .gitignore 設定
```ignore
# Tests - 一時ファイルのみ除外（permanent/は Git 管理）
tests/fixtures/temporary/
*.test.txt
*.test.md
```

**Git管理されるもの:**
- `tests/test_*.py` - ユニットテスト
- `tests/fixtures/permanent/` - 固定テストデータ
- `tests/README.md` - ルール説明

#### 4. テスト実行例

**一時的な動作確認（temporary/）:**
```bash
# ✅ 正しい例
cat > tests/fixtures/temporary/sample_conversation.test.txt << 'EOF'
テスト用の対話内容
EOF

python scripts/archive_conversation.py \
  --topic "テスト" \
  --conversation-file tests/fixtures/temporary/sample_conversation.test.txt
```

**恒久的なテストデータ（permanent/）- 将来使用:**
```bash
# 固定テストデータ作成（Git管理）
cat > tests/fixtures/permanent/standard_conversation.md << 'EOF'
標準的な対話パターン
EOF

# ユニットテストで使用
# tests/test_archive_conversation.py
def test_with_permanent_fixture():
    with open('tests/fixtures/permanent/standard_conversation.md') as f:
        content = f.read()
    # テスト実行...
```

**❌ 間違った例:**
```bash
# プロジェクトrootに作成してはいけない
cat > test_conversation.txt << 'EOF'  # NG!
EOF
```

#### 5. AI への指示
- スクリプトテスト時は `tests/fixtures/temporary/` にテストファイル作成
- テストコードで使う固定データは `tests/fixtures/permanent/` に配置
- プロジェクトrootに一時ファイル作成禁止
- 人間がrootに一時ファイルを作成しようとしたら警告
- tests/README.md に本ADRへのリンクを記載

#### 6. 設計思想：長期的な美しさ

このルールは「長い目でみて美しいかどうか」を重視して設計されている：

- **2層構造（permanent / temporary）**: 将来のユニットテスト導入を見据えた拡張性
- **明確な責任分離**: 恒久的データと一時的データを混在させない
- **判断基準の明文化**: 人間・AIが迷わず判断できる
- **段階的成長**: 今は `temporary/` だけでも、将来 `permanent/` が自然に育つ

この設計により、プロジェクトが成長しても構造的な美しさを維持できる。

## Consequences

### ✅ メリット
- **ファイル配置の一貫性**: テストファイルの場所が明確
- **バージョン管理の整理**: 一時ファイルのみ `.gitignore`、固定データは Git 管理
- **AI・人間の再発防止**: 明文化されたルールにより同じミスを回避
- **標準的な構造**: 一般的なプロジェクト構造（tests/ディレクトリ）に準拠
- **将来への拡張性**: ユニットテスト導入時にスムーズに移行可能
- **明確な責任分離**: 恒久的データ（permanent/）と一時的データ（temporary/）を混在させない
- **長期的な美しさ**: プロジェクト成長後も構造的美観を維持
- **tests/README.md**: 詳細なルール説明 + 判断基準 + 実行例で学習コスト削減

### ⚠️ デメリット
- **最初の一手間**: テストファイル作成時に `tests/fixtures/temporary/` パス指定が必要
- **判断コスト**: permanent/ と temporary/ のどちらに置くか判断が必要（ただし判断基準は明記）
- **既存習慣の変更**: rootに気軽に作成していた場合は慣れが必要

### 📋 TODO
- [x] tests/fixtures/permanent/ ディレクトリ作成
- [x] tests/fixtures/temporary/ ディレクトリ作成
- [x] .gitignore に tests/fixtures/temporary/, *.test.txt, *.test.md 追加
- [x] tests/README.md 作成（2層構造の説明 + 判断基準 + 実行例）
- [x] tests/fixtures/permanent/.gitkeep 作成
- [x] tests/fixtures/temporary/.gitkeep 作成
- [x] tests/README.md に本ADR-0009へのリンク追加
- [x] scripts/README.md にもテストファイル配置ルールを記載
- [x] .github/copilot-instructions.md にテストファイル配置ルールを追記
- [x] README.md にディレクトリ構造図を追加
- [x] CONTRIBUTING.md にディレクトリ構造図を追加
- [x] DOCUMENTATION_UPDATE_CHECKLIST.md に tests/ 変更時のチェック項目を追加

## Related

### 関連するファイル
- `tests/README.md` - テストルール説明文書
- `tests/fixtures/` - テストデータディレクトリ
- `.gitignore` - テストファイル除外設定
- `scripts/archive_conversation.py` - 本インシデントの発端スクリプト

### 関連する ADR
- ADR-0008: 対話ログ保存システムの設計と実装

### 関連する対話ログ
- `2025-10-29_Codex_CodeLens自動実装インシデントの原因解明.md` - 本ルール策定のきっかけとなったインシデント記録

---

**Status**: Accepted  
**次のアクション**: 実装完了。今後のテストファイル作成時は本ルールに従う。
