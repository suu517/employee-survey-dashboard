# 📊 Employee Survey Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/your-username/your-repository)

## 🎯 概要
従業員調査データを可視化するStreamlitベースのWebダッシュボードです。リアルタイムでデータを分析し、美しいグラフと直感的なUIで組織の健康状態を把握できます。

## ✨ 主な機能

### 📈 KPI概要ダッシュボード
- **eNPS (Employee Net Promoter Score)**: 従業員推奨度指標
- **総合満足度**: 1-5スケールでの満足度評価
- **活躍貢献度**: 従業員のパフォーマンス指標
- **勤続意向**: 長期定着の意向度合い

### 🎯 満足度・期待度分析
- **レーダーチャート**: 11カテゴリの満足度可視化
- **満足度ランキング**: カテゴリ別パフォーマンス比較
- **ギャップ分析**: 期待度vs満足度の差分識別

### 🏢 部署別・詳細分析
- 部署ごとのKPI比較
- 個別回答者データの詳細表示
- インタラクティブなデータテーブル

## 🚀 デプロイ方法

### Streamlit Community Cloud (推奨)
1. GitHubリポジトリを作成
2. [Streamlit Community Cloud](https://share.streamlit.io/)にアクセス
3. GitHubアカウントでログイン
4. リポジトリを選択してデプロイ

### ローカル実行
```bash
# 1. 依存パッケージをインストール
pip install -r requirements.txt

# 2. アプリケーション起動
streamlit run app.py

# 3. ブラウザでアクセス
http://localhost:8501
```

## 📁 ファイル構成
```
employee-survey-dashboard/
├── app.py                        # エントリーポイント
├── employee_survey_dashboard.py  # メインアプリケーション
├── data.xlsx                     # 調査データ（暗号化推奨）
├── requirements.txt              # 依存パッケージ
├── .streamlit/
│   ├── config.toml              # Streamlit設定
│   └── secrets.toml             # 秘密情報（Git除外）
├── .gitignore                   # Git除外設定
└── README.md                    # ドキュメント
```

## 🔒 セキュリティ機能
- データファイルの匿名化 (`data.xlsx`)
- Streamlit Community Cloudの認証機能
- 秘密情報の環境変数管理
- CSRF保護有効化

## 🛠 使用技術
- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **Deployment**: Streamlit Community Cloud
- **Security**: Built-in authentication

## 📊 サポートするデータ形式
- Excel形式 (`.xlsx`)
- Responsesシートに調査回答データ
- 106項目の詳細調査に対応
- 1名から数百名規模まで対応

## 🔄 データ更新
1. `data.xlsx`ファイルを更新
2. ダッシュボードの「🔄 データ更新」ボタンをクリック
3. 最新データで自動的に再分析・表示

## 📝 ライセンス
This project is licensed under the MIT License.

## 🤝 サポート
- Issue報告: GitHub Issues
- 機能要望: GitHub Discussions
- セキュリティ: security@yourcompany.com