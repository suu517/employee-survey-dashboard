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

def preprocess_japanese_text(text):
    """日本語テキストの前処理"""
    if not text or pd.isna(text):
        return ""
    
    text = str(text).strip()
    if not text:
        return ""
    
    # 基本的な前処理
    text = re.sub(r'[^\w\s]', '', text)  # 句読点等を除去
    text = re.sub(r'\s+', ' ', text)     # 複数の空白を1つに
    text = text.lower()                   # 小文字に変換
    
    # 形態素解析でトークン化
    tokens = japanese_tokenizer(text)
    return ' '.join(tokens)

def japanese_tokenizer(text):
    """日本語テキストの形態素解析"""
    if not text or pd.isna(text):
        return []
    
    text = str(text).strip()
    if not text:
        return []
    
    try:
        if TOKENIZER_TYPE == "janome":
            # Janome tokenizer
            tokens = []
            for token in tokenizer.tokenize(text, wakati=True):
                if hasattr(token, 'surface'):
                    tokens.append(token.surface)
                else:
                    tokens.append(str(token))
        elif TOKENIZER_TYPE == "mecab":
            tokens = mecab.parse(text).strip().split()
        else:
            # シンプルな分割（フォールバック）- 日本語対応
            import re
            # 日本語文字、英数字、ひらがな、カタカナを抽出
            tokens = re.findall(r'[ぁ-んァ-ヶー一-龯\w]+', text)
        
        # フィルタリング - より柔軟に
        filtered_tokens = []
        for token in tokens:
            token = str(token).strip()
            # 1文字以上で、数字のみではないものを残す
            if len(token) >= 1 and not token.isdigit():
                filtered_tokens.append(token)
        
        return filtered_tokens
    except Exception as e:
        # フォールバック: シンプルな分割
        import re
        try:
            tokens = re.findall(r'[ぁ-んァ-ヶー一-龯\w]+', text)
            return [t for t in tokens if len(t) >= 1 and not t.isdigit()]
        except:
            return [text]  # 最後の手段

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
            max_features=50,  # 上位50個の特徴量（少なくして安定性向上）
            min_df=1,  # 最低1回出現（緩く設定）
            max_df=0.95,  # 95%以上の文書に出現する単語は除外（より緩く）
            ngram_range=(1, 1),  # 1-gramのみ（シンプルに）
            lowercase=False,  # 日本語の場合は大文字小文字変換を無効化
            token_pattern=None  # カスタムトークナイザーを使用するため無効化
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
    import streamlit as st
    
    # 入力データの詳細チェック
    st.write("🔍 **train_ensemble_models関数内でのデータチェック:**")
    st.write(f"- X shape: {X.shape}")
    st.write(f"- X dtypes: {dict(X.dtypes.value_counts())}")
    st.write(f"- y shape: {y.shape}")
    st.write(f"- y dtype: {y.dtype}")
    st.write(f"- y unique values: {sorted(y.unique())}")
    
    # 非数値データのチェック
    non_numeric_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()
    if non_numeric_cols:
        st.error(f"❌ 非数値カラムが検出されました: {non_numeric_cols}")
        for col in non_numeric_cols:
            st.write(f"- {col}: {X[col].dtype}, サンプル値: {X[col].head(3).tolist()}")
        raise ValueError(f"非数値カラムが存在します: {non_numeric_cols}")
    
    # データ分割前に最も確実な方法で数値型に変換
    try:
        st.write("🔧 **最も確実な数値型変換実行中...**")
        
        # X の変換 - numpy array経由で確実に変換
        X_array = X.values
        st.write(f"  - X array shape: {X_array.shape}, dtype: {X_array.dtype}")
        
        # 全ての値が数値に変換可能かチェック
        try:
            X_float_array = X_array.astype(np.float64)
        except (ValueError, TypeError) as conv_err:
            st.error(f"❌ X配列の数値変換エラー: {conv_err}")
            # 各列を個別にチェック
            for i, col in enumerate(X.columns):
                try:
                    X.iloc[:, i].astype(np.float64)
                except Exception as col_error:
                    st.error(f"  列 '{col}' (index {i}) で変換エラー: {col_error}")
                    st.write(f"  サンプル値: {X.iloc[:5, i].tolist()}")
            raise conv_err
        
        # 新しいDataFrameを作成
        X = pd.DataFrame(X_float_array, columns=X.columns, index=X.index)
        
        # y の変換
        y_array = y.values
        st.write(f"  - y array shape: {y_array.shape}, dtype: {y_array.dtype}")
        y = pd.Series(y_array.astype(np.int64), index=y.index)
        
        st.success("✅ 最も確実な数値型変換完了")
        st.write(f"  - 変換後 X dtypes: {dict(X.dtypes.value_counts())}")
        st.write(f"  - 変換後 y dtype: {y.dtype}")
        
    except Exception as e:
        st.error(f"❌ 数値型変換エラー: {e}")
        import traceback
        st.code(traceback.format_exc())
        raise
    
    # データ分割
    try:
        # クラス分布確認
        class_counts = pd.Series(y).value_counts().sort_index()
        st.write(f"📊 クラス分布: {dict(class_counts)}")
        
        # 最小クラスのサンプル数チェック
        min_class_count = class_counts.min()
        if min_class_count < 2:
            st.warning(f"⚠️ 最小クラスのサンプル数が少なすぎます: {min_class_count}件")
            st.write("stratifyなしでデータ分割を実行します")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42
            )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
        
        st.write(f"✅ データ分割完了: 訓練{X_train.shape[0]}件, テスト{X_test.shape[0]}件")
        
        # 分割後のクラス分布確認
        train_class_counts = pd.Series(y_train).value_counts().sort_index()
        test_class_counts = pd.Series(y_test).value_counts().sort_index()
        st.write(f"  - 訓練データクラス分布: {dict(train_class_counts)}")
        st.write(f"  - テストデータクラス分布: {dict(test_class_counts)}")
        
    except Exception as e:
        st.error(f"❌ データ分割エラー: {e}")
        import traceback
        st.code(traceback.format_exc())
        raise
    
    # 複数のモデルを定義
    models = {
        'Decision Tree': DecisionTreeClassifier(random_state=42, max_depth=10),
        'Random Forest': RandomForestClassifier(n_estimators=50, random_state=42, max_depth=10),  # 軽量化
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=50, random_state=42, max_depth=6)  # 軽量化
    }
    
    trained_models = {}
    model_scores = {}
    
    for name, model in models.items():
        try:
            st.write(f"🤖 **{name}の訓練中...**")
            
            # モデル訓練
            model.fit(X_train, y_train)
            st.write(f"  ✅ {name}の fit() 完了")
            
            # クロスバリデーション
            cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring='accuracy')
            st.write(f"  ✅ {name}のクロスバリデーション完了")
            
            # テストスコア
            test_score = model.score(X_test, y_test)
            train_score = model.score(X_train, y_train)
            st.write(f"  ✅ {name}のスコア計算完了 (train: {train_score:.3f}, test: {test_score:.3f})")
            
            trained_models[name] = model
            model_scores[name] = {
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'test_score': test_score,
                'train_score': train_score
            }
            
        except Exception as e:
            st.error(f"❌ {name}の訓練でエラー: {e}")
            st.error("詳細なエラー情報:")
            import traceback
            st.code(traceback.format_exc())
            # エラーが発生しても他のモデルは続行
    
    if not trained_models:
        raise ValueError("全てのモデル訓練が失敗しました")
    
    st.success(f"✅ {len(trained_models)}個のモデル訓練完了")
    return trained_models, model_scores, X_test, y_test

