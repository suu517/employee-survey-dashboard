#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テキスト分析と機械学習による従業員満足度予測機能
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# 日本語の自然言語処理用のライブラリ
try:
    import janome
    from janome.tokenizer import Tokenizer
    TOKENIZER_TYPE = "janome"
    tokenizer = Tokenizer()
except ImportError:
    try:
        import MeCab
        TOKENIZER_TYPE = "mecab"
        mecab = MeCab.Tagger("-Owakati")
    except ImportError:
        TOKENIZER_TYPE = "simple"

def japanese_tokenizer(text):
    """日本語テキストの形態素解析"""
    if not text or pd.isna(text):
        return []
    
    text = str(text).strip()
    if not text:
        return []
    
    try:
        if TOKENIZER_TYPE == "janome":
            tokens = [token.surface for token in tokenizer.tokenize(text, wakati=True)]
        elif TOKENIZER_TYPE == "mecab":
            tokens = mecab.parse(text).strip().split()
        else:
            # シンプルな分割（フォールバック）
            tokens = re.findall(r'\w+', text)
        
        # フィルタリング
        filtered_tokens = []
        for token in tokens:
            if len(token) >= 2 and not token.isdigit():
                filtered_tokens.append(token)
        
        return filtered_tokens
    except Exception:
        return []

def create_sample_data_for_ml(n_samples=150):
    """機械学習用のサンプルデータを作成"""
    np.random.seed(42)
    
    # 主要KPIのサンプルスコア生成
    data = []
    
    # 低満足度グループ (下位20% - ラベル1)
    low_satisfaction_samples = int(n_samples * 0.2)
    for i in range(low_satisfaction_samples):
        recommend_score = np.random.choice([0, 1, 2, 3, 4, 5, 6], p=[0.1, 0.15, 0.2, 0.25, 0.15, 0.1, 0.05])
        overall_satisfaction = np.random.choice([1, 2, 3], p=[0.4, 0.4, 0.2])
        long_term_intention = np.random.choice([1, 2, 3], p=[0.5, 0.3, 0.2])
        sense_of_contribution = np.random.choice([1, 2, 3], p=[0.4, 0.4, 0.2])
        
        # 低満足度に関連するコメントキーワード
        negative_words = [
            "不満", "改善", "問題", "課題", "厳しい", "大変", "困難", "ストレス", "疲労", "負担",
            "不安", "心配", "期待", "希望", "要望", "残業", "忙しい", "時間", "給与", "評価",
            "上司", "同僚", "人間関係", "環境", "制度", "システム", "業務", "仕事", "会社",
            "経営", "戦略", "方針", "変更", "改革", "将来", "キャリア", "成長", "機会"
        ]
        
        comment_words = np.random.choice(negative_words, size=np.random.randint(8, 15), replace=True)
        comment = " ".join(comment_words) + "について不満を感じています。改善が必要だと思います。"
        
        data.append({
            'recommend_score': recommend_score,
            'overall_satisfaction': overall_satisfaction,
            'long_term_intention': long_term_intention,
            'sense_of_contribution': sense_of_contribution,
            'comment': comment,
            'is_low_satisfaction': 1  # 下位20%
        })
    
    # 中・高満足度グループ (上位80% - ラベル0)
    high_satisfaction_samples = n_samples - low_satisfaction_samples
    for i in range(high_satisfaction_samples):
        recommend_score = np.random.choice([6, 7, 8, 9, 10], p=[0.1, 0.2, 0.3, 0.25, 0.15])
        overall_satisfaction = np.random.choice([3, 4, 5], p=[0.3, 0.4, 0.3])
        long_term_intention = np.random.choice([3, 4, 5], p=[0.3, 0.4, 0.3])
        sense_of_contribution = np.random.choice([3, 4, 5], p=[0.3, 0.4, 0.3])
        
        # 高満足度に関連するコメントキーワード
        positive_words = [
            "満足", "良い", "素晴らしい", "優秀", "充実", "安心", "快適", "効率", "成長", "学習",
            "達成", "成功", "評価", "認められる", "支援", "サポート", "協力", "チームワーク", "信頼", "尊重",
            "自由", "裁量", "責任", "挑戦", "機会", "可能性", "将来", "キャリア", "昇進", "昇格",
            "給与", "待遇", "福利厚生", "休暇", "働きやすい", "環境", "制度", "システム", "効率化"
        ]
        
        comment_words = np.random.choice(positive_words, size=np.random.randint(8, 15), replace=True)
        comment = " ".join(comment_words) + "に満足しており、今後も継続して働きたいと思います。"
        
        data.append({
            'recommend_score': recommend_score,
            'overall_satisfaction': overall_satisfaction,
            'long_term_intention': long_term_intention,
            'sense_of_contribution': sense_of_contribution,
            'comment': comment,
            'is_low_satisfaction': 0  # 上位80%
        })
    
    return pd.DataFrame(data)

