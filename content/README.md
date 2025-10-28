# Content Directory

**多言語コンテンツ管理**

---

## 📁 構造

```
content/
├── ja/                    # 🇯🇵 日本語（一次情報）
│   ├── AGENT.md
│   └── EmotionMood_Dictionary.md
└── en/                    # 🇬🇧 英語（自動生成）
    ├── AGENT.md
    └── EmotionMood_Dictionary.md
```

---

## 🎯 設計思想

### 言語別ディレクトリ構造

**原則**:
1. **一次情報は日本語** (`ja/`)
2. **他言語は自動生成** (`en/`, 将来: `zh/`, `fr/` など)
3. **各言語で同じファイル名** (翻訳スクリプトの簡素化)

### 編集ルール

| ディレクトリ | 編集可否 | 更新方法 |
|-------------|---------|---------|
| `content/ja/` | ✅ 編集対象 | 人間が直接編集 |
| `content/en/` | ❌ 編集禁止 | CI/CDで自動生成 |
| 将来の多言語 | ❌ 編集禁止 | CI/CDで自動生成 |

---

## 📝 ファイル説明

### 日本語 (一次情報)

#### `ja/AGENT.md`
- **説明**: Self-Perfecting OS の完全仕様書
- **内容**: 6ペルソナシステム、EBI測定、選択的透過フィルタ等
- **更新頻度**: 毎週〜毎月
- **編集者**: プロジェクトオーナー

#### `ja/EmotionMood_Dictionary.md`
- **説明**: 54種類の基本感情を体系化した辞書
- **内容**: 感情名、定義、ペルソナとの関係
- **更新頻度**: 随時
- **編集者**: プロジェクトオーナー

### 英語 (自動生成)

#### `en/AGENT.md`
- **説明**: 日本語版の自動翻訳
- **生成元**: `ja/AGENT.md`
- **翻訳モデル**: Claude Sonnet 4.5 (予定)
- **状態**: ⚠️ CI未稼働（API選定中）

#### `en/EmotionMood_Dictionary.md`
- **説明**: 感情辞書の自動翻訳
- **生成元**: `ja/EmotionMood_Dictionary.md`
- **翻訳モデル**: Claude Sonnet 4.5 (予定)
- **状態**: ⚠️ CI未稼働（API選定中）

---

## 🔄 翻訳ワークフロー

### 現在の状態（CI未稼働）

```
content/ja/*.md  ─X─>  content/en/*.md
                 (保留中)
```

**理由**:
- LLM API選定中 (Claude Sonnet 4.5 評価中)
- レート制限対応の実装が必要
- 詳細: [docs/project-status.ja.md](../docs/project-status.ja.md)

### 将来の自動化フロー

```
content/ja/*.md
    ↓ (git push)
    ↓ GitHub Actions
    ↓ scripts/build.py
    ↓ Claude Sonnet 4.5 API
    ↓
content/en/*.md (自動生成)
    ↓
AGENT.md (ルートにコピー)
```

---

## 🌍 将来の多言語展開

### 追加予定言語

| 言語 | コード | 優先度 | 状態 |
|-----|-------|-------|------|
| 🇨🇳 中国語 | `zh/` | 中 | 未着手 |
| 🇫🇷 フランス語 | `fr/` | 低 | 未着手 |
| 🇪🇸 スペイン語 | `es/` | 低 | 未着手 |
| 🇩🇪 ドイツ語 | `de/` | 低 | 未着手 |

### 追加手順

```bash
# 新言語追加（例: 中国語）
mkdir content/zh
scripts/build.py --translate ja → zh
```

---

## 🔗 関連ドキュメント

- [README.md](../README.md) - プロジェクト概要
- [docs/project-status.ja.md](../docs/project-status.ja.md) - 現在の状態
- [docs/decisions/active/2025/10/20251028_0001_ci-cd-pause_architecture.md](../docs/decisions/active/2025/10/20251028_0001_ci-cd-pause_architecture.md) - CI/CD一時停止の決定
- [scripts/build.py](../scripts/build.py) - 翻訳スクリプト

---

**最終更新**: 2025-10-28  
**次回更新予定**: CI/CD稼働時
