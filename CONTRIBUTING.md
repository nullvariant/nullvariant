# Contributing to Self-Perfecting OS

Self-Perfecting OSへのコントリビューションをありがとうございます!

> **📊 プロジェクト状況**: このプロジェクトは一部メンテナンスが追いついていない領域があります。  
> 現在のメンテナンス優先度と今後の方向性については **[docs/PROJECT_STATUS.ja.md](docs/PROJECT_STATUS.ja.md)** を参照してください。

## 📋 基本方針

- **編集対象**: `content/AGENT.ja.md`（日本語一次情報）のみ
- **自動生成**: CI が `AGENT.md`（英語）と `spec/agent.spec.yaml` を生成（**⚠️ 現在未稼働**）
- **Changelog**: 全ての変更は `CHANGELOG.md` に記録
- **現状**: 
  - ✅ `content/`と`changelogs/`は積極的に更新中
  - ⚠️ `docs/`配下は一部古い情報あり
  - ❌ CI/CDパイプラインは未稼働（LLM API選定中）

---

## 🚀 クイックスタート

### 1. ローカル環境構築

```bash
# リポジトリクローン
git clone https://github.com/nullvariant/nullvariant.git
cd nullvariant

# Python環境構築
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Anthropic API キー設定
export ANTHROPIC_API_KEY=sk-ant-...
```

### 2. 編集フロー

> **⚠️ 注意**: 現在CI/CDパイプラインが未稼働のため、以下のステップ4は実行不要です。

```bash
# 1. AGENT.ja.md を編集
vim content/AGENT.ja.md

# 2. 目次再生成（必要な場合）
python scripts/gen_toc.py

# 3. CHANGELOG.md 更新
vim CHANGELOG.md  # [Unreleased] セクションに変更を記録

# 4. (現在スキップ) ビルド＆検証
# make gen  # 英訳＆YAML生成 (LLM API選定後に実施予定)
# make val  # 類似度検証 (LLM API選定後に実施予定)

# 5. Commit & Push
git add CHANGELOG.md content/AGENT.ja.md
# ⚠️ CI未稼働のため AGENT.md, spec/agent.spec.yaml は現時点でコミット不要
git commit -m "feat: [変更内容の簡潔な説明]"
git push origin feature/your-feature-name
```

### 3. Pull Request

> **⚠️ 注意**: 現在CI/CDが未稼働のため、自動チェックは実行されません。

- 変更内容を説明
- ~~`make val` が PASS していることを確認~~ (CI稼働後に実施)
- ~~CI チェック（pr-guard.yml）が通過することを確認~~ (CI稼働後に実施)

---

## 📝 Changelog 運用

### バージョニング