def identify_low_performers(df, kpi_column, threshold_percentile=20):
    """主要KPIの下位20%を特定"""
    if kpi_column not in df.columns:
        return pd.Series([0] * len(df))
    
    threshold = df[kpi_column].quantile(threshold_percentile / 100)
    return (df[kpi_column] <= threshold).astype(int)

def preprocess_text_features(comments):
    """テキストの前処理と特徴量抽出"""
    if len(comments) == 0:
        return pd.DataFrame()
    
    # テキストのクリーニング
    cleaned_comments = []
    for comment in comments:
        if pd.isna(comment):
            cleaned_comments.append("")
        else:
            # 基本的なクリーニング
            text = str(comment).strip()
            text = re.sub(r'[^\w\s]', ' ', text)  # 句読点を除去
            text = re.sub(r'\s+', ' ', text)  # 複数スペースを単一スペースに
            cleaned_comments.append(text)
    
    # TF-IDF特徴量の作成
    try:
        # カスタム形態素解析器を使用
        def custom_tokenizer(text):
            tokens = japanese_tokenizer(text)
            return tokens if tokens else ['']
        
        # TF-IDF Vectorizer（日本語対応）
        vectorizer = TfidfVectorizer(
            tokenizer=custom_tokenizer,
            max_features=100,  # 上位100個の特徴量
            min_df=2,  # 最低2回出現
            max_df=0.8,  # 80%以上の文書に出現する単語は除外
            ngram_range=(1, 2)  # 1-gram と 2-gram
        )
        
        tfidf_matrix = vectorizer.fit_transform(cleaned_comments)
        feature_names = vectorizer.get_feature_names_out()
        
        # データフレームに変換
        tfidf_df = pd.DataFrame(
            tfidf_matrix.toarray(),
            columns=[f"word_{name}" for name in feature_names]
        )
        
        return tfidf_df, vectorizer
        
    except Exception as e:
        st.error(f"テキスト特徴量抽出エラー: {e}")
        # フォールバック: シンプルな単語カウント
        word_counts = pd.DataFrame()
        return word_counts, None

def train_ensemble_models(X, y):
    """アンサンブル学習モデルの訓練"""
    # データ分割
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    # 複数のモデルを定義
    models = {
        'Decision Tree': DecisionTreeClassifier(random_state=42, max_depth=10),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42, max_depth=6)
    }
    
    trained_models = {}
    model_scores = {}
    
    for name, model in models.items():
        try:
            # モデル訓練
            model.fit(X_train, y_train)
            
            # クロスバリデーション
            cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring='accuracy')
            
            # テストスコア
            test_score = model.score(X_test, y_test)
            
            trained_models[name] = model
            model_scores[name] = {
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'test_score': test_score,
                'train_score': model.score(X_train, y_train)
            }
            
        except Exception as e:
            st.warning(f"{name}の訓練でエラー: {e}")
    
    return trained_models, model_scores, X_test, y_test