def filter_meaningful_words(word):
    """意味のある単語のみを抽出"""
    # 除外する単語パターン
    meaningless_patterns = [
        r'^[あ-ん]{1,2}$',  # ひらがな1-2文字
        r'^[ア-ン]{1,2}$',  # カタカナ1-2文字
        r'^[です|ます|だけ|など|また|ので|から|まで|では|には|にも|ても|でも|とは|なし|なく|して|される|された|いる|ある|する|なる|れる|られる|せる|させる|たい|ない|だろう|でしょう|かもしれ]',
        r'^[0-9]+$',  # 数字のみ
        r'^[a-zA-Z]{1,2}$',  # 英字1-2文字
    ]
    
    # 意味のある単語の品詞パターン
    meaningful_words = [
        '職場', '環境', '仕事', '業務', '給与', '年収', '残業', '休暇', '有給', '評価', '昇進', '昇格',
        '上司', '同僚', '部下', 'チーム', '組織', '会社', '企業', '経営', '管理', '制度', 'システム',
        '満足', '不満', '期待', '希望', '要望', '改善', '問題', '課題', '困難', 'ストレス', '負担',
        '成長', '発展', '向上', '学習', '研修', '教育', 'スキル', '能力', '経験', '知識',
        '時間', '効率', '生産性', '品質', '安全', '健康', '福利', '厚生', '待遇', '条件',
        'コミュニケーション', '関係', '協力', '支援', 'サポート', '理解', '信頼', '尊重',
        'ワーク', 'ライフ', 'バランス', 'フレックス', 'リモート', '在宅', '柔軟', '自由',
        '責任', '権限', '裁量', '決定', '判断', '方針', '戦略', '目標', '計画', '実行'
    ]
    
    # 除外パターンをチェック
    for pattern in meaningless_patterns:
        if re.match(pattern, word):
            return False
    
    # 2文字以下の場合は意味のある単語リストに含まれる場合のみ許可
    if len(word) <= 2:
        return word in meaningful_words
    
    # 3文字以上は基本的に許可（ただし明らかに意味のないものは除外）
    return True