本プロジェクトは [Semantic Versioning](https://semver.org/) を採用:

| 種類 | 形式 | 例 | 使用タイミング |
|------|------|----|----|
| **Major** | x.0.0 | 4.0.0 | 破壊的変更、アーキテクチャ再設計 |
| **Minor** | 4.x.0 | 4.1.0 | 新機能追加、大幅強化 |
| **Patch** | 4.1.x | 4.1.1 | バグ修正、小改善、誤字修正 |

### Changelogカテゴリ

変更内容は以下のカテゴリで分類:

- `Added`: 新機能・新セクション追加
- `Enhanced`: 既存機能の改善・拡張
- `Fixed`: バグ修正
- `Changed`: 仕様変更
- `Deprecated`: 非推奨化（将来削除予定）
- `Removed`: 削除
- `Security`: セキュリティ修正

### Changelog記載例

```markdown
## [Unreleased]

### Added
- **Section 6.4**: 新しい感情測定メカニズム
  - 詳細な説明...

### Enhanced
- **Section 2.1**: ペルソナシステムの精密化
  - 改善内容...

### Fixed
- Section 4.3の誤字修正
```

---

## 🔧 開発ツール

### スクリプト

| スクリプト | 用途 | コマンド |
|----------|------|---------|
| `build.py` | 英訳＆YAML生成 | `make gen` |
| `review.py` | 類似度検証 | `make val` |
| `gen_toc.py` | 目次生成 | `python scripts/gen_toc.py` |
| `prepare_note_article.py` | note記事生成 | `python scripts/prepare_note_article.py` |

詳細: [`scripts/README.md`](scripts/README.md)

### Makefile コマンド

```bash
make gen   # build.py 実行（英訳＆YAML生成）
make val   # review.py 実行（類似度検証）
```

---

## 🌐 GitHub Actions

### build.yml
- **トリガー**: `content/AGENT.ja.md` への push
- **処理**: 英訳＆YAML生成 → 自動commit

### pr-guard.yml
- **トリガー**: Pull Request作成時
- **処理**: 
  - 類似度検証（>= 0.86）
  - スキーマ検証
  - Legend同期チェック

### 必要なSecrets
- `OPENAI_API_KEY`: OpenAI API キー

---

## 📂 リポジトリ構成

```
nullvariant/
├── content/
│   ├── AGENT.ja.md               # 🇯🇵 編集対象（日本語一次情報）
│   └── EmotionMood_Dictionary.ja.md
├── AGENT.md                      # 🇬🇧 CI自動生成（英語標準）
├── CHANGELOG.md                  # 📋 バージョン履歴
├── spec/
│   ├── agent.spec.yaml          # CI自動生成
│   └── agent.schema.json
├── changelogs/
│   └── note-archives/           # note公開版アーカイブ
├── docs/
│   ├── OPERATIONS.ja.md         # 運用マニュアル
│   ├── NOTE_SYNC_MANUAL.ja.md   # note同期手順
│   └── PRD_CHANGELOG_MIGRATION.ja.md
├── scripts/
│   ├── build.py
│   ├── gen_toc.py
│   ├── prepare_note_article.py
│   ├── review.py
│   └── prompts/
├── i18n/
│   ├── glossary.yml             # 用語固定辞書
│   └── style/
└── .github/
    └── workflows/
        ├── build.yml
        └── pr-guard.yml
```

---

## ✅ Pull Request チェックリスト

> **⚠️ CI未稼働**: 現在は以下の簡易版チェックリストを使用してください。

### 現在のチェックリスト（Phase 0）

#### 編集前
- [ ] `content/AGENT.ja.md` のみを編集対象としている
- [ ] `CHANGELOG.md` の `[Unreleased]` セクションに変更を記録

#### 編集後
- [ ] 目次が正しく更新されている（必要な場合: `python scripts/gen_toc.py`）
- [ ] マークダウンの構文が正しい（プレビューで確認）

#### PR作成時
- [ ] PR説明に変更内容を明記
- [ ] コミットメッセージが明確

### 将来のチェックリスト（CI稼働後）

以下は現在実行不要です:

- ~~[ ] `make gen` 実行済み（`AGENT.md`, `agent.spec.yaml` 更新）~~
- ~~[ ] `make val` PASS（類似度 >= 0.86）~~
- ~~[ ] 新語は `i18n/glossary.yml` に登録済み~~
- ~~[ ] CI チェックが全て通過~~

---

## 🔗 関連ドキュメント

- [PROJECT_STATUS.ja.md](docs/PROJECT_STATUS.ja.md): **📊 プロジェクト状況・メンテナンス優先度**
- [OPERATIONS.ja.md](docs/OPERATIONS.ja.md): 運用マニュアル（⚠️ 一部情報が古い可能性あり）
- [NOTE_SYNC_MANUAL.ja.md](docs/NOTE_SYNC_MANUAL.ja.md): note同期手順
- [scripts/README.md](scripts/README.md): スクリプト詳細（⚠️ 一部情報が古い可能性あり）

---

## 💡 Tips

### 類似度が低い場合
1. `i18n/glossary.yml` に用語を追加
2. プロンプト (`scripts/prompts/01_en_translate.txt`) を調整
3. 原文の構造を簡潔に

### 新しいセクション追加時
1. AGENT.ja.md に追加
2. 目次を再生成: `python scripts/gen_toc.py`
3. CHANGELOG.md の `Added` カテゴリに記載

---

## 📧 サポート

質問や提案がある場合:
- **Issues**: GitHub Issues で報告
- **Discussions**: 議論や質問

---

_Thank you for contributing to NULLVARIANT OS!_