def visualize_feature_importance(models, feature_names, top_n=20):
    """特徴量重要性の可視化"""
    fig = make_subplots(
        rows=len(models), cols=1,
        subplot_titles=[f"{name} - 特徴量重要性" for name in models.keys()],
        vertical_spacing=0.1
    )
    
    for i, (model_name, model) in enumerate(models.items(), 1):
        if hasattr(model, 'feature_importances_'):
            # 特徴量重要性を取得
            importances = model.feature_importances_
            
            # 重要性でソート
            indices = np.argsort(importances)[::-1][:top_n]
            top_features = [feature_names[idx] for idx in indices]
            top_importances = importances[indices]
            
            # バープロット追加
            fig.add_trace(
                go.Bar(
                    y=top_features[::-1],  # 重要度順に表示
                    x=top_importances[::-1],
                    orientation='h',
                    name=model_name,
                    showlegend=False
                ),
                row=i, col=1
            )
    
    fig.update_layout(
        height=300 * len(models),
        title="特徴量重要性ランキング（アンサンブルモデル比較）",
        title_font_size=16
    )
    
    fig.update_xaxes(title_text="重要性スコア")
    
    return fig

def create_prediction_summary(models, model_scores):
    """予測結果サマリーの作成"""
    summary_data = []
    
    for model_name, scores in model_scores.items():
        summary_data.append({
            'モデル': model_name,
            '訓練精度': f"{scores['train_score']:.3f}",
            'クロスバリデーション精度': f"{scores['cv_mean']:.3f} (±{scores['cv_std']:.3f})",
            'テスト精度': f"{scores['test_score']:.3f}"
        })
    
    return pd.DataFrame(summary_data)

