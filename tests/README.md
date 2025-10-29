# Tests Directory

このディレクトリはスクリプトのテスト用ファイルを格納します。

> **📋 詳細ルール**: [ADR-0009: テストファイル管理規則](../docs/decisions/active/2025/10/20251029_0009_テストファイル管理規則testsfixtures配下に集約_process.md)

## ディレクトリ構成

```
tests/
├── README.md              # このファイル
├── test_*.py              # ユニットテスト（将来的に作成）→ Git管理
└── fixtures/              # テストデータ
    ├── permanent/         # 固定テストデータ（回帰テスト用）→ Git管理
    │   └── sample_conversation.md
    └── temporary/         # 一時的な動作確認用 → .gitignore
        └── *.test.txt
```

## ルール

### 1. テストデータの配置

#### A. 恒久的なテストデータ（Git管理）
**配置先**: `tests/fixtures/permanent/`

**用途:**
- ユニットテストで使用する固定データ
- 回帰テスト用の参照データ
- 毎回同じ結果を期待するテストケース

**例:**
```bash
# 固定された会話サンプル（テストで毎回使用）
tests/fixtures/permanent/sample_conversation.md
tests/fixtures/permanent/expected_frontmatter.yml
```

**特徴:**
- ✅ Git管理される（バージョン管理）
- ✅ 内容は基本的に変更しない
- ✅ テストコード（test_*.py）から参照される

---

#### B. 一時的な動作確認用（.gitignore）
**配置先**: `tests/fixtures/temporary/`

**用途:**
- 開発中の手動動作確認
- その場限りのテストデータ
- 実験的な試行

**例:**
```bash
# 手動確認用の一時ファイル
tests/fixtures/temporary/quick_test.test.txt
tests/fixtures/temporary/debug_output.test.md
```

**特徴:**
- ❌ Git管理されない（.gitignore対象）
- ✅ 削除しても問題ない
- ✅ ファイル名は `*.test.txt` または `*.test.md` 推奨

---

### 2. 判断基準：どちらに置くべきか？

| 質問 | permanent/ | temporary/ |
|------|-----------|-----------|
| テストコード（test_*.py）から使う？ | ✅ | ❌ |
| 毎回同じ内容を期待する？ | ✅ | ❌ |
| 削除したら困る？ | ✅ | ❌ |
| 他の人（AI含む）も使う？ | ✅ | ❌ |
| その場限りの確認？ | ❌ | ✅ |
| 実験的・試行錯誤用？ | ❌ | ✅ |

**迷ったら**: まず `temporary/` に置いて、後で必要なら `permanent/` に昇格

---

### 2. .gitignore 設定

**一時ファイルのみ除外:**
```ignore
# Tests - 一時ファイルのみ除外
tests/fixtures/temporary/
*.test.txt
*.test.md
```

**Git管理されるもの:**
- `tests/test_*.py` - ユニットテスト
- `tests/fixtures/permanent/` - 固定テストデータ
- `tests/README.md` - このファイル

---

### 3. プロジェクトroot直下への配置禁止

❌ **絶対にやってはいけない:**
```bash
# プロジェクトrootに一時ファイル作成
/Users/.../nullvariant/test_conversation.txt  # NG!
```

✅ **正しい配置:**
```bash
# tests/fixtures/temporary/ 配下
/Users/.../nullvariant/tests/fixtures/temporary/test_conversation.txt  # OK
```

---

### 4. テスト実行例

#### A. 一時的な動作確認（temporary/）

```bash
# 一時テストファイル作成
cat > tests/fixtures/temporary/sample_conversation.test.txt << 'EOF'
## 対話例
ユーザー: こんにちは
AI: はい、どうぞ
EOF

# テスト実行
python scripts/archive_conversation.py \
  --topic "テスト" \
  --conversation-file tests/fixtures/temporary/sample_conversation.test.txt

# テスト後、ファイルは削除しても問題なし
rm tests/fixtures/temporary/sample_conversation.test.txt
```

---

#### B. 恒久的なテストデータ（permanent/）- 将来的に使用

```bash
# 固定テストデータを作成（Git管理）
cat > tests/fixtures/permanent/standard_conversation.md << 'EOF'
## 標準的な対話パターン
ユーザー: Phase 2を開始します
AI: 承知しました
EOF

# ユニットテストで使用（将来実装）
# tests/test_archive_conversation.py
def test_with_permanent_fixture():
    with open('tests/fixtures/permanent/standard_conversation.md') as f:
        content = f.read()
    # テスト実行...
```

---

#### C. check_token_usage.py のテスト（テストファイル不要）

```bash
# 通常実行（テストファイル不要）
python scripts/check_token_usage.py

# 詳細モード
python scripts/check_token_usage.py --detailed
```

---

### 5. AI への指示（重要）

**Claude Code / GitHub Copilot 向けルール:**

1. ✅ スクリプトテスト時は `tests/fixtures/temporary/` にファイル作成
2. ❌ プロジェクトrootに一時ファイル作成禁止
3. ✅ ファイル名は `*.test.txt` または `*.test.md` 推奨
4. ✅ テストコードで使う固定データは `permanent/` に配置
5. ⚠️ 人間がrootに一時ファイルを作成しようとしたら警告

---

## 注意事項

- テスト用のログファイルは `../nullvariant-writings/docs/log/` に保存される
- `--auto-commit` オプション使用時は実際にGitコミットされるので注意
- テストデータに個人情報を含めない
