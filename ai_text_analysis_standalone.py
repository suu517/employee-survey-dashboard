#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIテキスト分析スタンドアロン版
従業員満足度予測とコメント分析のための機械学習ダッシュボード
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

# ページ設定
st.set_page_config(
    page_title="AI テキスト分析",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 日本語の自然言語処理用のライブラリ
try:
    import janome
    from janome.tokenizer import Tokenizer
    TOKENIZER_TYPE = "janome"
    tokenizer = Tokenizer()
    st.sidebar.success("✅ Janome形態素解析エンジン利用可能")
except ImportError:
    TOKENIZER_TYPE = "simple"
    st.sidebar.warning("⚠️ シンプルトークナイザーを使用")

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

@st.cache_data
def create_enhanced_sample_data(n_samples=200):
    """強化されたサンプルデータを作成"""
    np.random.seed(42)
    
    data = []
    
    # 低満足度グループ (下位20% - ラベル1)
    low_satisfaction_samples = int(n_samples * 0.2)
    for i in range(low_satisfaction_samples):
        recommend_score = np.random.choice([0, 1, 2, 3, 4, 5, 6], p=[0.1, 0.15, 0.2, 0.25, 0.15, 0.1, 0.05])
        overall_satisfaction = np.random.choice([1, 2, 3], p=[0.4, 0.4, 0.2])
        long_term_intention = np.random.choice([1, 2, 3], p=[0.5, 0.3, 0.2])
        sense_of_contribution = np.random.choice([1, 2, 3], p=[0.4, 0.4, 0.2])
        
        # より現実的な不満コメント
        negative_templates = [
            "上司との{keyword1}に問題があり、{keyword2}を感じています。改善が必要です。",
            "{keyword1}の制度に不満があります。特に{keyword2}の点で課題があります。",
            "職場の{keyword1}が厳しく、{keyword2}に負担を感じています。",
            "{keyword1}についての期待と現実にギャップがあり、{keyword2}を感じています。",
            "会社の{keyword1}に関する方針が不明確で、{keyword2}になっています。"
        ]
        
        negative_keywords1 = ["人間関係", "評価制度", "労働環境", "業務量", "キャリアパス", "給与体系", "福利厚生"]
        negative_keywords2 = ["不安", "ストレス", "不満", "疲労", "困惑", "失望", "心配"]
        
        template = np.random.choice(negative_templates)
        keyword1 = np.random.choice(negative_keywords1)
        keyword2 = np.random.choice(negative_keywords2)
        comment = template.format(keyword1=keyword1, keyword2=keyword2)
        
        data.append({
            'recommend_score': recommend_score,
            'overall_satisfaction': overall_satisfaction,
            'long_term_intention': long_term_intention,
            'sense_of_contribution': sense_of_contribution,
            'comment': comment,
            'is_low_satisfaction': 1
        })
    
    # 中・高満足度グループ (上位80% - ラベル0)
    high_satisfaction_samples = n_samples - low_satisfaction_samples
    for i in range(high_satisfaction_samples):
        recommend_score = np.random.choice([6, 7, 8, 9, 10], p=[0.1, 0.2, 0.3, 0.25, 0.15])
        overall_satisfaction = np.random.choice([3, 4, 5], p=[0.3, 0.4, 0.3])
        long_term_intention = np.random.choice([3, 4, 5], p=[0.3, 0.4, 0.3])
        sense_of_contribution = np.random.choice([3, 4, 5], p=[0.3, 0.4, 0.3])
        
        # より現実的な満足コメント
        positive_templates = [
            "{keyword1}に満足しており、{keyword2}を感じています。継続して働きたいです。",
            "職場の{keyword1}が充実していて、{keyword2}に繋がっています。",
            "{keyword1}の制度が整っており、{keyword2}を実感しています。",
            "同僚や上司との{keyword1}が良好で、{keyword2}を感じています。",
            "会社の{keyword1}に共感でき、{keyword2}を持って働いています。"
        ]
        
        positive_keywords1 = ["成長機会", "チームワーク", "評価制度", "労働環境", "福利厚生", "教育制度", "ビジョン"]
        positive_keywords2 = ["やりがい", "達成感", "安心感", "満足感", "成長実感", "誇り", "希望"]
        
        template = np.random.choice(positive_templates)
        keyword1 = np.random.choice(positive_keywords1)
        keyword2 = np.random.choice(positive_keywords2)
        comment = template.format(keyword1=keyword1, keyword2=keyword2)
        
        data.append({
            'recommend_score': recommend_score,
            'overall_satisfaction': overall_satisfaction,
            'long_term_intention': long_term_intention,
            'sense_of_contribution': sense_of_contribution,
            'comment': comment,
            'is_low_satisfaction': 0
        })
    
    return pd.DataFrame(data)

def preprocess_text_features(comments):
    """テキストの前処理と特徴量抽出"""
    if len(comments) == 0:
        return pd.DataFrame(), None
    
    # テキストのクリーニング
    cleaned_comments = []
    for comment in comments:
        if pd.isna(comment):
            cleaned_comments.append("")
        else:
            text = str(comment).strip()
            text = re.sub(r'[^\w\s]', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            cleaned_comments.append(text)
    
    try:
        # カスタム形態素解析器を使用
        def custom_tokenizer(text):
            tokens = japanese_tokenizer(text)
            return tokens if tokens else ['']
        
        vectorizer = TfidfVectorizer(
            tokenizer=custom_tokenizer,
            max_features=50,  # 特徴量数を調整
            min_df=2,
            max_df=0.8,
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = vectorizer.fit_transform(cleaned_comments)
        feature_names = vectorizer.get_feature_names_out()
        
        tfidf_df = pd.DataFrame(
            tfidf_matrix.toarray(),
            columns=[f"word_{name}" for name in feature_names]
        )
        
        return tfidf_df, vectorizer
        
    except Exception as e:
        st.error(f"テキスト特徴量抽出エラー: {e}")
        return pd.DataFrame(), None

def train_ensemble_models(X, y):
    """アンサンブル学習モデルの訓練"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    models = {
        'Decision Tree': DecisionTreeClassifier(random_state=42, max_depth=8),
        'Random Forest': RandomForestClassifier(n_estimators=50, random_state=42, max_depth=8),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=50, random_state=42, max_depth=5)
    }
    
    trained_models = {}
    model_scores = {}
    
    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring='accuracy')
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

def visualize_feature_importance(models, feature_names, top_n=15):
    """特徴量重要性の可視化"""
    fig = make_subplots(
        rows=len(models), cols=1,
        subplot_titles=[f"{name} - Top {top_n} Important Features" for name in models.keys()],
        vertical_spacing=0.15
    )
    
    for i, (model_name, model) in enumerate(models.items(), 1):
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1][:top_n]
            top_features = [feature_names[idx].replace('word_', '') for idx in indices]
            top_importances = importances[indices]
            
            fig.add_trace(
                go.Bar(
                    y=top_features[::-1],
                    x=top_importances[::-1],
                    orientation='h',
                    name=model_name,
                    showlegend=False,
                    marker_color=px.colors.qualitative.Set3[i-1]
                ),
                row=i, col=1
            )
    
    fig.update_layout(
        height=250 * len(models),
        title="🎯 特徴量重要性ランキング（どの単語が低満足度を予測するか）",
        title_font_size=18,
        title_x=0.5
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
            'CV精度': f"{scores['cv_mean']:.3f} (±{scores['cv_std']:.3f})",
            'テスト精度': f"{scores['test_score']:.3f}",
            '汎化性能': "良好" if scores['test_score'] > 0.7 else "要改善"
        })
    
    return pd.DataFrame(summary_data)

def main():
    # メインヘッダー
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem; text-align: center;">
        <h1 style="margin: 0; color: white;">🤖 AI テキスト分析ダッシュボード</h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">従業員コメント×機械学習による満足度予測システム</p>
    </div>
    """, unsafe_allow_html=True)
    
    # サイドバー
    with st.sidebar:
        st.markdown("## 🔧 設定")
        
        # サンプルサイズ設定
        sample_size = st.slider("サンプルデータ数", 100, 500, 200, 50)
        
        # 分析対象KPI選択
        target_kpi = st.selectbox(
            "分析対象KPI",
            ["総合満足度", "推奨スコア", "長期就業意向", "活躍貢献度"]
        )
        
        st.markdown("---")
        st.markdown("### 📖 使用方法")
        st.info("""
        1. **データ準備**: サンプルデータを生成
        2. **モデル訓練**: アンサンブル学習実行
        3. **結果分析**: 特徴量重要性を確認
        4. **解釈**: どの単語が予測に重要かを分析
        """)
        
        st.markdown("---")
        st.markdown("### 🎯 技術仕様")
        st.code("""
        • 形態素解析: Janome
        • 特徴量抽出: TF-IDF
        • アルゴリズム: 
          - Decision Tree
          - Random Forest  
          - Gradient Boosting
        • 評価: Cross Validation
        """)
    
    # データ準備
    with st.spinner("📊 データを準備中..."):
        df = create_enhanced_sample_data(sample_size)
        st.success(f"✅ 分析用データを準備完了: {len(df)}件のサンプル")
    
    # 基本統計
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        low_count = df['is_low_satisfaction'].sum()
        st.metric("💡 改善対象者数", f"{low_count}人", 
                 f"{low_count/len(df)*100:.1f}%")
    
    with col2:
        avg_recommend = df['recommend_score'].mean()
        st.metric("📈 平均推奨スコア", f"{avg_recommend:.1f}")
    
    with col3:
        avg_satisfaction = df['overall_satisfaction'].mean()
        st.metric("😊 平均満足度", f"{avg_satisfaction:.1f}/5")
    
    with col4:
        unique_words = len(set(' '.join(df['comment']).split()))
        st.metric("📝 ユニーク単語数", f"{unique_words:,}")
    
    # タブ設定
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 データ可視化", 
        "🤖 機械学習", 
        "🎯 特徴量分析", 
        "💭 コメント分析"
    ])
    
    with tab1:
        st.markdown("### 📊 データ分布と傾向分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 満足度分布
            fig1 = px.histogram(
                df, x='overall_satisfaction', color='is_low_satisfaction',
                title="満足度分布（改善対象者の特定）",
                labels={'is_low_satisfaction': '改善対象', 'overall_satisfaction': '総合満足度'},
                color_discrete_map={0: '#2E86AB', 1: '#F24236'},
                barmode='overlay'
            )
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # 推奨スコア分布
            fig2 = px.histogram(
                df, x='recommend_score', color='is_low_satisfaction',
                title="推奨スコア分布（NPS分析）",
                labels={'is_low_satisfaction': '改善対象', 'recommend_score': '推奨スコア'},
                color_discrete_map={0: '#2E86AB', 1: '#F24236'},
                barmode='overlay'
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        
        # 相関分析
        st.markdown("### 🔗 KPI間の相関関係")
        corr_data = df[['recommend_score', 'overall_satisfaction', 'long_term_intention', 'sense_of_contribution']].corr()
        
        fig3 = px.imshow(
            corr_data,
            title="KPI相関マトリックス",
            color_continuous_scale='RdBu',
            zmin=-1, zmax=1
        )
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)
        
        # サンプルコメント
        st.markdown("### 💬 コメントサンプル")
        sample_comments = df.sample(5)[['overall_satisfaction', 'recommend_score', 'is_low_satisfaction', 'comment']]
        sample_comments.columns = ['満足度', '推奨スコア', '改善対象', 'コメント']
        st.dataframe(sample_comments, use_container_width=True)
    
    with tab2:
        st.markdown("### 🤖 アンサンブル機械学習モデル")
        
        if st.button("🚀 アンサンブル学習を実行", type="primary", use_container_width=True):
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # ステップ1: テキスト特徴量抽出
            status_text.text("ステップ 1/3: テキスト特徴量抽出中...")
            progress_bar.progress(33)
            
            with st.spinner("形態素解析とTF-IDF特徴量抽出中..."):
                text_features, vectorizer = preprocess_text_features(df['comment'])
                
                if len(text_features.columns) > 0:
                    # ステップ2: 特徴量結合
                    status_text.text("ステップ 2/3: 特徴量結合中...")
                    progress_bar.progress(66)
                    
                    numeric_features = df[['recommend_score', 'overall_satisfaction', 'long_term_intention', 'sense_of_contribution']]
                    X = pd.concat([numeric_features, text_features], axis=1)
                    y = df['is_low_satisfaction']
                    
                    st.success(f"✅ 特徴量準備完了: {X.shape[1]}個の特徴量")
                    
                    # ステップ3: モデル訓練
                    status_text.text("ステップ 3/3: アンサンブルモデル訓練中...")
                    progress_bar.progress(100)
                    
                    with st.spinner("3つのモデルを訓練中..."):
                        models, scores, X_test, y_test = train_ensemble_models(X, y)
                        
                        # セッションステートに保存
                        st.session_state['ml_models'] = models
                        st.session_state['ml_scores'] = scores
                        st.session_state['ml_feature_names'] = X.columns.tolist()
                        st.session_state['ml_vectorizer'] = vectorizer
                        st.session_state['ml_X'] = X
                        st.session_state['ml_y'] = y
                        
                        status_text.text("✅ 訓練完了!")
                        progress_bar.empty()
                        
                        st.balloons()
                        st.success("🎉 アンサンブル学習が完了しました！")
                        
                        # モデル性能サマリー
                        st.markdown("### 📈 モデル性能比較")
                        summary_df = create_prediction_summary(models, scores)
                        st.dataframe(summary_df, use_container_width=True)
                        
                        # 性能評価のガイド
                        st.info("""
                        **性能評価の見方:**
                        - **訓練精度**: 訓練データでの予測精度
                        - **CV精度**: クロスバリデーション精度（汎化性能の指標）
                        - **テスト精度**: 未知データでの予測精度
                        - **汎化性能**: 過学習していないかの判定
                        """)
                        
                else:
                    st.error("❌ テキスト特徴量の抽出に失敗しました")
    
    with tab3:
        st.markdown("### 🎯 特徴量重要性分析")
        
        if 'ml_models' in st.session_state:
            models = st.session_state['ml_models']
            feature_names = st.session_state['ml_feature_names']
            
            # 特徴量重要性可視化
            fig_importance = visualize_feature_importance(models, feature_names, top_n=12)
            st.plotly_chart(fig_importance, use_container_width=True)
            
            # 詳細分析
            st.markdown("### 📝 重要特徴量の詳細分析")
            
            selected_model = st.selectbox(
                "詳細分析するモデルを選択:",
                list(models.keys())
            )
            
            if selected_model in models:
                model = models[selected_model]
                if hasattr(model, 'feature_importances_'):
                    importances = model.feature_importances_
                    indices = np.argsort(importances)[::-1][:15]
                    
                    detailed_data = []
                    for i, idx in enumerate(indices):
                        feature_name = feature_names[idx]
                        importance = importances[idx]
                        
                        if feature_name.startswith('word_'):
                            word = feature_name.replace('word_', '')
                            feature_type = "📝 テキスト特徴量"
                            impact = "この単語が含まれると低満足度になりやすい" if importance > 0.05 else "影響は軽微"
                        else:
                            word = feature_name
                            feature_type = "📊 数値特徴量"
                            impact = "KPI値が低いと低満足度になりやすい" if importance > 0.1 else "影響は軽微"
                        
                        detailed_data.append({
                            'ランク': i + 1,
                            '特徴量': word,
                            'タイプ': feature_type,
                            '重要性': f"{importance:.4f}",
                            '影響度': impact
                        })
                    
                    st.dataframe(pd.DataFrame(detailed_data), use_container_width=True)
            
            # アクションプラン
            st.markdown("### 💡 改善アクションプラン")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎯 優先改善領域")
                st.success("""
                **高重要度のネガティブ単語を特定し、以下を実施:**
                - 該当する問題の根本原因分析
                - 具体的な改善施策の立案
                - 改善効果の測定とモニタリング
                """)
            
            with col2:
                st.markdown("#### 📋 継続施策")
                st.info("""
                **ポジティブ単語の重要度を高めるために:**
                - 満足度向上施策の継続実施
                - 従業員エンゲージメント向上
                - 定期的なフィードバック収集
                """)
                
        else:
            st.info("まず「🤖 機械学習」タブでモデルを訓練してください。")
    
    with tab4:
        st.markdown("### 💭 コメント分析とインサイト")
        
        # コメント長分析
        df['comment_length'] = df['comment'].str.len()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_length = px.histogram(
                df, x='comment_length', color='is_low_satisfaction',
                title="コメント文字数分布",
                labels={'comment_length': '文字数', 'is_low_satisfaction': '改善対象'},
                color_discrete_map={0: '#2E86AB', 1: '#F24236'}
            )
            st.plotly_chart(fig_length, use_container_width=True)
        
        with col2:
            # 感情分析風の可視化
            sentiment_data = []
            for idx, row in df.iterrows():
                positive_words = ['満足', '良い', '素晴らしい', '充実', '成長', 'やりがい', '達成']
                negative_words = ['不満', '問題', '課題', '厳しい', '大変', '困難', 'ストレス']
                
                pos_count = sum(1 for word in positive_words if word in row['comment'])
                neg_count = sum(1 for word in negative_words if word in row['comment'])
                sentiment_score = pos_count - neg_count
                
                sentiment_data.append({
                    'sentiment_score': sentiment_score,
                    'is_low_satisfaction': row['is_low_satisfaction']
                })
            
            sentiment_df = pd.DataFrame(sentiment_data)
            fig_sentiment = px.histogram(
                sentiment_df, x='sentiment_score', color='is_low_satisfaction',
                title="感情スコア分布（正-負単語バランス）",
                labels={'sentiment_score': '感情スコア', 'is_low_satisfaction': '改善対象'},
                color_discrete_map={0: '#2E86AB', 1: '#F24236'}
            )
            st.plotly_chart(fig_sentiment, use_container_width=True)
        
        # キーワード分析
        st.markdown("### 🔍 頻出キーワード分析")
        
        # 低満足度グループのキーワード
        low_comments = df[df['is_low_satisfaction'] == 1]['comment'].str.cat(sep=' ')
        high_comments = df[df['is_low_satisfaction'] == 0]['comment'].str.cat(sep=' ')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⚠️ 改善対象者のキーワード")
            low_words = japanese_tokenizer(low_comments)
            low_word_freq = pd.Series(low_words).value_counts().head(10)
            
            fig_low = px.bar(
                x=low_word_freq.values,
                y=low_word_freq.index,
                orientation='h',
                title="頻出ネガティブキーワード",
                color_discrete_sequence=['#F24236']
            )
            fig_low.update_layout(height=400)
            st.plotly_chart(fig_low, use_container_width=True)
        
        with col2:
            st.markdown("#### ✅ 満足者のキーワード")
            high_words = japanese_tokenizer(high_comments)
            high_word_freq = pd.Series(high_words).value_counts().head(10)
            
            fig_high = px.bar(
                x=high_word_freq.values,
                y=high_word_freq.index,
                orientation='h',
                title="頻出ポジティブキーワード",
                color_discrete_sequence=['#2E86AB']
            )
            fig_high.update_layout(height=400)
            st.plotly_chart(fig_high, use_container_width=True)

if __name__ == "__main__":
    main()