def show_text_analysis_ml_page():
    """テキスト分析と機械学習ページの表示"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem; text-align: center;">
        <h2 style="margin: 0; color: white;">📝 テキスト分析 × 機械学習</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">コメント分析による満足度予測モデル</p>
    </div>
    """, unsafe_allow_html=True)
    
    # データの準備
    with st.spinner("データを準備中..."):
        # サンプルデータを作成（実際のプロジェクトでは実データを使用）
        df = create_sample_data_for_ml(200)
        st.success(f"分析用データを準備しました: {len(df)}件のサンプル")
    
    # 基本統計
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        low_satisfaction_count = df['is_low_satisfaction'].sum()
        st.metric("下位20%（改善対象）", f"{low_satisfaction_count}人", 
                 f"{low_satisfaction_count/len(df)*100:.1f}%")
    
    with col2:
        avg_recommend = df['recommend_score'].mean()
        st.metric("平均推奨スコア", f"{avg_recommend:.1f}")
    
    with col3:
        avg_satisfaction = df['overall_satisfaction'].mean()
        st.metric("平均総合満足度", f"{avg_satisfaction:.1f}")
    
    with col4:
        unique_words = len(set(' '.join(df['comment']).split()))
        st.metric("ユニーク単語数", f"{unique_words:,}")
    
    # タブで機能を分割
    tab1, tab2, tab3, tab4 = st.tabs(["📊 データ分析", "🤖 機械学習モデル", "📈 特徴量重要性", "🎯 予測結果"])
    
    with tab1:
        st.subheader("データ分布分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # KPI分布
            fig_kpi = px.histogram(
                df, x='overall_satisfaction', color='is_low_satisfaction',
                title="総合満足度の分布", 
                labels={'is_low_satisfaction': '下位20%フラグ'},
                color_discrete_map={0: '#2E86AB', 1: '#F24236'}
            )
            st.plotly_chart(fig_kpi, use_container_width=True)
        
        with col2:
            # 推奨スコア分布
            fig_nps = px.histogram(
                df, x='recommend_score', color='is_low_satisfaction',
                title="推奨スコアの分布",
                labels={'is_low_satisfaction': '下位20%フラグ'},
                color_discrete_map={0: '#2E86AB', 1: '#F24236'}
            )
            st.plotly_chart(fig_nps, use_container_width=True)
        
        # コメントサンプル表示
        st.subheader("コメントサンプル")
        sample_comments = df.sample(5)[['overall_satisfaction', 'recommend_score', 'is_low_satisfaction', 'comment']]
        st.dataframe(sample_comments, use_container_width=True)
    
    with tab2:
        st.subheader("機械学習モデルの訓練")
        
        if st.button("🚀 アンサンブル学習を実行", type="primary"):
            with st.spinner("テキスト特徴量抽出中..."):
                # テキスト特徴量抽出
                text_features, vectorizer = preprocess_text_features(df['comment'])
                
                if len(text_features.columns) > 0:
                    # 数値特徴量と結合
                    numeric_features = df[['recommend_score', 'overall_satisfaction', 'long_term_intention', 'sense_of_contribution']]
                    X = pd.concat([numeric_features, text_features], axis=1)
                    y = df['is_low_satisfaction']
                    
                    st.success(f"特徴量準備完了: {X.shape[1]}個の特徴量")
                    
                    # モデル訓練
                    with st.spinner("アンサンブルモデル訓練中..."):
                        models, scores, X_test, y_test = train_ensemble_models(X, y)
                        
                        # 結果をセッションステートに保存
                        st.session_state['ml_models'] = models
                        st.session_state['ml_scores'] = scores
                        st.session_state['ml_feature_names'] = X.columns.tolist()
                        st.session_state['ml_vectorizer'] = vectorizer
                        
                        st.success("✅ モデル訓練完了！")
                        
                        # モデル性能サマリー
                        summary_df = create_prediction_summary(models, scores)
                        st.subheader("モデル性能比較")
                        st.dataframe(summary_df, use_container_width=True)
                        
                else:
                    st.error("テキスト特徴量の抽出に失敗しました")
    
    with tab3:
        st.subheader("特徴量重要性分析")
        
        if 'ml_models' in st.session_state:
            models = st.session_state['ml_models']
            feature_names = st.session_state['ml_feature_names']
            
            # 特徴量重要性を可視化
            fig_importance = visualize_feature_importance(models, feature_names, top_n=15)
            st.plotly_chart(fig_importance, use_container_width=True)
            
            # トップ特徴量の詳細
            st.subheader("重要な特徴量の詳細")
            
            for model_name, model in models.items():
                if hasattr(model, 'feature_importances_'):
                    st.write(f"**{model_name}**")
                    
                    importances = model.feature_importances_
                    indices = np.argsort(importances)[::-1][:10]
                    
                    top_features_data = []
                    for i, idx in enumerate(indices):
                        feature_name = feature_names[idx]
                        importance = importances[idx]
                        
                        # テキスト特徴量の場合は単語を抽出
                        if feature_name.startswith('word_'):
                            word = feature_name.replace('word_', '')
                            feature_type = "テキスト特徴量"
                        else:
                            word = feature_name
                            feature_type = "数値特徴量"
                        
                        top_features_data.append({
                            'ランク': i + 1,
                            '特徴量': word,
                            'タイプ': feature_type,
                            '重要性': f"{importance:.4f}"
                        })
                    
                    st.dataframe(pd.DataFrame(top_features_data), use_container_width=True)
                    st.write("---")
        else:
            st.info("まず「機械学習モデル」タブでモデルを訓練してください。")
    
    with tab4:
        st.subheader("予測と解釈")
        
        if 'ml_models' in st.session_state:
            models = st.session_state['ml_models']
            
            # アンサンブル予測（多数決）
            st.write("### 🎯 アンサンブル予測の仕組み")
            st.info("""
            **アンサンブル学習の利点:**
            - 複数のモデルを組み合わせることで予測精度が向上
            - 個々のモデルの弱点を補完
            - より堅牢で信頼性の高い予測が可能
            
            **使用モデル:**
            - Decision Tree: 解釈しやすいルールベースモデル
            - Random Forest: 複数の決定木による予測の平均化
            - Gradient Boosting: 段階的に予測を改善する手法
            """)
            
            # サンプル予測
            sample_idx = st.slider("予測対象のサンプルを選択", 0, len(df)-1, 0)
            sample_data = df.iloc[sample_idx]
            
            st.write(f"**選択されたサンプル #{sample_idx}**")
            st.write(f"- 推奨スコア: {sample_data['recommend_score']}")
            st.write(f"- 総合満足度: {sample_data['overall_satisfaction']}")
            st.write(f"- 実際のラベル: {'下位20%' if sample_data['is_low_satisfaction'] else '上位80%'}")
            st.write(f"- コメント: {sample_data['comment'][:100]}...")
            
            # 実装の詳細（実際のプロジェクトでは予測機能を実装）
            st.write("### 📊 予測結果")
            st.info("予測機能は実データでの実装時に追加されます。")
            
        else:
            st.info("まず「機械学習モデル」タブでモデルを訓練してください。")

if __name__ == "__main__":
    show_text_analysis_ml_page()