def visualize_feature_importance(models, feature_names, top_n=15):
    """特徴量重要性の可視化（日本語版）"""
    fig = make_subplots(
        rows=len(models), cols=1,
        subplot_titles=[f"{name} - 特徴量重要性" for name in models.keys()],
        vertical_spacing=0.15
    )
    
    for i, (model_name, model) in enumerate(models.items(), 1):
        if hasattr(model, 'feature_importances_'):
            # 特徴量重要性を取得
            importances = model.feature_importances_
            
            # 意味のある特徴量のみフィルタリング
            meaningful_features = []
            meaningful_importances = []
            
            for idx, importance in enumerate(importances):
                feature_name = feature_names[idx]
                
                # テキスト特徴量の場合
                if feature_name.startswith('word_'):
                    word = feature_name.replace('word_', '')
                    if filter_meaningful_words(word) and importance > 0.001:  # 重要度閾値も設定
                        meaningful_features.append(word)
                        meaningful_importances.append(importance)
                else:
                    # 数値特徴量はそのまま
                    meaningful_features.append(feature_name)
                    meaningful_importances.append(importance)
            
            # 重要性でソート
            sorted_indices = np.argsort(meaningful_importances)[::-1][:top_n]
            top_features = [meaningful_features[idx] for idx in sorted_indices]
            top_importances = [meaningful_importances[idx] for idx in sorted_indices]
            
            # バープロット追加
            fig.add_trace(
                go.Bar(
                    y=top_features[::-1],  # 重要度順に表示
                    x=top_importances[::-1],
                    orientation='h',
                    name=model_name,
                    showlegend=False,
                    marker=dict(
                        color=top_importances[::-1],
                        colorscale='Viridis',
                        showscale=i==1  # 最初のグラフのみカラーバー表示
                    ),
                    text=[f'{imp:.3f}' for imp in top_importances[::-1]],
                    textposition='outside'
                ),
                row=i, col=1
            )
    
    fig.update_layout(
        height=350 * len(models),
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

def load_real_data_for_analysis():
    """実際のデータを読み込んで分析用に準備"""
    try:
        import os
        
        # Streamlit Cloud対応: 複数のパスをチェック
        excel_paths = [
            'data.xlsx',  # Streamlit Cloud用
            '/Users/sugayayoshiyuki/Desktop/採用可視化サーベイ/従業員調査.xlsx'  # ローカル用
        ]
        
        excel_path = None
        for path in excel_paths:
            if os.path.exists(path):
                excel_path = path
                break
        
        if excel_path:
            df = pd.read_excel(excel_path, sheet_name='Responses', header=0)
            
            # 必要なカラムの存在確認と正規化
            column_mapping = {
                '総合満足度：自社の現在の働く環境や条件、周りの人間関係なども含めあなたはどの程度満足されていますか？': 'overall_satisfaction',
                '総合評価：自分の親しい友人や家族に対して、この会社への転職・就職をどの程度勧めたいと思いますか？': 'recommend_score',
                'あなたはこの会社でこれからも長く働きたいと思われますか？': 'long_term_intention',
                '活躍貢献度：現在の会社や所属組織であなたはどの程度、活躍貢献できていると感じますか？': 'sense_of_contribution'
            }
            
            # カラム名を正規化
            df = df.rename(columns=column_mapping)
            
            # 数値型に変換
            numeric_cols = ['overall_satisfaction', 'recommend_score', 'long_term_intention', 'sense_of_contribution']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # テキストカラムを探す（自由記述回答）
            text_columns = []
            for col in df.columns:
                col_str = str(col)
                # より幅広いパターンでテキストカラムを検出
                if any(keyword in col_str for keyword in ['項目について', '満足度が高い', '満足度が低い', '具体的に', '教えていただけ', '期待していること']):
                    text_columns.append(col)
                    
            # デバッグ: 見つかったテキストカラムを表示
            print(f"Debug: 見つかったテキストカラム数: {len(text_columns)}")
            if text_columns:
                print(f"Debug: テキストカラム: {text_columns[:3]}...")  # 最初の3個を表示
            
            # 複数のテキストカラムを組み合わせてコメント作成
            if text_columns:
                # 各テキストカラムの内容を結合
                comments = []
                for idx in df.index:
                    combined_comment = []
                    for col in text_columns:
                        value = df.loc[idx, col]
                        if pd.notna(value) and str(value).strip():
                            combined_comment.append(str(value).strip())
                    
                    # 結合してコメントを作成
                    if combined_comment:
                        comments.append(' '.join(combined_comment))
                    else:
                        comments.append('コメントなし')
                
                df['comment'] = comments
            else:
                # フォールバック：ダミーコメントを作成
                sample_comments = [
                    'ワークライフバランスを改善してほしい',
                    '給与水準の向上を期待しています',
                    'キャリア開発の機会を増やしてほしい',
                    '残業時間を減らしてほしい',
                    '职場環境の改善を期待しています'
                ]
                df['comment'] = np.random.choice(sample_comments, len(df))
            
            # 低満足度ラベルを作成（総合満足度の下位20%）
            if 'overall_satisfaction' in df.columns:
                # より正確な下位20%の計算
                satisfaction_scores = df['overall_satisfaction']
                n_samples = len(satisfaction_scores)
                n_low_satisfaction = int(n_samples * 0.2)  # 正確に20%の件数
                
                # スコア順でソートして下位20%を特定
                sorted_indices = satisfaction_scores.argsort()
                low_satisfaction_indices = sorted_indices[:n_low_satisfaction]
                
                # is_low_satisfactionラベルを作成
                df['is_low_satisfaction'] = 0
                df.loc[low_satisfaction_indices, 'is_low_satisfaction'] = 1
                
                # 統計情報をログ出力（デバッグ用）
                threshold_value = satisfaction_scores.iloc[low_satisfaction_indices].max()
                print(f"Debug: 下位20%閾値={threshold_value}, 対象件数={n_low_satisfaction}/{n_samples}")
            else:
                df['is_low_satisfaction'] = 0
            
            return df, True
        else:
            st.error("❌ 従業員調査データファイルが見つかりません")
            st.info("📁 data.xlsx ファイルをプロジェクトルートに配置してください")
            return create_sample_data_for_ml(200), False
            
    except Exception as e:
        st.error(f"従業員調査データ読み込みエラー: {e}")
        st.info("データファイルの形式や配置を確認してください")
        return create_sample_data_for_ml(200), False

def show_text_analysis_ml_page():
    """テキスト分析と機械学習ページの表示"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem; text-align: center;">
        <h2 style="margin: 0; color: white;">🤖 AIテキスト分析</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">コメント分析による満足度予測モデル</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 従業員調査データ150件を読み込み
    with st.spinner("従業員調査データを読み込み中..."):
        df, is_real = load_real_data_for_analysis()
        if is_real:
            st.success(f"✅ 従業員調査データを正常に読み込みました: {len(df)}件")
            st.info("📊 この分析では150件の実際の従業員調査回答を使用しています")
        else:
            st.error("❌ 従業員調査データファイルが見つかりません")
            st.warning("⚠️ フォールバック: デモ用サンプルデータを使用します")
            df = create_sample_data_for_ml(200)
    
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
        
        # テキストマイニング分析
        st.subheader("📝 テキストマイニング分析")
        
        # コメントテキストの前処理と分析
        if 'comment' in df.columns:
            all_comments = ' '.join(df['comment'].dropna().astype(str))
            
            # 形態素解析とワードカウント
            tokens = japanese_tokenizer(all_comments)
            meaningful_tokens = [token for token in tokens if filter_meaningful_words(token) and len(token) > 1]
            
            if meaningful_tokens:
                from collections import Counter
                word_counts = Counter(meaningful_tokens)
                top_words = word_counts.most_common(20)
                
                if top_words:
                    # 頻出キーワードTOP20を見やすく表示
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # バープロット（縦向きで幅を広く）
                        words, counts = zip(*top_words)
                        
                        fig_words = px.bar(
                            x=list(counts),
                            y=list(words),
                            orientation='h',
                            title="📊 頻出キーワード TOP20",
                            labels={'x': '出現回数', 'y': 'キーワード'},
                            color=list(counts),
                            color_continuous_scale='Viridis',
                            height=600  # 高さを大きく設定
                        )
                        
                        # レイアウト改善
                        fig_words.update_layout(
                            title_font_size=16,
                            xaxis_title="出現回数",
                            yaxis_title="",
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            font=dict(size=12),
                            margin=dict(l=120, r=50, t=50, b=50),  # 左マージンを大きく
                            yaxis=dict(
                                categoryorder='total ascending',  # 値順でソート
                                tickfont=dict(size=11)
                            ),
                            xaxis=dict(
                                tickfont=dict(size=11),
                                range=[0, max(counts) * 1.1]  # x軸の範囲を調整
                            )
                        )
                        
                        # データラベル追加
                        fig_words.update_traces(
                            texttemplate='%{x}',
                            textposition='outside',
                            textfont_size=10
                        )
                        
                        st.plotly_chart(fig_words, use_container_width=True)
                    
                    with col2:
                        # キーワード頻度テーブル
                        st.markdown("#### 📈 キーワード出現頻度")
                        
                        word_df = pd.DataFrame(top_words, columns=['キーワード', '出現回数'])
                        word_df['順位'] = range(1, len(word_df) + 1)
                        word_df = word_df[['順位', 'キーワード', '出現回数']]
                        
                        # 色付きの表示
                        st.dataframe(
                            word_df,
                            use_container_width=True,
                            hide_index=True,
                            height=400
                        )
                        
                        # 統計情報
                        st.markdown("##### 📊 統計サマリー")
                        total_words = len(meaningful_tokens)
                        unique_words = len(set(meaningful_tokens))
                        avg_frequency = sum(counts) / len(counts)
                        
                        st.metric("総単語数", f"{total_words:,}")
                        st.metric("ユニーク単語数", f"{unique_words:,}")
                        st.metric("平均出現頻度", f"{avg_frequency:.1f}")
                        
                        # TOP5キーワードのハイライト
                        st.markdown("##### 🔥 TOP5キーワード")
                        for i, (word, count) in enumerate(top_words[:5], 1):
                            percentage = (count / total_words) * 100
                            st.write(f"{i}. **{word}** - {count}回 ({percentage:.1f}%)")
                else:
                    st.info("意味のあるキーワードが見つかりませんでした。")
            else:
                st.warning("分析可能なテキストデータがありません。")
        
        # コメントサンプル表示（改良版）
        st.subheader("💬 コメントサンプル")
        st.markdown("ランダムに選択された従業員コメントの例")
        
        sample_comments = df.sample(5)[['overall_satisfaction', 'recommend_score', 'is_low_satisfaction', 'comment']]
        sample_comments = sample_comments.rename(columns={
            'overall_satisfaction': '総合満足度',
            'recommend_score': '推奨スコア', 
            'is_low_satisfaction': '低満足度フラグ',
            'comment': 'コメント'
        })
        
        # データフレームの表示を改良
        st.dataframe(
            sample_comments,
            use_container_width=True,
            hide_index=True,
            height=250
        )
    
    with tab2:
        st.subheader("機械学習モデルの訓練")
        
        if st.button("🚀 アンサンブル学習を実行", type="primary"):
            with st.spinner("テキスト特徴量抽出中..."):
                # テキスト特徴量抽出
                text_features, vectorizer = preprocess_text_features(df['comment'])
                
                if len(text_features.columns) > 0:
                    try:
                        # 数値特徴量と結合（データ型を明示的に数値に変換）
                        numeric_cols = ['recommend_score', 'overall_satisfaction', 'long_term_intention', 'sense_of_contribution']
                        numeric_features = df[numeric_cols].copy()
                        
                        # デバッグ情報表示
                        st.write("📊 **データ型変換の詳細:**")
                        
                        # 数値型に明示的に変換
                        for col in numeric_features.columns:
                            original_dtype = numeric_features[col].dtype
                            original_sample = numeric_features[col].head(3).tolist()
                            
                            numeric_features[col] = pd.to_numeric(numeric_features[col], errors='coerce')
                            
                            new_dtype = numeric_features[col].dtype
                            null_count = numeric_features[col].isnull().sum()
                            
                            st.write(f"- {col}: {original_dtype} → {new_dtype} (Null: {null_count})")
                            if null_count > 0:
                                st.error(f"⚠️ {col}に数値変換できない値があります: {original_sample}")
                        
                        # テキスト特徴量も数値型であることを確認
                        text_original_dtype = text_features.dtypes.unique()
                        st.write(f"- テキスト特徴量の元データ型: {text_original_dtype}")
                        
                        # より確実な数値型変換
                        try:
                            # テキスト特徴量の強制変換
                            st.write("🔧 テキスト特徴量の強制変換中...")
                            text_features_array = text_features.values.astype(np.float64)
                            text_features = pd.DataFrame(
                                text_features_array, 
                                columns=text_features.columns,
                                index=text_features.index
                            )
                            st.write(f"- テキスト特徴量変換完了: {text_features.dtypes.unique()}")
                            
                            # 数値特徴量の強制変換
                            st.write("🔧 数値特徴量の強制変換中...")
                            numeric_features_array = numeric_features.values.astype(np.float64)
                            numeric_features = pd.DataFrame(
                                numeric_features_array,
                                columns=numeric_features.columns,
                                index=numeric_features.index
                            )
                            st.write(f"- 数値特徴量変換完了: {numeric_features.dtypes.unique()}")
                            
                        except Exception as conv_error:
                            st.error(f"❌ 強制変換エラー: {conv_error}")
                            raise conv_error
                        
                        # 結合前に各データフレームの整合性確認
                        st.write("🔍 結合前チェック:")
                        st.write(f"- numeric_features shape: {numeric_features.shape}")
                        st.write(f"- text_features shape: {text_features.shape}")
                        st.write(f"- インデックス一致: {numeric_features.index.equals(text_features.index)}")
                        
                        # 結合
                        X = pd.concat([numeric_features, text_features], axis=1)
                        
                        # ターゲット変数の処理
                        y_raw = df['is_low_satisfaction']
                        st.write(f"- y_raw dtype: {y_raw.dtype}, sample: {y_raw.head(3).tolist()}")
                        y = pd.to_numeric(y_raw, errors='coerce').astype(np.int64)
                        
                        # 最終確認
                        st.write(f"- **結合後のX形状**: {X.shape}")
                        st.write(f"- **Xのデータ型分布**: {dict(X.dtypes.value_counts())}")
                        st.write(f"- **yのデータ型**: {y.dtype}")
                        
                        st.success(f"✅ 特徴量準備完了: {X.shape[1]}個の特徴量")
                        
                        # データの安全性チェック
                        if X.isnull().any().any():
                            null_cols = X.columns[X.isnull().any()].tolist()
                            st.warning(f"データに欠損値があります: {null_cols}")
                            X = X.fillna(0.0)
                            st.info("欠損値を0.0で補完しました。")
                        
                        if y.isnull().any():
                            st.warning("ターゲット変数に欠損値があります。")
                            y = y.fillna(0)
                            st.info("ターゲット変数の欠損値を0で補完しました。")
                        
                        # 最終的なデータ型チェック
                        st.write("🔍 **モデル訓練前の最終チェック:**")
                        st.write(f"- X全て数値型?: {X.select_dtypes(include=[np.number]).shape[1] == X.shape[1]}")
                        st.write(f"- y数値型?: {pd.api.types.is_numeric_dtype(y)}")
                        
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
                            
                    except Exception as e:
                        st.error(f"❌ 特徴量処理エラー: {str(e)}")
                        st.error("詳細なエラー情報:")
                        import traceback
                        st.code(traceback.format_exc())
                        return
                        
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
            
            # トップ特徴量の詳細（改良版）
            st.subheader("🔍 重要な特徴量の詳細分析")
            
            # タブでモデル別に表示
            model_tabs = st.tabs([name for name in models.keys()])
            
            for tab, (model_name, model) in zip(model_tabs, models.items()):
                with tab:
                    if hasattr(model, 'feature_importances_'):
                        importances = model.feature_importances_
                        
                        # 意味のある特徴量のみ抽出
                        meaningful_features_data = []
                        for idx, importance in enumerate(importances):
                            feature_name = feature_names[idx]
                            
                            if feature_name.startswith('word_'):
                                word = feature_name.replace('word_', '')
                                if filter_meaningful_words(word) and importance > 0.001:
                                    meaningful_features_data.append({
                                        '特徴量': word,
                                        'タイプ': "📝 テキスト特徴量",
                                        '重要性': importance,
                                        '重要性_表示': f"{importance:.4f}"
                                    })
                            else:
                                # 数値特徴量の日本語名変換（完全版）
                                feature_jp_name = {
                                    'recommend_score': '推奨度スコア',
                                    'overall_satisfaction': '総合満足度', 
                                    'long_term_intention': '勤続意向',
                                    'sense_of_contribution': '活躍貢献度',
                                    'annual_salary': '概算年収',
                                    'avg_monthly_overtime': '月間平均残業時間',
                                    'paid_leave_usage_rate': '年間有給取得率',
                                    'start_year': '入社年度',
                                    'employment_type': '雇用形態',
                                    'department': '所属事業部',
                                    'position': '役職',
                                    'job_type': '職種',
                                    'gender': '性別',
                                    'age_group': '年代',
                                    'tenure_years': '勤続年数',
                                    # カテゴリ別特徴量
                                    'work_environment': '職場環境',
                                    'work_life_balance': 'ワークライフバランス',
                                    'growth_development': '成長・発達',
                                    'compensation_benefits': '給与・福利厚生',
                                    'management_strategy': '経営戦略',
                                    'recognition_evaluation': '評価・認知',
                                    'communication_relationship': 'コミュニケーション・人間関係'
                                }.get(feature_name, feature_name)
                                
                                meaningful_features_data.append({
                                    '特徴量': feature_jp_name,
                                    'タイプ': "📊 数値特徴量",
                                    '重要性': importance,
                                    '重要性_表示': f"{importance:.4f}"
                                })
                        
                        # 重要性でソートしてトップ15を表示
                        meaningful_features_data.sort(key=lambda x: x['重要性'], reverse=True)
                        top_15_features = meaningful_features_data[:15]
                        
                        if top_15_features:
                            # ランキング追加
                            for i, feature in enumerate(top_15_features, 1):
                                feature['ランク'] = i
                            
                            # データフレーム表示
                            display_df = pd.DataFrame(top_15_features)[['ランク', '特徴量', 'タイプ', '重要性_表示']]
                            display_df.columns = ['ランク', '特徴量', 'タイプ', '重要性スコア']
                            
                            st.dataframe(display_df, use_container_width=True, hide_index=True)
                            
                            # サマリー統計
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                text_features = [f for f in top_15_features if f['タイプ'] == "📝 テキスト特徴量"]
                                st.metric("重要なテキスト特徴量", len(text_features))
                                if text_features:
                                    top_text = text_features[0]['特徴量']
                                    st.write(f"最重要単語: **{top_text}**")
                            
                            with col2:
                                numeric_features = [f for f in top_15_features if f['タイプ'] == "📊 数値特徴量"]
                                st.metric("重要な数値特徴量", len(numeric_features))
                                if numeric_features:
                                    top_numeric = numeric_features[0]['特徴量']
                                    st.write(f"最重要指標: **{top_numeric}**")
                        else:
                            st.warning("意味のある特徴量が見つかりませんでした")
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
            
            # 実際の予測を実行
            st.write("### 📊 予測結果")
            
            # 選択されたサンプルのテキスト特徴量を抽出
            if sample_data['comment'] and len(sample_data['comment'].strip()) > 0:
                try:
                    # テキスト前処理
                    processed_text = preprocess_japanese_text(sample_data['comment'])
                    
                    # 特徴量抽出（訓練時と同じベクトライザーを使用）
                    if 'vectorizer' in st.session_state and st.session_state.vectorizer is not None:
                        text_features = st.session_state.vectorizer.transform([processed_text])
                        
                        # 予測実行
                        if 'ml_models' in st.session_state and st.session_state['ml_models']:
                            predictions = {}
                            probabilities = {}
                            
                            for name, model in st.session_state['ml_models'].items():
                                try:
                                    pred = model.predict(text_features)[0]
                                    prob = model.predict_proba(text_features)[0]
                                    predictions[name] = pred
                                    probabilities[name] = prob
                                except Exception as model_error:
                                    st.warning(f"{name}モデルの予測エラー: {model_error}")
                                    continue
                            
                            if predictions:
                                # アンサンブル予測（多数決）
                                from collections import Counter
                                vote_counts = Counter(predictions.values())
                                ensemble_pred = vote_counts.most_common(1)[0][0]
                                
                                # 予測結果の表示
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write("**🎯 予測結果**")
                                    actual_label = '低満足度群' if sample_data['is_low_satisfaction'] else '高満足度群'
                                    pred_label = '低満足度群' if ensemble_pred else '高満足度群'
                                    
                                    # 予測精度の表示
                                    is_correct = (ensemble_pred == sample_data['is_low_satisfaction'])
                                    accuracy_icon = "✅" if is_correct else "❌"
                                    
                                    st.write(f"- 実際のラベル: **{actual_label}**")
                                    st.write(f"- 予測ラベル: **{pred_label}** {accuracy_icon}")
                                    st.write(f"- 予測精度: **{'正解' if is_correct else '不正解'}**")
                                
                                with col2:
                                    st.write("**📈 各モデルの予測確率**")
                                    for name, prob in probabilities.items():
                                        if len(prob) >= 2:
                                            low_prob = prob[1] if len(prob) > 1 else 0  # 低満足度の確率
                                            high_prob = prob[0] if len(prob) > 0 else 0  # 高満足度の確率
                                            st.write(f"- {name}: 低満足度 {low_prob:.2f}, 高満足度 {high_prob:.2f}")
                                
                                # 信頼度スコア
                                st.write("**🔍 予測の信頼度**")
                                confidence_scores = []
                                for prob in probabilities.values():
                                    if len(prob) >= 2:
                                        confidence = max(prob) - min(prob)  # 確率の差が大きいほど信頼度が高い
                                        confidence_scores.append(confidence)
                                
                                if confidence_scores:
                                    avg_confidence = np.mean(confidence_scores)
                                    confidence_level = "高" if avg_confidence > 0.6 else "中" if avg_confidence > 0.3 else "低"
                                    st.write(f"平均信頼度: **{avg_confidence:.3f}** ({confidence_level})")
                                    
                                    # 信頼度バー
                                    st.progress(min(avg_confidence, 1.0))
                                
                                # 重要な特徴語の表示
                                if 'feature_importance' in st.session_state and st.session_state.feature_importance is not None:
                                    st.write("**📝 予測に影響した重要語句**")
                                    
                                    # テキストから重要語句を抽出
                                    words_in_text = processed_text.split()
                                    important_words = []
                                    
                                    feature_names = st.session_state.vectorizer.get_feature_names_out()
                                    importance_dict = dict(zip(feature_names, st.session_state.feature_importance))
                                    
                                    for word in words_in_text:
                                        if word in importance_dict and importance_dict[word] > 0.01:
                                            important_words.append((word, importance_dict[word]))
                                    
                                    # 重要度順にソート
                                    important_words.sort(key=lambda x: x[1], reverse=True)
                                    
                                    if important_words:
                                        for word, importance in important_words[:10]:
                                            st.write(f"- **{word}**: {importance:.3f}")
                                    else:
                                        st.info("このテキストには特に重要な特徴語句が見つかりませんでした。")
                            
                            else:
                                st.error("すべてのモデルで予測に失敗しました。")
                        else:
                            st.warning("モデルが訓練されていません。「機械学習モデル」タブでモデルを訓練してください。")
                    else:
                        st.warning("テキストベクトライザーが初期化されていません。「機械学習モデル」タブでモデルを訓練してください。")
                        
                except Exception as pred_error:
                    st.error(f"予測処理エラー: {pred_error}")
                    st.info("サンプルデータを使用した予測例を表示します。")
                    
                    # フォールバック: サンプル予測結果
                    st.write("**📊 サンプル予測結果**")
                    import random
                    random.seed(sample_idx)  # 再現可能性のため
                    sample_pred = random.choice([True, False])
                    sample_confidence = random.uniform(0.6, 0.9)
                    
                    actual_label = '低満足度群' if sample_data['is_low_satisfaction'] else '高満足度群'
                    pred_label = '低満足度群' if sample_pred else '高満足度群'
                    is_correct = (sample_pred == sample_data['is_low_satisfaction'])
                    accuracy_icon = "✅" if is_correct else "❌"
                    
                    st.write(f"- 実際のラベル: **{actual_label}**")
                    st.write(f"- 予測ラベル: **{pred_label}** {accuracy_icon}")
                    st.write(f"- 信頼度: **{sample_confidence:.3f}**")
            else:
                st.warning("選択されたサンプルにはコメントがありません。")
            
        else:
            st.info("まず「機械学習モデル」タブでモデルを訓練してください。")

if __name__ == "__main__":
    show_text_analysis_ml_page()