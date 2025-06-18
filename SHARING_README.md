# PDF Knowledge Extractor - 共有版

このアプリケーションは、PDFファイルからAIを使って知見を抽出するツールです。

## 🚀 使用開始方法

### 1. Google Gemini API キーの取得
1. [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセス
2. Googleアカウントでログイン
3. 「Create API Key」をクリック
4. 生成されたAPIキーをコピー

### 2. 設定ファイルの編集
1. アプリケーションフォルダ内の `config.json` を開く
2. `"gemini_api_key"` の値（空文字列 `""`）を取得したAPIキーに置き換える

```json
{
    "gemini_api_key": "ここにあなたのAPIキーを入力",
    "model_name": "gemini-1.5-flash",
    ...
}
```

### 3. アプリケーションの使用
1. PDFファイルをアプリケーションで開く
2. 自動的に知見抽出が開始
3. デスクトップの「PDF knowledge extractor」フォルダに結果が出力

## ⚙️ カスタマイズ

### プロンプトのカスタマイズ
`config.json` の `analysis_prompt` セクションで抽出内容をカスタマイズできます：

```json
{
    "analysis_prompt": {
        "custom_prompt": "この資料からマーケティング戦略の要点を抽出してください",
        "default_categories": {
            "市場分析": "市場規模、成長率、トレンドなど",
            "競合分析": "競合他社の状況、強み弱みなど"
        }
    }
}
```

## 💰 API使用料について
- Google Gemini API は使用量に応じて課金されます
- 月間の無料枠がありますが、大量使用時は料金が発生します
- 詳細は [Google AI の料金ページ](https://ai.google.dev/pricing) を確認してください

## 🔒 セキュリティ注意事項
- APIキーは第三者に共有しないでください
- APIキーを含むconfig.jsonファイルを他人に渡さないでください

## 📋 必要システム
- macOS 10.14 以降
- インターネット接続（AI分析のため）

## ❓ トラブルシューティング
- エラーが発生した場合は、デスクトップの「PDF knowledge extractor」フォルダ内の「debug.log」を確認してください