#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
従業員調査可視化ダッシュボード - 実データ対応版
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import os
import re
from collections import Counter
from janome.tokenizer import Tokenizer
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import r2_score, mean_squared_error
try:
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    from statsmodels.stats.diagnostic import durbin_watson, het_breuschpagan
    import statsmodels.api as sm
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
from scipy import stats
from scipy.stats import probplot
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import locale
import warnings
warnings.filterwarnings('ignore')

# ページ設定
st.set_page_config(
    page_title="従業員調査可視化ダッシュボード",
    page_icon="👥",
    layout="wide",
)

# カスタムCSS
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Helvetica', 'Arial', 'Hiragino Sans', 'Yu Gothic', sans-serif;
        background-color: #f8fafc;
    }
    
    h1, h2, h3 {
        color: #1E293B;
    }
    
    /* 改良されたKPIカードスタイル */
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 16px;
        padding: 24px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 16px;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .kpi-title {
        font-size: 13px;
        color: #64748b;
        margin-bottom: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        line-height: 1.2;
    }
    
    .kpi-value {
        font-size: 32px;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 8px;
        line-height: 1.1;
        display: flex;
        align-items: baseline;
    }
    
    .kpi-unit {
        font-size: 18px;
        font-weight: 500;
        color: #64748b;
        margin-left: 4px;
    }
    
    .kpi-change {
        font-size: 13px;
        display: flex;
        align-items: center;
        color: #64748b;
        font-weight: 500;
    }
    
    .kpi-icon {
        margin-right: 8px;
        font-size: 20px;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    
    /* カラー付きKPIカード */
    .kpi-card-green::before {
        background: linear-gradient(90deg, #22c55e, #16a34a);
    }
    .kpi-card-orange::before {
        background: linear-gradient(90deg, #f59e0b, #d97706);
    }
    .kpi-card-red::before {
        background: linear-gradient(90deg, #ef4444, #dc2626);
    }
    .kpi-card-blue::before {
        background: linear-gradient(90deg, #3b82f6, #2563eb);
    }
    
    /* セクションヘッダー改善 */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px 28px;
        border-radius: 16px;
        margin-bottom: 32px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .section-header h2 {
        color: white !important;
        margin: 0;
        font-size: 24px;
        font-weight: 700;
    }
    
    /* データ状況表示の改善 */
    .data-status {
        background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
        border: 1px solid #0ea5e9;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(14, 165, 233, 0.1);
    }
    
    /* サイドバーヘッダー */
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 18px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
    }
    
    .sidebar-logo {
        background-color: rgba(255, 255, 255, 0.95);
        width: 48px;
        height: 48px;
        border-radius: 10px;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-right: 14px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* レスポンシブ対応 */
    @media (max-width: 768px) {
        .kpi-card {
            min-height: 120px;
            padding: 20px 16px;
        }
        .kpi-value {
            font-size: 28px;
        }
        .kpi-title {
            font-size: 12px;
        }
    }
</style>
""", unsafe_allow_html=True)

# データ読み込み関数
@st.cache_data
def load_employee_data():
    """従業員調査データを読み込む（デモ用ダミーデータ）"""
    st.info("📊 デモ用のサンプルデータを使用しています")
    return create_dummy_data()

def load_comment_data():
    """コメントデータを読み込み・処理する"""
    try:
        excel_path = './data.xlsx'
        if not os.path.exists(excel_path):
            return None
            
        # Responsesシートの生データを読み込み
        df_raw = pd.read_excel(excel_path, sheet_name='Responses', header=None)
        
        if len(df_raw) < 3:
            return None
            
        # コメントカラムのインデックス（0ベース）
        comment_columns = {
            '期待コメント': 60,   # 最も期待が高い項目について
            '満足コメント': 103,  # 最も満足度が高い項目について  
            '不満コメント': 104   # 満足度が低い項目について
        }
        
        comments = {}
        for comment_type, col_idx in comment_columns.items():
            if col_idx < len(df_raw.columns):
                # データ行（2行目以降）からコメントを取得
                comment_data = []
                for row_idx in range(2, len(df_raw)):
                    comment = df_raw.iloc[row_idx, col_idx]
                    if pd.notna(comment) and str(comment).strip():
                        comment_data.append(str(comment).strip())
                
                comments[comment_type] = comment_data
        
        return comments
        
    except Exception as e:
        st.error(f"コメントデータ読み込みエラー: {e}")
        return None

def preprocess_japanese_text(text):
    """日本語テキストの前処理"""
    if not text or pd.isna(text):
        return ""
    
    # 文字列に変換
    text = str(text)
    
    # 不要な文字を削除
    text = re.sub(r'[^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3400-\u4DBF\uFF00-\uFFEFa-zA-Z0-9\s]', '', text)
    
    # 余分な空白を削除
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_keywords_janome(texts, min_length=2, max_features=100):
    """Janomeを使って日本語テキストからキーワードを抽出"""
    if not texts:
        return []
    
    # Janomeトークナイザー
    tokenizer = Tokenizer()
    
    # ストップワード（除外する語）
    stop_words = {
        'こと', 'もの', 'ため', 'よう', 'など', 'について', 'において', 'として', 
        'による', 'により', 'に対して', 'それ', 'これ', 'その', 'この', 'ある',
        'いる', 'する', 'なる', 'れる', 'られる', 'です', 'である', 'だ', 'で',
        'は', 'が', 'を', 'に', 'の', 'と', 'や', 'か', 'も', 'から', 'まで',
        '1', '2', '3', '4', '5', 'どちら', '言える', '満足', '期待', '項目'
    }
    
    all_keywords = []
    
    for text in texts:
        if not text:
            continue
            
        # 前処理
        cleaned_text = preprocess_japanese_text(text)
        
        # 形態素解析
        tokens = tokenizer.tokenize(cleaned_text)
        
        for token in tokens:
            # 名詞のみ抽出
            if token.part_of_speech.split(',')[0] in ['名詞']:
                word = token.surface
                
                # 条件に合うものだけ抽出
                if (len(word) >= min_length and 
                    word not in stop_words and
                    not word.isdigit() and
                    not re.match(r'^[ぁ-ん]+$', word)):  # ひらがなのみの語を除外
                    all_keywords.append(word)
    
    # 出現頻度でソート
    keyword_counts = Counter(all_keywords)
    return keyword_counts.most_common(max_features)

def build_cooccurrence_network(texts, min_cooccurrence=1):
    """共起ネットワークを構築"""
    if not texts:
        return None, None
    
    tokenizer = Tokenizer()
    
    # 各テキストから名詞を抽出
    doc_keywords = []
    for text in texts:
        if not text:
            continue
            
        cleaned_text = preprocess_japanese_text(text)
        tokens = tokenizer.tokenize(cleaned_text)
        
        keywords = []
        for token in tokens:
            if token.part_of_speech.split(',')[0] in ['名詞']:
                word = token.surface
                if (len(word) >= 2 and 
                    not word.isdigit() and
                    word not in {'こと', 'もの', 'ため', 'よう', '項目', '満足', '期待'}):
                    keywords.append(word)
        
        doc_keywords.append(keywords)
    
    # 共起関係を計算
    cooccurrence = {}
    for keywords in doc_keywords:
        for i, word1 in enumerate(keywords):
            for j, word2 in enumerate(keywords):
                if i != j:
                    pair = tuple(sorted([word1, word2]))
                    cooccurrence[pair] = cooccurrence.get(pair, 0) + 1
    
    # 最小共起回数でフィルタリング
    filtered_cooccurrence = {pair: count for pair, count in cooccurrence.items() 
                           if count >= min_cooccurrence}
    
    if not filtered_cooccurrence:
        return None, None
    
    # ネットワークグラフを構築
    G = nx.Graph()
    
    for (word1, word2), weight in filtered_cooccurrence.items():
        G.add_edge(word1, word2, weight=weight)
    
    return G, filtered_cooccurrence

def load_timestamp_data():
    """タイムスタンプデータを読み込み・処理する"""
    try:
        excel_path = './data.xlsx'
        if not os.path.exists(excel_path):
            return None
            
        # Responsesシートの生データを読み込み
        df_raw = pd.read_excel(excel_path, sheet_name='Responses', header=None)
        
        if len(df_raw) < 2:
            return None
        
        # タイムスタンプカラムのインデックス（0ベース）
        start_time_col = 2  # 回答開始（列3）
        end_time_col = 3    # 回答完了（列4）
        
        timestamp_data = []
        
        # データ行（2行目以降）からタイムスタンプを取得
        for row_idx in range(1, len(df_raw)):
            try:
                start_time_raw = df_raw.iloc[row_idx, start_time_col]
                end_time_raw = df_raw.iloc[row_idx, end_time_col]
                
                if pd.notna(start_time_raw) and pd.notna(end_time_raw):
                    # 日本語日時フォーマットをパース
                    start_time = parse_japanese_datetime(str(start_time_raw))
                    end_time = parse_japanese_datetime(str(end_time_raw))
                    
                    if start_time and end_time:
                        duration_minutes = (end_time - start_time).total_seconds() / 60
                        timestamp_data.append({
                            'response_id': row_idx,
                            'start_time': start_time,
                            'end_time': end_time,
                            'duration_minutes': duration_minutes,
                            'date': start_time.date(),
                            'hour': start_time.hour,
                            'weekday': start_time.weekday(),
                            'weekday_name': ['月', '火', '水', '木', '金', '土', '日'][start_time.weekday()]
                        })
            except Exception as e:
                continue
        
        return pd.DataFrame(timestamp_data) if timestamp_data else None
        
    except Exception as e:
        st.error(f"タイムスタンプデータ読み込みエラー: {e}")
        return None

def parse_japanese_datetime(datetime_str):
    """日本語の日時文字列を解析してdatetimeオブジェクトに変換"""
    try:
        # "6月 08, 2025 08:39:24 午後" のような形式を処理
        import re
        
        # 月名の日本語を英語に変換
        month_map = {
            '1月': 'Jan', '2月': 'Feb', '3月': 'Mar', '4月': 'Apr',
            '5月': 'May', '6月': 'Jun', '7月': 'Jul', '8月': 'Aug', 
            '9月': 'Sep', '10月': 'Oct', '11月': 'Nov', '12月': 'Dec'
        }
        
        datetime_str = str(datetime_str).strip()
        
        # 午前/午後の処理
        is_pm = '午後' in datetime_str
        datetime_str = datetime_str.replace('午前', '').replace('午後', '').strip()
        
        # 日本語の月を英語に変換
        for jp_month, en_month in month_map.items():
            if jp_month in datetime_str:
                datetime_str = datetime_str.replace(jp_month, en_month)
                break
        
        # パターンマッチングで日時要素を抽出
        pattern = r'(\w+)\s+(\d+),\s+(\d+)\s+(\d+):(\d+):(\d+)'
        match = re.search(pattern, datetime_str)
        
        if match:
            month_str, day, year, hour, minute, second = match.groups()
            
            # 月名を数値に変換
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            month = month_names.index(month_str) + 1
            
            # 午後の場合は12時間を追加（ただし12時の場合は除く）
            hour_int = int(hour)
            if is_pm and hour_int != 12:
                hour_int += 12
            elif not is_pm and hour_int == 12:
                hour_int = 0
            
            return datetime(int(year), month, int(day), hour_int, int(minute), int(second))
        
        return None
        
    except Exception as e:
        return None

def process_real_survey_data(df):
    """実際の調査データを処理する"""
    processed_data = []
    
    # 各回答者のデータを処理
    for idx, row in df.iterrows():
        try:
            # 基本情報の抽出
            employee_data = {
                'response_id': idx + 1,
                'department': extract_value(row, '所属事業部', 'マーケティング部'),
                'position': extract_value(row, '役職', '役職なし'),
                'employment_type': extract_value(row, '雇用形態', '正社員'),
                'job_category': extract_value(row, '職種', 'その他'),
                'start_year': extract_numeric_value(row, '入社年度を教えてください', 2019),
                'annual_salary': extract_numeric_value(row, '概算年収を教えてください', 500),
                'monthly_overtime': extract_numeric_value(row, '1ヶ月当たりの平均残業時間', 20),
                'paid_leave_rate': extract_numeric_value(row, '1年間当たりの平均有給休暇取得率', 50),
            }
            
            # 主要評価指標の抽出
            employee_data.update({
                'nps_score': extract_nps_score(row, '総合評価：自分の親しい友人や家族に対して、この会社への転職・就職をどの程度勧めたいと思いますか？'),
                'overall_satisfaction': extract_satisfaction_score(row, '総合満足度：自社の現在の働く環境や条件、周りの人間関係なども含めあなたはどの程度満足されていますか？'),
                'long_term_intention': extract_satisfaction_score(row, 'あなたはこの会社でこれからも長く働きたいと思われますか？'),
                'contribution_score': extract_satisfaction_score(row, '活躍貢献度：現在の会社や所属組織であなたはどの程度、活躍貢献できていると感じますか？'),
            })
            
            # 期待度項目の抽出
            expectation_items = [
                ('勤務時間', '自分に合った勤務時間で働ける職場'),
                ('休日休暇', '休日休暇がちゃんと取れる職場'),
                ('有給休暇', '有給休暇がちゃんと取れる職場'),
                ('勤務体系', '柔軟な勤務体系（リモートワーク、時短勤務、フレックス制など）のもとで働ける職場'),
                ('昇給昇格', '成果に応じて早期の昇給・昇格が望める職場'),
                ('人間関係', '人間関係が良好な職場'),
                ('働く環境', '働きやすい仕事環境やオフィス環境がある会社'),
                ('成長実感', '専門的なスキルや技術・知識や経験を獲得できる職場'),
                ('将来キャリア', '自分に合った将来のキャリアパスをしっかり設計してくれる職場'),
                ('福利厚生', '充実した福利厚生がある職場'),
                ('評価制度', '自身の行った仕事が正当に評価される職場'),
            ]
            
            for category, keyword in expectation_items:
                expectation_score = extract_expectation_score(row, keyword)
                employee_data[f'{category}_期待度'] = expectation_score
            
            # 満足度項目の抽出
            satisfaction_items = [
                ('勤務時間', '自分に合った勤務時間で働ける'),
                ('休日休暇', '休日休暇がちゃんと取れる'),
                ('有給休暇', '有給休暇がちゃんと取れる'),
                ('勤務体系', '柔軟な勤務体系（リモートワーク、時短勤務、フレックス制など）のもとで働ける'),
                ('昇給昇格', '成果に応じて早期の昇給・昇格が望める体制について'),
                ('人間関係', '人間関係が良好な環境について'),
                ('働く環境', '働きやすい仕事環境やオフィス環境がある会社'),
                ('成長実感', '専門的なスキルや技術・知識や経験の獲得について'),
                ('将来キャリア', '自分に合った将来のキャリアパス設計について'),
                ('福利厚生', '充実した福利厚生について'),
                ('評価制度', '自身の行った仕事が正当に評価される体制について'),
            ]
            
            for category, keyword in satisfaction_items:
                satisfaction_score = extract_satisfaction_score_detailed(row, keyword)
                employee_data[f'{category}_満足度'] = satisfaction_score
            
            processed_data.append(employee_data)
            
        except Exception as e:
            st.warning(f"行 {idx + 1} の処理でエラー: {e}")
            continue
    
    if processed_data:
        return {'employee_data': pd.DataFrame(processed_data)}
    else:
        return create_dummy_data()

def extract_value(row, keyword, default=''):
    """行から特定のキーワードを含む列の値を抽出"""
    for col in row.index:
        if str(col).find(keyword) != -1:
            value = row[col]
            return str(value) if pd.notna(value) else default
    return default

def extract_numeric_value(row, keyword, default=0):
    """行から数値を抽出"""
    for col in row.index:
        if str(col).find(keyword) != -1:
            value = row[col]
            if pd.notna(value):
                try:
                    return float(str(value).replace(',', ''))
                except:
                    return default
    return default

def extract_nps_score(row, keyword):
    """NPS スコアを抽出（0-10の値）"""
    for col in row.index:
        if str(col).find(keyword) != -1:
            value = str(row[col])
            if 'Promoter' in value:
                return 9
            elif 'Passive' in value:
                return 7
            elif 'Detractor' in value:
                return 4
            else:
                try:
                    return int(float(value))
                except:
                    return 5
    return 5

def extract_satisfaction_score(row, keyword):
    """満足度スコアを抽出（1-5の値）"""
    for col in row.index:
        if str(col).find(keyword) != -1:
            value = str(row[col])
            if 'Promoter' in value:
                return 5
            elif 'Passive' in value:
                return 3
            elif 'Detractor' in value:
                return 2
            else:
                try:
                    return int(float(value))
                except:
                    return 3
    return 3

def extract_expectation_score(row, keyword):
    """期待度スコアを抽出"""
    for col in row.index:
        if str(col).find(keyword) != -1:
            value = row[col]
            if pd.notna(value):
                try:
                    return int(float(value))
                except:
                    return 3
    return 3

def extract_satisfaction_score_detailed(row, keyword):
    """詳細満足度スコアを抽出"""
    for col in row.index:
        if str(col).find(keyword) != -1:
            value = row[col]
            if pd.notna(value):
                try:
                    return int(float(value))
                except:
                    return 3
    return 3

def create_dummy_data():
    """ダミーデータを作成（データが読み込めない場合）"""
    np.random.seed(42)
    n_employees = 30
    
    # より現実的なデータ分布を作成
    departments = ['マーケティング部', 'エンジニアリング部', '人事部', '営業部', '総務部', '経理部']
    positions = ['役職なし', 'チームリーダー', 'マネージャー', '主任', '課長']
    groups = ['Aグループ', 'Bグループ', 'Cグループ', 'Dグループ']
    workplaces = ['東京本社', '大阪支社', '名古屋支社', '福岡支社', '横浜オフィス']
    business_types = ['営業系', '技術系', '管理系', 'サポート系', '企画系']
    regions = ['関東', '関西', '中部', '九州', '首都圏']
    job_categories = ['正社員', '契約社員', 'パート', '派遣']
    age_groups = ['20代', '30代', '40代', '50代以上']
    
    # 部署別に特徴のあるデータを生成
    employee_data_list = []
    
    for i in range(n_employees):
        department = np.random.choice(departments, p=[0.25, 0.3, 0.1, 0.25, 0.05, 0.05])
        
        # 部署に応じてポジションの分布を調整
        if department in ['人事部', '総務部', '経理部']:
            position = np.random.choice(positions, p=[0.4, 0.3, 0.2, 0.05, 0.05])
        elif department == 'エンジニアリング部':
            position = np.random.choice(positions, p=[0.6, 0.2, 0.1, 0.05, 0.05])
        else:
            position = np.random.choice(positions, p=[0.5, 0.25, 0.15, 0.05, 0.05])
        
        # 年齢層を設定
        age_group = np.random.choice(age_groups, p=[0.3, 0.35, 0.25, 0.1])
        
        # 年齢に応じて経験年数を調整
        if age_group == '20代':
            start_year = np.random.choice(range(2020, 2025))
            base_salary = np.random.normal(350, 50)
        elif age_group == '30代':
            start_year = np.random.choice(range(2015, 2023))
            base_salary = np.random.normal(500, 80)
        elif age_group == '40代':
            start_year = np.random.choice(range(2010, 2020))
            base_salary = np.random.normal(650, 100)
        else:  # 50代以上
            start_year = np.random.choice(range(2005, 2018))
            base_salary = np.random.normal(750, 120)
        
        # ポジションに応じて給与を調整
        if position == 'マネージャー':
            salary_multiplier = 1.3
        elif position == '課長':
            salary_multiplier = 1.5
        elif position in ['チームリーダー', '主任']:
            salary_multiplier = 1.1
        else:
            salary_multiplier = 1.0
        
        annual_salary = int(max(300, min(1200, base_salary * salary_multiplier)))
        
        # 満足度指標（相関を持たせる）
        base_satisfaction = np.random.normal(3.2, 0.8)
        satisfaction_noise = np.random.normal(0, 0.3)
        
        overall_satisfaction = max(1, min(5, int(base_satisfaction + satisfaction_noise)))
        
        # 推奨スコア（10段階評価）を生成
        base_recommend = 6.5  # 基準推奨スコア
        recommend_noise = np.random.normal(0, 1.2)
        recommend_score = max(1, min(10, int(base_recommend + recommend_noise)))
        
        # nps_scoreも同じ値を使用（10段階スケール）
        nps_score = recommend_score
        
        # その他の指標
        contribution_score = max(1, min(5, int(base_satisfaction + np.random.normal(0, 0.4))))
        long_term_intention = max(1, min(5, int(base_satisfaction + np.random.normal(0, 0.5))))
        
        employee_data_list.append({
            'response_id': i + 1,
            'department': department,
            'position': position,
            'start_year': start_year,
            'annual_salary': annual_salary,
            'monthly_overtime': max(0, min(80, int(np.random.normal(25, 15)))),
            'paid_leave_rate': max(10, min(100, int(np.random.normal(65, 20)))),
            'recommend_score': recommend_score,
            'nps_score': nps_score,
            'overall_satisfaction': overall_satisfaction,
            'long_term_intention': long_term_intention,
            'contribution_score': contribution_score,
            # フィルター用項目
            'group': np.random.choice(groups),
            'workplace': np.random.choice(workplaces),
            'employee_number': f"{((i // 10) * 10 + 1):02d}-{((i // 10 + 1) * 10):02d}",
            'business_type': np.random.choice(business_types),
            'region': np.random.choice(regions),
            'job_category': np.random.choice(job_categories, p=[0.7, 0.15, 0.1, 0.05]),
            'age_group': age_group,
        })
    
    employee_data = pd.DataFrame(employee_data_list)
    
    categories = ['勤務時間', '休日休暇', '有給休暇', '勤務体系', '昇給昇格', '人間関係', 
                 '働く環境', '成長実感', '将来キャリア', '福利厚生', '評価制度']
    
    for category in categories:
        employee_data[f'{category}_期待度'] = np.random.choice(range(1, 6), n_employees)
        employee_data[f'{category}_満足度'] = np.random.choice(range(1, 6), n_employees)
    
    return {'employee_data': employee_data}

@st.cache_data
def calculate_kpis(data):
    """KPIを計算する"""
    if 'employee_data' not in data:
        return {}
    
    df = data['employee_data']
    
    # 推奨度計算（10段階評価の平均値）
    if 'recommend_score' in df.columns:
        nps = df['recommend_score'].mean()
    elif 'nps_score' in df.columns:
        nps = df['nps_score'].mean()
    else:
        nps = 6.5  # デフォルト値
    
    # 満足度カテゴリー
    categories = ['勤務時間', '休日休暇', '有給休暇', '勤務体系', '昇給昇格', '人間関係', 
                 '働く環境', '成長実感', '将来キャリア', '福利厚生', '評価制度']
    
    satisfaction_by_category = {}
    expectation_by_category = {}
    gap_by_category = {}
    
    for category in categories:
        sat_col = f'{category}_満足度'
        exp_col = f'{category}_期待度'
        if sat_col in df.columns and exp_col in df.columns:
            satisfaction_by_category[category] = df[sat_col].mean()
            expectation_by_category[category] = df[exp_col].mean()
            gap_by_category[category] = df[sat_col].mean() - df[exp_col].mean()
    
    return {
        'total_employees': len(df),
        'nps': nps,
        'avg_nps_score': df['nps_score'].mean(),
        'avg_satisfaction': df['overall_satisfaction'].mean(),
        'avg_contribution': df['contribution_score'].mean(),
        'avg_long_term_intention': df['long_term_intention'].mean(),
        'avg_salary': df['annual_salary'].mean(),
        'avg_overtime': df['monthly_overtime'].mean(),
        'avg_leave_usage': df['paid_leave_rate'].mean(),
        'satisfaction_by_category': satisfaction_by_category,
        'expectation_by_category': expectation_by_category,
        'gap_by_category': gap_by_category,
    }

def show_kpi_overview(data, kpis):
    """KPI概要を表示（Streamlit標準コンポーネント使用）"""
    st.header("📊 総合KPIダッシュボード")
    
    # データ状況の表示
    df = data['employee_data']
    
    # 情報ボックス
    st.info(f"📅 **データ最終更新:** {datetime.now().strftime('%Y/%m/%d %H:%M')} | 📋 **調査項目:** {len(df.columns)}項目")
    
    if not kpis:
        st.error("KPIデータが利用できません")
        return
    
    st.subheader("🎯 主要指標")
    
    # メインKPI（Streamlit標準メトリクス使用）
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        nps_delta = "📈 良好" if kpis['nps'] >= 7 else "📉 要改善" if kpis['nps'] <= 5 else "⚠️ 普通"
        nps_color = "normal" if kpis['nps'] >= 7 else "inverse" if kpis['nps'] <= 5 else "off"
        st.metric(
            label="📈 eNPS",
            value=f"{kpis['nps']:.1f}",
            delta=nps_delta,
            delta_color=nps_color
        )
        st.caption("10段階評価")
    
    with col2:
        satisfaction = kpis['avg_satisfaction']
        sat_delta = f"😊 良好" if satisfaction >= 4 else "😔 要改善" if satisfaction <= 2.5 else "😐 普通"
        sat_color = "normal" if satisfaction >= 4 else "inverse" if satisfaction <= 2.5 else "off"
        st.metric(
            label="😊 総合満足度",
            value=f"{satisfaction:.1f}/5",
            delta=sat_delta,
            delta_color=sat_color
        )
        st.caption("全体的な満足度レベル")
    
    with col3:
        contribution = kpis['avg_contribution']
        cont_delta = "⭐ 高い" if contribution >= 4 else "💔 低い" if contribution <= 2.5 else "⚖️ 普通"
        cont_color = "normal" if contribution >= 4 else "inverse" if contribution <= 2.5 else "off"
        st.metric(
            label="⭐ 活躍貢献度",
            value=f"{contribution:.1f}/5",
            delta=cont_delta,
            delta_color=cont_color
        )
        st.caption("パフォーマンス評価")
    
    with col4:
        intention = kpis['avg_long_term_intention']
        int_delta = "🏢 高い" if intention >= 4 else "⚠️ 低い" if intention <= 2.5 else "➖ 普通"
        int_color = "normal" if intention >= 4 else "inverse" if intention <= 2.5 else "off"
        st.metric(
            label="🏢 勤続意向",
            value=f"{intention:.1f}/5",
            delta=int_delta,
            delta_color=int_color
        )
        st.caption("長期定着意向")
    
    st.divider()
    st.subheader("📊 基本指標")
    
    # サブKPI
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 平均年収",
            value=f"{kpis['avg_salary']:.0f}万円",
            delta="年収レベル"
        )
        st.caption("給与水準")
    
    with col2:
        overtime_delta = "⚠️ 多い" if kpis['avg_overtime'] >= 40 else "✅ 適正" if kpis['avg_overtime'] <= 20 else "⚖️ 普通"
        overtime_color = "inverse" if kpis['avg_overtime'] >= 40 else "normal" if kpis['avg_overtime'] <= 20 else "off"
        st.metric(
            label="⏰ 月平均残業時間",
            value=f"{kpis['avg_overtime']:.1f}h",
            delta=overtime_delta,
            delta_color=overtime_color
        )
        st.caption("労働時間管理")
    
    with col3:
        leave_delta = "✅ 良好" if kpis['avg_leave_usage'] >= 80 else "⚠️ 低い" if kpis['avg_leave_usage'] <= 50 else "➖ 普通"
        leave_color = "normal" if kpis['avg_leave_usage'] >= 80 else "inverse" if kpis['avg_leave_usage'] <= 50 else "off"
        st.metric(
            label="🏖️ 有給取得率",
            value=f"{kpis['avg_leave_usage']:.1f}%",
            delta=leave_delta,
            delta_color=leave_color
        )
        st.caption("休暇利用状況")
    
    with col4:
        avg_start_year = kpis.get('avg_start_year', datetime.now().year - 3)
        avg_tenure = datetime.now().year - avg_start_year
        tenure_delta = "📈 ベテラン" if avg_tenure > 5 else "🌱 新鮮" if avg_tenure < 2 else "⚖️ 適度"
        tenure_color = "normal" if 2 <= avg_tenure <= 5 else "off"
        st.metric(
            label="👤 平均勤続年数",
            value=f"{avg_tenure:.1f}年",
            delta=tenure_delta,
            delta_color=tenure_color
        )
        st.caption("平均勤続期間")

def show_satisfaction_analysis(data, kpis):
    """満足度分析を表示"""
    st.header("📈 満足度・期待度分析")
    
    if not kpis or 'satisfaction_by_category' not in kpis:
        st.error("満足度データが利用できません")
        return
    
    tab1, tab2, tab3 = st.tabs(["📊 レーダーチャート", "📋 満足度ランキング", "🎯 期待度ギャップ分析"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # 満足度レーダーチャート
            categories = list(kpis['satisfaction_by_category'].keys())
            satisfaction_values = list(kpis['satisfaction_by_category'].values())
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=satisfaction_values,
                theta=categories,
                fill='toself',
                name='満足度',
                marker_color='rgba(46, 204, 113, 0.6)',
                line=dict(color='rgba(46, 204, 113, 1)', width=3)
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(size=10)),
                    angularaxis=dict(tickfont=dict(size=9))
                ),
                showlegend=False,
                title="満足度レーダーチャート",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 期待度レーダーチャート
            if 'expectation_by_category' in kpis:
                expectation_values = list(kpis['expectation_by_category'].values())
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=satisfaction_values,
                    theta=categories,
                    fill='toself',
                    name='満足度',
                    marker_color='rgba(46, 204, 113, 0.6)',
                    line=dict(color='rgba(46, 204, 113, 1)', width=2)
                ))
                fig.add_trace(go.Scatterpolar(
                    r=expectation_values,
                    theta=categories,
                    fill='toself',
                    name='期待度',
                    marker_color='rgba(52, 152, 219, 0.4)',
                    line=dict(color='rgba(52, 152, 219, 1)', width=2)
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(size=10)),
                        angularaxis=dict(tickfont=dict(size=9))
                    ),
                    title="満足度 vs 期待度",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # 満足度ランキング
        categories = list(kpis['satisfaction_by_category'].keys())
        satisfaction_values = list(kpis['satisfaction_by_category'].values())
        
        satisfaction_df = pd.DataFrame({
            'カテゴリ': categories,
            '満足度': satisfaction_values
        }).sort_values('満足度', ascending=True)
        
        fig = px.bar(
            satisfaction_df,
            x='満足度',
            y='カテゴリ',
            orientation='h',
            title="カテゴリ別満足度ランキング",
            color='満足度',
            color_continuous_scale='RdYlGn',
            range_color=[1, 5],
            height=600
        )
        
        fig.update_layout(
            xaxis_title="満足度 (1-5点)",
            yaxis_title="",
            coloraxis_colorbar=dict(title="満足度スコア")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # 期待度ギャップ分析
        if ('gap_by_category' in kpis and 
            'expectation_by_category' in kpis and 
            len(satisfaction_values) > 0):
            
            try:
                gap_df = pd.DataFrame({
                    'カテゴリ': list(kpis['gap_by_category'].keys()),
                    'ギャップ': list(kpis['gap_by_category'].values()),
                    '満足度': satisfaction_values,
                    '期待度': list(kpis['expectation_by_category'].values())
                })
                
                # データフレームが有効かチェック
                if gap_df.empty or len(gap_df) == 0:
                    st.warning("期待度ギャップ分析用のデータが不足しています。")
                    return
                    
            except Exception as e:
                st.error(f"データの準備中にエラーが発生しました: {str(e)}")
                return
            
            # 4象限プロット（大幅改善版）
            fig = go.Figure()
            
            # 4象限の背景色を追加
            mid_x, mid_y = 3, 3  # 中央値
            
            # 象限分類関数を事前定義
            def classify_quadrant(row):
                x, y = row['満足度'], row['期待度']
                if x >= 3 and y >= 3:
                    return '💪 強み'
                elif x < 3 and y >= 3:
                    return '🔴 優先改善課題'
                elif x >= 3 and y < 3:
                    return '✅ 現状維持項目'
                else:
                    return '⚫ 弱み'
            
            # 象限の背景色（拡大版 - 文字の視認性向上）
            fig.add_shape(
                type="rect", x0=0.5, y0=mid_y, x1=mid_x, y1=5.5,
                fillcolor="rgba(245, 101, 101, 0.15)", line=dict(width=0),
                name="優先改善課題（低満足・高期待）"
            )
            fig.add_shape(
                type="rect", x0=mid_x, y0=mid_y, x1=5.5, y1=5.5,
                fillcolor="rgba(72, 187, 120, 0.15)", line=dict(width=0),
                name="強み（高満足・高期待）"
            )
            fig.add_shape(
                type="rect", x0=0.5, y0=0.5, x1=mid_x, y1=mid_y,
                fillcolor="rgba(237, 137, 54, 0.15)", line=dict(width=0),
                name="弱み（低満足・低期待）"
            )
            fig.add_shape(
                type="rect", x0=mid_x, y0=0.5, x1=5.5, y1=mid_y,
                fillcolor="rgba(159, 122, 234, 0.15)", line=dict(width=0),
                name="現状維持項目（高満足・低期待）"
            )
            
            # 区切り線を追加
            fig.add_hline(y=mid_y, line_dash="dash", line_color="rgba(128, 128, 128, 0.8)", line_width=2)
            fig.add_vline(x=mid_x, line_dash="dash", line_color="rgba(128, 128, 128, 0.8)", line_width=2)
            
            # データポイントを追加（テキスト重なり回避版）
            colors = []
            sizes = []
            symbols = []
            text_positions = []
            
            # テキスト位置を動的に決定する関数
            def get_optimal_text_position(x, y, index, total_points):
                positions = [
                    "top center", "bottom center", "middle left", "middle right",
                    "top left", "top right", "bottom left", "bottom right"
                ]
                
                # 象限ベースの基本位置を決定
                if x >= mid_x and y >= mid_y:  # 強み
                    base_pos = ["top center", "top right", "middle right"]
                elif x < mid_x and y >= mid_y:  # 優先改善課題
                    base_pos = ["top center", "top left", "middle left"]
                elif x >= mid_x and y < mid_y:  # 現状維持項目
                    base_pos = ["bottom center", "bottom right", "middle right"]
                else:  # 弱み
                    base_pos = ["bottom center", "bottom left", "middle left"]
                
                # インデックスに基づいて位置を循環選択
                return base_pos[index % len(base_pos)]
            
            for i, (_, row) in enumerate(gap_df.iterrows()):
                x, y = row['満足度'], row['期待度']
                gap = row['ギャップ']
                
                # 象限によって色を決定（すべて円形で統一）
                if x >= mid_x and y >= mid_y:
                    colors.append('#48BB78')  # 緑 - 強み
                    symbols.append('circle')
                elif x < mid_x and y >= mid_y:
                    colors.append('#F56565')  # 赤 - 優先改善課題
                    symbols.append('circle')
                elif x >= mid_x and y < mid_y:
                    colors.append('#9F7AEA')  # 紫 - 現状維持項目
                    symbols.append('circle')
                else:
                    colors.append('#ED8936')  # オレンジ - 弱み
                    symbols.append('circle')
                
                sizes.append(20)  # 統一サイズ
                text_positions.append(get_optimal_text_position(x, y, i, len(gap_df)))
            
            # マーカーのみを表示（テキストは分離）
            fig.add_trace(go.Scatter(
                x=gap_df['満足度'],
                y=gap_df['期待度'],
                mode='markers',
                marker=dict(
                    size=sizes,
                    color=colors,
                    symbol=symbols,
                    line=dict(width=2, color='white'),
                    opacity=0.9
                ),
                hovertemplate='<b>%{customdata[0]}</b><br>' +
                            '満足度: %{x:.1f}<br>' +
                            '期待度: %{y:.1f}<br>' +
                            'ギャップ: %{customdata[1]:.2f}<br>' +
                            '象限: %{customdata[2]}<extra></extra>',
                customdata=list(zip(
                    gap_df['カテゴリ'], 
                    gap_df['ギャップ'],
                    [classify_quadrant(row) for _, row in gap_df.iterrows()]
                )),
                showlegend=False,
                name=""
            ))
            
            # テキストを個別に追加（重なり回避）
            for i, (_, row) in enumerate(gap_df.iterrows()):
                x, y = row['満足度'], row['期待度']
                category = row['カテゴリ']
                
                # テキストオフセットを計算（象限ラベルとの重なりを避ける）
                offset_map = {
                    "top center": (0, 0.2),
                    "bottom center": (0, -0.2),
                    "middle left": (-0.3, 0),
                    "middle right": (0.3, 0),
                    "top left": (-0.25, 0.2),
                    "top right": (0.25, 0.2),
                    "bottom left": (-0.25, -0.2),
                    "bottom right": (0.25, -0.2)
                }
                
                text_pos = text_positions[i]
                offset_x, offset_y = offset_map.get(text_pos, (0, 0.15))
                
                fig.add_annotation(
                    x=x + offset_x,
                    y=y + offset_y,
                    text=f"<b>{category}</b>",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=1,
                    arrowcolor=colors[i],
                    ax=0,
                    ay=-15 if "top" in text_pos else 15 if "bottom" in text_pos else 0,
                    font=dict(size=9, color='#1f2937'),
                    bgcolor='rgba(255, 255, 255, 0.8)',
                    bordercolor=colors[i],
                    borderwidth=1
                )
            
            # レイアウト設定
            fig.update_layout(
                title={
                    'text': "期待度 vs 満足度 4象限分析",
                    'x': 0.5,
                    'font': {'size': 18, 'color': '#1f2937'}
                },
                xaxis=dict(
                    title="満足度 →",
                    range=[0.3, 5.7],
                    showgrid=True,
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    dtick=1
                ),
                yaxis=dict(
                    title="↑ 期待度",
                    range=[0.3, 5.7],
                    showgrid=True,
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    dtick=1
                ),
                height=650,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            # 象限ラベルを追加（重なり回避のため外側に配置）
            annotations = [
                dict(x=4.8, y=4.8, text="<b>💪 強み</b><br>(高満足・高期待)", 
                     showarrow=False, font=dict(size=10, color='#22543d'), 
                     bgcolor='rgba(72, 187, 120, 0.2)', bordercolor='#48BB78',
                     xanchor='center', yanchor='middle'),
                dict(x=1.2, y=4.8, text="<b>🔴 優先改善課題</b><br>(低満足・高期待)", 
                     showarrow=False, font=dict(size=10, color='#742a2a'), 
                     bgcolor='rgba(245, 101, 101, 0.2)', bordercolor='#F56565',
                     xanchor='center', yanchor='middle'),
                dict(x=4.8, y=1.2, text="<b>✅ 現状維持項目</b><br>(高満足・低期待)", 
                     showarrow=False, font=dict(size=10, color='#553c9a'), 
                     bgcolor='rgba(159, 122, 234, 0.2)', bordercolor='#9F7AEA',
                     xanchor='center', yanchor='middle'),
                dict(x=1.2, y=1.2, text="<b>⚫ 弱み</b><br>(低満足・低期待)", 
                     showarrow=False, font=dict(size=10, color='#9c4221'), 
                     bgcolor='rgba(237, 137, 54, 0.2)', bordercolor='#ED8936',
                     xanchor='center', yanchor='middle')
            ]
            
            for ann in annotations:
                fig.add_annotation(**ann)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 象限別の説明
            st.info("""
            **📊 4象限の解釈**
            - 💪 **強み（右上）**: 満足度・期待度ともに高い項目。競争優位性の源泉
            - 🔴 **優先改善課題（左上）**: 期待は高いが満足度が低い項目。最優先で改善が必要
            - ✅ **現状維持項目（右下）**: 満足度は高いが期待度が低い項目。現状の品質を維持
            - ⚫ **弱み（左下）**: 期待・満足ともに低い項目。長期的な改善検討が必要
            """)
            
            # ギャップテーブル（改善版）
            st.subheader("📋 象限別分析結果")
            
            try:
                gap_display = gap_df.copy()
                gap_display['象限'] = gap_display.apply(classify_quadrant, axis=1)
                gap_display['ギャップ評価'] = gap_display['ギャップ'].apply(
                    lambda x: '😊 満足>期待' if x > 0.3 else '😔 期待>満足' if x < -0.3 else '😐 ほぼ同等'
                )
                
                # 優先度を設定
                priority_map = {'🔴 優先改善課題': 1, '⚫ 弱み': 2, '✅ 現状維持項目': 3, '💪 強み': 4}
                gap_display['優先度'] = gap_display['象限'].map(priority_map)
                
                # NaNの処理
                gap_display['優先度'] = gap_display['優先度'].fillna(5)
                
                # 必要なカラムが存在するかチェック
                required_columns = ['カテゴリ', '満足度', '期待度', 'ギャップ', '象限', 'ギャップ評価', '優先度']
                if all(col in gap_display.columns for col in required_columns):
                    # 表示用に整理
                    display_df = gap_display[required_columns].sort_values('優先度')
                    display_df = display_df.round({'満足度': 1, '期待度': 1, 'ギャップ': 2})
                    display_df = display_df.drop_duplicates().reset_index(drop=True)
                    
                    # 優先度カラムを除外して表示
                    st.dataframe(
                        display_df[['カテゴリ', '満足度', '期待度', 'ギャップ', '象限', 'ギャップ評価']], 
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.error("必要なデータカラムが不足しています。")
                    
            except Exception as e:
                st.error(f"テーブル表示中にエラーが発生しました: {str(e)}")
                st.info("基本的な満足度・期待度データは利用可能です。詳細な分析表示のみエラーが発生しています。")
                
        else:
            st.warning("期待度ギャップ分析に必要なデータが不足しています。満足度データまたは期待度データが利用できません。")

def show_text_mining_analysis():
    """テキストマイニング分析を表示"""
    st.header("📝 テキストマイニング分析")
    
    # コメントデータの読み込み
    with st.spinner("💬 コメントデータを読み込み中..."):
        comments = load_comment_data()
    
    if not comments:
        st.error("コメントデータが読み込めませんでした。")
        return
    
    # タブを作成
    tabs = st.tabs(["📊 キーワード分析", "🕸️ 共起ネットワーク", "☁️ ワードクラウド", "📋 コメント一覧"])
    
    with tabs[0]:  # キーワード分析
        st.subheader("🔍 頻出キーワード分析")
        
        comment_type = st.selectbox(
            "分析するコメント種別を選択:",
            list(comments.keys()),
            key="keyword_analysis_type"
        )
        
        if comment_type in comments and comments[comment_type]:
            keywords = extract_keywords_janome(comments[comment_type], max_features=20)
            
            if keywords:
                # データフレームに変換
                keyword_df = pd.DataFrame(keywords, columns=['キーワード', '出現回数'])
                
                # 棒グラフで表示
                fig = px.bar(
                    keyword_df, 
                    x='出現回数', 
                    y='キーワード',
                    orientation='h',
                    title=f"{comment_type} - 頻出キーワードランキング",
                    color='出現回数',
                    color_continuous_scale='viridis'
                )
                fig.update_layout(height=600, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
                
                # テーブル表示
                st.subheader("📋 キーワード詳細")
                st.dataframe(keyword_df, use_container_width=True, hide_index=True)
            else:
                st.info("抽出されたキーワードがありません。")
        else:
            st.info(f"{comment_type}のデータがありません。")
    
    with tabs[1]:  # 共起ネットワーク
        st.subheader("🕸️ 共起ネットワーク分析")
        
        comment_type = st.selectbox(
            "分析するコメント種別を選択:",
            list(comments.keys()),
            key="network_analysis_type"
        )
        
        min_cooccurrence = st.slider("最小共起回数", 1, 5, 1)
        
        if comment_type in comments and comments[comment_type]:
            G, cooccurrence = build_cooccurrence_network(comments[comment_type], min_cooccurrence)
            
            if G and len(G.nodes()) > 0:
                # NetworkXを使ってネットワーク図を作成
                pos = nx.spring_layout(G, k=3, iterations=50)
                
                # エッジの情報を取得
                edge_x = []
                edge_y = []
                edge_info = []
                
                for edge in G.edges():
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                    weight = G[edge[0]][edge[1]]['weight']
                    edge_info.append(f"{edge[0]} - {edge[1]}: {weight}回")
                
                # ノードの情報を取得
                node_x = []
                node_y = []
                node_text = []
                node_size = []
                
                for node in G.nodes():
                    x, y = pos[node]
                    node_x.append(x)
                    node_y.append(y)
                    node_text.append(node)
                    node_size.append(10 + G.degree(node) * 5)
                
                # Plotlyでネットワーク図を作成
                fig = go.Figure()
                
                # エッジを追加
                fig.add_trace(go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=2, color='#888'),
                    hoverinfo='none',
                    mode='lines',
                    showlegend=False
                ))
                
                # ノードを追加
                fig.add_trace(go.Scatter(
                    x=node_x, y=node_y,
                    mode='markers+text',
                    hoverinfo='text',
                    text=node_text,
                    textposition="middle center",
                    textfont=dict(size=12, color='white'),
                    marker=dict(
                        size=node_size,
                        color=node_size,
                        colorscale='viridis',
                        line=dict(width=2, color='white')
                    ),
                    showlegend=False
                ))
                
                fig.update_layout(
                    title=f"{comment_type} - 共起ネットワーク図",
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text="ノードサイズ: 接続数、線: 共起関係",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ,
                        xanchor="left", yanchor="bottom",
                        font=dict(color="gray", size=12)
                    )],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 共起関係の詳細
                st.subheader("📊 共起関係詳細")
                cooccurrence_df = pd.DataFrame([
                    {'語1': pair[0], '語2': pair[1], '共起回数': count}
                    for pair, count in sorted(cooccurrence.items(), key=lambda x: x[1], reverse=True)
                ])
                st.dataframe(cooccurrence_df, use_container_width=True, hide_index=True)
            else:
                st.info("共起ネットワークを構築できませんでした。最小共起回数を下げてみてください。")
        else:
            st.info(f"{comment_type}のデータがありません。")
    
    with tabs[2]:  # ワードクラウド
        st.subheader("☁️ ワードクラウド")
        
        comment_type = st.selectbox(
            "分析するコメント種別を選択:",
            list(comments.keys()),
            key="wordcloud_analysis_type"
        )
        
        if comment_type in comments and comments[comment_type]:
            # キーワードを抽出
            keywords = extract_keywords_janome(comments[comment_type], max_features=50)
            
            if keywords:
                # ワードクラウド用のデータを準備
                wordcloud_dict = dict(keywords)
                
                try:
                    # ワードクラウドを生成
                    wc = WordCloud(
                        font_path=None,  # システムフォントを使用
                        width=800, height=400,
                        background_color='white',
                        max_words=50,
                        colormap='viridis'
                    ).generate_from_frequencies(wordcloud_dict)
                    
                    # matplotlib で表示
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.imshow(wc, interpolation='bilinear')
                    ax.axis('off')
                    ax.set_title(f'{comment_type} - ワードクラウド', fontsize=16, pad=20)
                    
                    st.pyplot(fig)
                    
                except Exception as e:
                    st.warning(f"ワードクラウドの生成に失敗しました: {e}")
                    st.info("代わりにキーワードリストを表示します:")
                    keyword_df = pd.DataFrame(keywords, columns=['キーワード', '出現回数'])
                    st.dataframe(keyword_df, use_container_width=True, hide_index=True)
            else:
                st.info("キーワードが抽出できませんでした。")
        else:
            st.info(f"{comment_type}のデータがありません。")
    
    with tabs[3]:  # コメント一覧
        st.subheader("📋 コメント一覧")
        
        comment_type = st.selectbox(
            "表示するコメント種別を選択:",
            list(comments.keys()),
            key="comment_list_type"
        )
        
        if comment_type in comments and comments[comment_type]:
            st.write(f"**{comment_type}** ({len(comments[comment_type])}件)")
            
            for i, comment in enumerate(comments[comment_type], 1):
                with st.expander(f"コメント {i}"):
                    st.write(comment)
        else:
            st.info(f"{comment_type}のデータがありません。")

def show_time_series_analysis():
    """KPI時系列分析を表示"""
    st.header("📈 KPI時系列分析")
    
    # データの読み込み
    with st.spinner("📊 調査データを読み込み中..."):
        data = load_employee_data()
        
    if not data or 'employee_data' not in data:
        st.error("調査データが読み込めませんでした。")
        return
    
    # 現在は1回分のデータしかないため、デモ用の時系列データを生成
    st.info("📊 現在は1回分の調査データのみのため、デモンストレーション用の時系列データを表示します")
    
    # デモ用の時系列KPIデータを生成
    monthly_kpi_data = create_dummy_monthly_kpi_data()
    
    # メイン指標の時系列グラフ
    st.subheader("📈 主要KPI指標の月別推移")
    
    # 4つの主要指標を2x2のレイアウトで表示
    col1, col2 = st.columns(2)
    
    with col1:
        # eNPS推移
        fig_nps = px.line(
            monthly_kpi_data,
            x='年月',
            y='eNPS',
            title='eNPS (Employee Net Promoter Score) 推移',
            markers=True,
            color_discrete_sequence=['#FF6B6B']
        )
        fig_nps.update_layout(
            height=300,
            yaxis_title='eNPS (%)',
            xaxis_title='年月'
        )
        fig_nps.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="基準線 (0)")
        st.plotly_chart(fig_nps, use_container_width=True)
        
        # 活躍貢献度推移
        fig_contribution = px.line(
            monthly_kpi_data,
            x='年月',
            y='活躍貢献度',
            title='活躍貢献度 推移',
            markers=True,
            color_discrete_sequence=['#4ECDC4']
        )
        fig_contribution.update_layout(
            height=300,
            yaxis_title='活躍貢献度 (1-5点)',
            xaxis_title='年月',
            yaxis=dict(range=[1, 5])
        )
        st.plotly_chart(fig_contribution, use_container_width=True)
    
    with col2:
        # 総合満足度推移
        fig_satisfaction = px.line(
            monthly_kpi_data,
            x='年月',
            y='総合満足度',
            title='総合満足度 推移',
            markers=True,
            color_discrete_sequence=['#45B7D1']
        )
        fig_satisfaction.update_layout(
            height=300,
            yaxis_title='総合満足度 (1-5点)',
            xaxis_title='年月',
            yaxis=dict(range=[1, 5])
        )
        st.plotly_chart(fig_satisfaction, use_container_width=True)
        
        # 勤続意向推移
        fig_retention = px.line(
            monthly_kpi_data,
            x='年月',
            y='勤続意向',
            title='勤続意向 推移',
            markers=True,
            color_discrete_sequence=['#96CEB4']
        )
        fig_retention.update_layout(
            height=300,
            yaxis_title='勤続意向 (1-5点)',
            xaxis_title='年月',
            yaxis=dict(range=[1, 5])
        )
        st.plotly_chart(fig_retention, use_container_width=True)
    
    # 全指標を1つのグラフで比較
    st.subheader("📊 主要指標比較 (正規化)")
    
    # 正規化データを作成（0-1の範囲に正規化）
    normalized_data = monthly_kpi_data.copy()
    normalized_data['eNPS_正規化'] = (normalized_data['eNPS'] + 100) / 200  # -100~100 → 0~1
    normalized_data['総合満足度_正規化'] = (normalized_data['総合満足度'] - 1) / 4  # 1~5 → 0~1
    normalized_data['活躍貢献度_正規化'] = (normalized_data['活躍貢献度'] - 1) / 4  # 1~5 → 0~1
    normalized_data['勤続意向_正規化'] = (normalized_data['勤続意向'] - 1) / 4  # 1~5 → 0~1
    
    # 比較グラフ
    fig_compare = go.Figure()
    
    fig_compare.add_trace(go.Scatter(
        x=normalized_data['年月'],
        y=normalized_data['eNPS_正規化'],
        mode='lines+markers',
        name='eNPS',
        line=dict(color='#FF6B6B')
    ))
    
    fig_compare.add_trace(go.Scatter(
        x=normalized_data['年月'],
        y=normalized_data['総合満足度_正規化'],
        mode='lines+markers',
        name='総合満足度',
        line=dict(color='#45B7D1')
    ))
    
    fig_compare.add_trace(go.Scatter(
        x=normalized_data['年月'],
        y=normalized_data['活躍貢献度_正規化'],
        mode='lines+markers',
        name='活躍貢献度',
        line=dict(color='#4ECDC4')
    ))
    
    fig_compare.add_trace(go.Scatter(
        x=normalized_data['年月'],
        y=normalized_data['勤続意向_正規化'],
        mode='lines+markers',
        name='勤続意向',
        line=dict(color='#96CEB4')
    ))
    
    fig_compare.update_layout(
        title='主要KPI指標の推移比較 (正規化済み)',
        xaxis_title='年月',
        yaxis_title='正規化値 (0-1)',
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_compare, use_container_width=True)
    
    # 月別詳細データテーブル
    st.subheader("📋 月別KPI詳細データ")
    
    # 表示用にデータを整形
    display_data = monthly_kpi_data.copy()
    display_data['eNPS'] = display_data['eNPS'].round(1)
    display_data['総合満足度'] = display_data['総合満足度'].round(2)
    display_data['活躍貢献度'] = display_data['活躍貢献度'].round(2)
    display_data['勤続意向'] = display_data['勤続意向'].round(2)
    display_data['回答者数'] = display_data['回答者数'].astype(int)
    
    st.dataframe(display_data, use_container_width=True, hide_index=True)
    
    # トレンド分析
    st.subheader("📈 トレンド分析")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        nps_trend = monthly_kpi_data['eNPS'].iloc[-1] - monthly_kpi_data['eNPS'].iloc[0]
        st.metric(
            "eNPS変化", 
            f"{monthly_kpi_data['eNPS'].iloc[-1]:.1f}%",
            delta=f"{nps_trend:+.1f}%"
        )
    
    with col2:
        satisfaction_trend = monthly_kpi_data['総合満足度'].iloc[-1] - monthly_kpi_data['総合満足度'].iloc[0]
        st.metric(
            "総合満足度変化",
            f"{monthly_kpi_data['総合満足度'].iloc[-1]:.2f}点",
            delta=f"{satisfaction_trend:+.2f}点"
        )
    
    with col3:
        contribution_trend = monthly_kpi_data['活躍貢献度'].iloc[-1] - monthly_kpi_data['活躍貢献度'].iloc[0]
        st.metric(
            "活躍貢献度変化",
            f"{monthly_kpi_data['活躍貢献度'].iloc[-1]:.2f}点",
            delta=f"{contribution_trend:+.2f}点"
        )
    
    with col4:
        retention_trend = monthly_kpi_data['勤続意向'].iloc[-1] - monthly_kpi_data['勤続意向'].iloc[0]
        st.metric(
            "勤続意向変化",
            f"{monthly_kpi_data['勤続意向'].iloc[-1]:.2f}点",
            delta=f"{retention_trend:+.2f}点"
        )

def create_dummy_monthly_kpi_data():
    """デモ用の月別KPIデータを生成"""
    np.random.seed(42)
    
    # 過去12ヶ月のデータを生成
    months = []
    base_date = datetime.now().replace(day=1) - timedelta(days=365)
    
    for i in range(12):
        current_date = base_date + timedelta(days=30*i)
        months.append(current_date.strftime('%Y-%m'))
    
    # 基準値からトレンドのあるデータを生成
    base_recommend = 6.5  # 基準推奨スコア（10段階）
    base_satisfaction = 3.2  # 基準満足度
    base_contribution = 3.5  # 基準活躍貢献度
    base_retention = 3.1  # 基準勤続意向
    
    monthly_data = []
    
    for i, month in enumerate(months):
        # 季節性とトレンドを含んだデータ生成
        seasonal_factor = 0.1 * np.sin(2 * np.pi * i / 12)  # 季節変動
        trend_factor = i * 0.02  # 上昇トレンド
        
        # ランダムノイズ
        noise_recommend = np.random.normal(0, 0.3)
        noise_satisfaction = np.random.normal(0, 0.1)
        noise_contribution = np.random.normal(0, 0.1)
        noise_retention = np.random.normal(0, 0.1)
        
        # 推奨スコアを10段階で生成
        recommend = base_recommend + trend_factor * 3 + seasonal_factor * 0.5 + noise_recommend
        recommend = max(1, min(10, recommend))
        
        # 推奨スコア（10段階評価の平均値）
        enps = recommend
        
        satisfaction = base_satisfaction + trend_factor * 2 + seasonal_factor * 0.2 + noise_satisfaction
        contribution = base_contribution + trend_factor * 1.5 + seasonal_factor * 0.15 + noise_contribution
        retention = base_retention + trend_factor * 1.8 + seasonal_factor * 0.18 + noise_retention
        
        # 値の範囲制限
        satisfaction = max(1, min(5, satisfaction))
        contribution = max(1, min(5, contribution))
        retention = max(1, min(5, retention))
        
        monthly_data.append({
            '年月': month,
            'eNPS': enps,
            '総合満足度': satisfaction,
            '活躍貢献度': contribution,
            '勤続意向': retention,
            '回答者数': np.random.randint(45, 55)  # 回答者数も変動
        })
    
    return pd.DataFrame(monthly_data)

def show_department_analysis(data, kpis):
    """部署別分析を表示"""
    st.header("🏢 部署別・詳細分析")
    
    if 'employee_data' not in data:
        st.error("部署別データが利用できません")
        return
    
    df = data['employee_data']
    
    # タブを作成して内容を整理
    tabs = st.tabs(["📊 部署別分析", "💪 強み・弱み分析"])
    
    with tabs[0]:  # 部署別分析タブ
        # 部署別統計
        if 'department' in df.columns:
            dept_stats = df.groupby('department').agg({
                'overall_satisfaction': 'mean',
                'nps_score': 'mean',
                'contribution_score': 'mean',
                'long_term_intention': 'mean',
                'annual_salary': 'mean',
                'monthly_overtime': 'mean',
                'response_id': 'count'
            }).round(2)
            
            dept_stats.columns = ['総合満足度', 'NPS', '活躍貢献度', '勤続意向', '平均年収', '平均残業時間', '回答者数']
            
            # 部署別満足度比較
            fig = px.bar(
                dept_stats.reset_index(),
                x='department',
                y='総合満足度',
                title='部署別総合満足度',
                color='総合満足度',
                color_continuous_scale='RdYlGn',
                text='総合満足度'
            )
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig.update_layout(height=400, xaxis_title='部署', yaxis_title='満足度')
            st.plotly_chart(fig, use_container_width=True)
            
            # 詳細データテーブル
            st.subheader("部署別詳細データ")
            st.dataframe(dept_stats, use_container_width=True)
        else:
            st.info("部署情報が含まれていないため、個別回答者の詳細データを表示します")
            
            # 個別データの表示
            display_cols = ['response_id', 'overall_satisfaction', 'nps_score', 'contribution_score', 
                           'annual_salary', 'monthly_overtime', 'paid_leave_rate']
            available_cols = [col for col in display_cols if col in df.columns]
            
            if available_cols:
                st.dataframe(df[available_cols], use_container_width=True)
    
    with tabs[1]:  # 強み・弱み分析タブ
        show_strengths_weaknesses_analysis(data, kpis)

def show_strengths_weaknesses_analysis(data, kpis):
    """強み・弱み分析を表示"""
    st.subheader("💪 組織の強み・弱み分析")
    
    if 'satisfaction_by_category' not in kpis or not kpis['satisfaction_by_category']:
        st.warning("満足度カテゴリーデータが利用できません")
        return
    
    satisfaction_data = kpis['satisfaction_by_category']
    
    # 満足度を降順でソート
    sorted_satisfaction = sorted(satisfaction_data.items(), key=lambda x: x[1], reverse=True)
    
    # TOP5とBOTTOM5を抽出
    top5_strengths = sorted_satisfaction[:5]
    bottom5_weaknesses = sorted_satisfaction[-5:]
    
    # 2列に分けて表示
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌟 **TOP5 強み領域**")
        
        # 強み領域のデータフレーム作成
        strengths_df = pd.DataFrame(top5_strengths, columns=['カテゴリー', '満足度'])
        strengths_df['満足度'] = strengths_df['満足度'].round(2)
        
        # 強み領域の棒グラフ
        fig_strengths = px.bar(
            strengths_df,
            x='満足度',
            y='カテゴリー',
            orientation='h',
            title='組織の強み TOP5',
            color='満足度',
            color_continuous_scale='Greens',
            text='満足度',
            height=400
        )
        fig_strengths.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_strengths.update_layout(
            yaxis={'categoryorder':'total ascending'},
            xaxis=dict(range=[0, 5])
        )
        st.plotly_chart(fig_strengths, use_container_width=True)
        
        # 強み詳細テーブル
        st.markdown("#### 📈 強み詳細")
        for i, (category, score) in enumerate(top5_strengths, 1):
            st.markdown(f"**{i}位** {category}: **{score:.2f}点**")
    
    with col2:
        st.markdown("### ⚠️ **改善要望 TOP5**")
        
        # 弱み領域のデータフレーム作成（昇順で表示）
        weaknesses_df = pd.DataFrame(bottom5_weaknesses, columns=['カテゴリー', '満足度'])
        weaknesses_df['満足度'] = weaknesses_df['満足度'].round(2)
        
        # 弱み領域の棒グラフ
        fig_weaknesses = px.bar(
            weaknesses_df,
            x='満足度',
            y='カテゴリー',
            orientation='h',
            title='改善要望 TOP5',
            color='満足度',
            color_continuous_scale='Reds',
            text='満足度',
            height=400
        )
        fig_weaknesses.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_weaknesses.update_layout(
            yaxis={'categoryorder':'total ascending'},
            xaxis=dict(range=[0, 5])
        )
        st.plotly_chart(fig_weaknesses, use_container_width=True)
        
        # 弱み詳細テーブル
        st.markdown("#### 📉 改善要望詳細")
        for i, (category, score) in enumerate(reversed(bottom5_weaknesses), 1):
            st.markdown(f"**{i}位** {category}: **{score:.2f}点**")
    
    # 全体の満足度分布
    st.markdown("---")
    st.subheader("📊 全カテゴリー満足度分布")
    
    # 全カテゴリーのデータフレーム作成
    all_categories_df = pd.DataFrame(sorted_satisfaction, columns=['カテゴリー', '満足度'])
    all_categories_df['満足度'] = all_categories_df['満足度'].round(2)
    all_categories_df['順位'] = range(1, len(all_categories_df) + 1)
    
    # 色分け用の列を追加
    all_categories_df['領域'] = all_categories_df.apply(
        lambda row: '強み' if row['順位'] <= 5 else ('改善要望' if row['順位'] > len(all_categories_df) - 5 else '標準'), 
        axis=1
    )
    
    # 全体の棒グラフ
    fig_all = px.bar(
        all_categories_df,
        x='満足度',
        y='カテゴリー',
        orientation='h',
        title='全カテゴリー満足度ランキング',
        color='領域',
        color_discrete_map={
            '強み': '#2E8B57',
            '標準': '#4682B4', 
            '改善要望': '#DC143C'
        },
        text='満足度',
        height=600
    )
    fig_all.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_all.update_layout(
        yaxis={'categoryorder':'total ascending'},
        xaxis=dict(range=[0, 5])
    )
    st.plotly_chart(fig_all, use_container_width=True)
    
    # 満足度サマリー
    avg_satisfaction = sum(satisfaction_data.values()) / len(satisfaction_data)
    st.markdown("---")
    st.markdown("### 📋 満足度サマリー")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("平均満足度", f"{avg_satisfaction:.2f}点", delta=f"{avg_satisfaction - 3:.2f}")
    with col2:
        top_score = top5_strengths[0][1]
        st.metric("最高満足度", f"{top_score:.2f}点", delta=f"{top_score - avg_satisfaction:.2f}")
    with col3:
        bottom_score = bottom5_weaknesses[0][1]
        st.metric("最低満足度", f"{bottom_score:.2f}点", delta=f"{bottom_score - avg_satisfaction:.2f}")

def apply_filters(data, filters):
    """フィルターを適用してデータを絞り込む"""
    if not data or 'employee_data' not in data:
        return data
    
    df = data['employee_data'].copy()
    
    # 各フィルターを適用
    if filters['group'] and 'group' in df.columns:
        df = df[df['group'].isin(filters['group'])]
    
    if filters['workplace'] and 'workplace' in df.columns:
        df = df[df['workplace'].isin(filters['workplace'])]
    
    if filters['employee_number'] and 'employee_number' in df.columns:
        df = df[df['employee_number'].isin(filters['employee_number'])]
    
    if filters['business_type'] and 'business_type' in df.columns:
        df = df[df['business_type'].isin(filters['business_type'])]
    
    if filters['region'] and 'region' in df.columns:
        df = df[df['region'].isin(filters['region'])]
    
    if filters['job_category'] and 'job_category' in df.columns:
        df = df[df['job_category'].isin(filters['job_category'])]
    
    if filters['age_group'] and 'age_group' in df.columns:
        df = df[df['age_group'].isin(filters['age_group'])]
    
    # フィルター後のデータを返す
    filtered_data = data.copy()
    filtered_data['employee_data'] = df
    
    return filtered_data

def main():
    # サイドバー
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-logo">
                <span style='color: #667eea; font-size: 24px;'>👥</span>
            </div>
            <div style='color: white; font-weight: bold; font-size: 18px;'>従業員調査分析</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # ページ選択
        page = st.radio(
            "📋 分析ページ選択",
            ["📊 KPI概要", "📈 満足度分析", "🏢 詳細分析", "📝 テキストマイニング", "⏰ 時系列分析", "🔬 重回帰分析", "🤖 AI テキスト分析"],
            index=0
        )
        
        st.divider()
        
        # フィルター設定
        st.markdown("### 🔍 データフィルター")
        
        # データを読み込んでフィルター選択肢を作成
        temp_data = load_employee_data()
        
        filters = {}
        
        if temp_data and 'employee_data' in temp_data:
            df = temp_data['employee_data']
            
            # グループフィルター
            if 'group' in df.columns:
                filters['group'] = st.multiselect(
                    "グループ",
                    options=sorted(df['group'].dropna().unique()),
                    default=None,
                    key="filter_group"
                )
            else:
                filters['group'] = []
            
            # 勤務地フィルター
            if 'workplace' in df.columns:
                filters['workplace'] = st.multiselect(
                    "勤務地",
                    options=sorted(df['workplace'].dropna().unique()),
                    default=None,
                    key="filter_workplace"
                )
            else:
                filters['workplace'] = []
            
            # 人数番号フィルター
            if 'employee_number' in df.columns:
                filters['employee_number'] = st.multiselect(
                    "人数番号",
                    options=sorted(df['employee_number'].dropna().unique()),
                    default=None,
                    key="filter_employee_number"
                )
            else:
                filters['employee_number'] = []
            
            # 勤務業務等フィルター
            if 'business_type' in df.columns:
                filters['business_type'] = st.multiselect(
                    "勤務業務等",
                    options=sorted(df['business_type'].dropna().unique()),
                    default=None,
                    key="filter_business_type"
                )
            else:
                filters['business_type'] = []
            
            # 地域フィルター
            if 'region' in df.columns:
                filters['region'] = st.multiselect(
                    "地域",
                    options=sorted(df['region'].dropna().unique()),
                    default=None,
                    key="filter_region"
                )
            else:
                filters['region'] = []
            
            # 職務フィルター
            if 'job_category' in df.columns:
                filters['job_category'] = st.multiselect(
                    "職務",
                    options=sorted(df['job_category'].dropna().unique()),
                    default=None,
                    key="filter_job_category"
                )
            else:
                filters['job_category'] = []
            
            # 年齢等フィルター
            if 'age_group' in df.columns:
                filters['age_group'] = st.multiselect(
                    "年齢等",
                    options=sorted(df['age_group'].dropna().unique()),
                    default=None,
                    key="filter_age_group"
                )
            else:
                filters['age_group'] = []
        else:
            filters = {
                'group': [],
                'workplace': [],
                'employee_number': [],
                'business_type': [],
                'region': [],
                'job_category': [],
                'age_group': []
            }
        
        # フィルターリセットボタン
        if st.button("🔄 フィルターリセット", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.divider()
        
        # データ更新ボタン
        if st.button("🔄 データ更新", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.info("💡 Excelファイル更新後は「データ更新」ボタンを押してください")
        
        st.divider()
        
        # レポート情報
        st.markdown("### 📋 レポート情報")
        
        st.write(f"🕐 **最終更新:** {datetime.now().strftime('%Y/%m/%d')}")
        
        # データエクスポート
        st.subheader("📥 データエクスポート")
        if st.button("📊 レポート出力", use_container_width=True):
            st.success("実装時には分析レポートをPDF/Excelで出力できます")
    
    # メインコンテンツ
    st.title("👥 従業員調査可視化ダッシュボード")
    st.markdown("---")
    
    # データ読み込み
    with st.spinner("📊 データを読み込み中..."):
        data = load_employee_data()
        # フィルターを適用
        filtered_data = apply_filters(data, filters)
        kpis = calculate_kpis(filtered_data)
    
    # ページ表示
    if page == "📊 KPI概要":
        show_kpi_overview(filtered_data, kpis)
    elif page == "📈 満足度分析":
        show_satisfaction_analysis(filtered_data, kpis)
    elif page == "🏢 詳細分析":
        show_department_analysis(filtered_data, kpis)
    elif page == "📝 テキストマイニング":
        show_text_mining_analysis()
    elif page == "⏰ 時系列分析":
        show_time_series_analysis()
    elif page == "🔬 重回帰分析":
        show_regression_analysis(filtered_data, kpis)
    
    elif page == "🤖 AI テキスト分析":
        # 新しいAIテキスト分析機能を表示
        from text_analysis_ml import show_text_analysis_ml_page
        show_text_analysis_ml_page()

def show_regression_analysis(data, kpis):
    """重回帰分析を表示"""
    st.header("🔬 重回帰分析")
    st.markdown("主要指標に対する満足度項目の影響力を分析します")
    
    if not data or 'employee_data' not in data:
        st.error("分析に必要なデータが不足しています")
        return
    
    df = data['employee_data']
    
    # 目的変数の選択（利用可能な列名を自動検出）
    target_options = {}
    
    # eNPS関連の列名を検索
    enps_candidates = ['nps_score', 'recommend_score']
    for candidate in enps_candidates:
        if candidate in df.columns:
            target_options['eNPS (推奨度)'] = candidate
            break
    
    # 実際のExcelデータの列名も検索
    for col in df.columns:
        col_str = str(col)
        if any(keyword in col_str for keyword in ['推奨', '親しい友人', '家族', '転職', '就職', '総合評価']):
            target_options['eNPS (推奨度)'] = col
            break
    
    # その他の目的変数（実データ対応）
    if 'overall_satisfaction' in df.columns:
        target_options['総合満足度'] = 'overall_satisfaction'
    else:
        # 実際のExcelデータの総合満足度列を検索
        for col in df.columns:
            if '総合満足度' in str(col):
                target_options['総合満足度'] = col
                break
    
    if 'long_term_intention' in df.columns:
        target_options['勤続意向'] = 'long_term_intention'
    else:
        # 実際のExcelデータの勤続意向列を検索
        for col in df.columns:
            if any(keyword in str(col) for keyword in ['長く働きたい', '勤続', '意向']):
                target_options['勤続意向'] = col
                break
                
    if 'contribution_score' in df.columns:
        target_options['活躍貢献度'] = 'contribution_score'
    else:
        # 実際のExcelデータの活躍貢献度列を検索
        for col in df.columns:
            if any(keyword in str(col) for keyword in ['活躍貢献', '貢献できている']):
                target_options['活躍貢献度'] = col
                break
    
    if not target_options:
        st.error("分析可能な目的変数が見つかりません。データの列名を確認してください。")
        st.info("利用可能な列名:")
        st.write(list(df.columns))
        return
    
    selected_target = st.selectbox(
        "🎯 分析対象（目的変数）を選択してください",
        list(target_options.keys())
    )
    
    target_col = target_options[selected_target]
    
    # 満足度項目（説明変数）を定義
    satisfaction_categories = [
        '勤務時間', '休日休暇', '有給休暇', '勤務体系', '昇給昇格', '人間関係',
        '働く環境', '成長実感', '将来キャリア', '福利厚生', '評価制度'
    ]
    
    # デバッグ情報：利用可能な列名を表示
    with st.expander("🔍 デバッグ情報（利用可能な列名）"):
        st.write("**全ての列名:**")
        st.write(list(df.columns))
        st.write(f"**選択された目的変数:** {target_col}")
        st.write("**データの形状:**", df.shape)
    
    # データの準備
    try:
        # 目的変数の確認
        if target_col not in df.columns:
            st.error(f"目的変数 '{target_col}' がデータに含まれていません")
            return
            
        # 目的変数の数値変換
        y = df[target_col].copy()
        
        # eNPS（推奨度）の場合の特別処理
        if 'eNPS' in selected_target:
            # "7 (Passive)" のような文字列から数値を抽出
            y = y.astype(str).str.extract(r'(\d+)', expand=False).astype(float)
        else:
            # その他の場合は数値変換を試行
            try:
                y = pd.to_numeric(y, errors='coerce')
            except:
                st.error(f"目的変数 '{target_col}' を数値に変換できません")
                return
        
        # 説明変数の準備（満足度項目）
        X_data = []
        available_features = []
        
        # 満足度系の列名パターンを検索
        satisfaction_patterns = ['満足度', '評価', '度合い']
        
        for category in satisfaction_categories:
            # パターン1: カテゴリ_満足度
            sat_col = f"{category}_満足度"
            if sat_col in df.columns:
                X_data.append(df[sat_col])
                available_features.append(sat_col)
                continue
                
            # パターン2: カテゴリ名そのもの
            if category in df.columns:
                X_data.append(df[category])
                available_features.append(category)
                continue
        
        # 追加で満足度系の列を自動検出
        for col in df.columns:
            if any(pattern in col for pattern in satisfaction_patterns) and col not in available_features:
                # 目的変数と同じ列は除外
                if col != target_col:
                    try:
                        # 数値データに変換を試行
                        numeric_data = pd.to_numeric(df[col], errors='coerce')
                        # 欠損値が80%未満の場合のみ採用
                        if numeric_data.notna().sum() / len(numeric_data) > 0.2:
                            X_data.append(numeric_data)
                            available_features.append(col)
                    except:
                        pass
        
        if not X_data:
            st.error("説明変数となる満足度データが見つかりません")
            st.info("利用可能な列名から満足度系のデータを探しましたが見つかりませんでした。")
            return
            
        X = pd.DataFrame(X_data).T
        X.columns = available_features
        
        # 選択された説明変数を表示
        st.info(f"📋 **検出された説明変数:** {len(available_features)}個")
        with st.expander("使用する説明変数一覧"):
            for i, feature in enumerate(available_features, 1):
                st.write(f"{i}. {feature}")
        
        # 欠損値の処理
        X = X.fillna(X.mean())
        y = y.fillna(y.mean())
        
        # 有効なデータのみを使用
        valid_idx = ~(X.isna().any(axis=1) | y.isna())
        X = X[valid_idx]
        y = y[valid_idx]
        
        if len(X) < 10:
            st.warning("分析に十分なデータがありません（最低10件必要）")
            return
            
        st.success(f"✅ 分析データ準備完了: {len(X)}件のデータを使用")
        
        # タブで結果を整理
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 分析結果", "🔍 多重共線性診断", "📈 係数可視化", "🎯 予測精度", "📈 詳細統計"])
        
        with tab1:
            st.subheader("📊 重回帰分析結果")
            
            # 標準化
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            X_scaled_df = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
            
            # 重回帰分析実行
            model = LinearRegression()
            model.fit(X_scaled_df, y)
            
            # 予測値計算
            y_pred = model.predict(X_scaled_df)
            
            # 決定係数とRMSE
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            
            # 結果表示
            col1, col2 = st.columns(2)
            with col1:
                st.metric("決定係数 (R²)", f"{r2:.3f}")
            with col2:
                st.metric("RMSE", f"{rmse:.3f}")
            
            # 統計的検定のためのOLS回帰を実行
            if STATSMODELS_AVAILABLE:
                X_with_const = sm.add_constant(X_scaled_df)
                ols_model = sm.OLS(y, X_with_const).fit()
            else:
                X_with_const = X_scaled_df
                ols_model = None
            
            # 回帰係数の表示（統計的有意性を含む）
            coef_data = []
            for i, var in enumerate(X.columns):
                coef = model.coef_[i]
                if STATSMODELS_AVAILABLE and ols_model is not None:
                    p_value = ols_model.pvalues[var] if var in ols_model.pvalues.index else None
                    conf_int = ols_model.conf_int().loc[var] if var in ols_model.conf_int().index else [None, None]
                else:
                    p_value = None
                    conf_int = [None, None]
                
                significance = ""
                if p_value is not None:
                    if p_value < 0.001:
                        significance = "***"
                    elif p_value < 0.01:
                        significance = "**"
                    elif p_value < 0.05:
                        significance = "*"
                    elif p_value < 0.1:
                        significance = "†"
                
                coef_data.append({
                    '説明変数': var,
                    '標準化係数': coef,
                    'p値': p_value,
                    '有意性': significance,
                    '95%信頼区間下限': conf_int[0],
                    '95%信頼区間上限': conf_int[1],
                    '絶対値': np.abs(coef)
                })
            
            coef_df = pd.DataFrame(coef_data).sort_values('絶対値', ascending=False)
            
            st.subheader("📋 回帰係数ランキング（統計的有意性付き）")
            
            # 有意性の説明
            st.markdown("""
            **有意性レベル:** *** p<0.001, ** p<0.01, * p<0.05, † p<0.1
            """)
            
            # 表示用データフレームを作成
            display_coef_df = coef_df[['説明変数', '標準化係数', 'p値', '有意性', '95%信頼区間下限', '95%信頼区間上限']].copy()
            display_coef_df['標準化係数'] = display_coef_df['標準化係数'].round(4)
            display_coef_df['p値'] = display_coef_df['p値'].round(4)
            display_coef_df['95%信頼区間下限'] = display_coef_df['95%信頼区間下限'].round(4)
            display_coef_df['95%信頼区間上限'] = display_coef_df['95%信頼区間上限'].round(4)
            
            st.dataframe(
                display_coef_df,
                use_container_width=True,
                hide_index=True
            )
            
        with tab2:
            st.subheader("🔍 多重共線性診断")
            
            # VIF計算
            def calculate_vif(X_df):
                if not STATSMODELS_AVAILABLE:
                    return pd.DataFrame({"説明変数": X_df.columns, "VIF": ["利用不可"] * len(X_df.columns)})
                vif_data = pd.DataFrame()
                vif_data["説明変数"] = X_df.columns
                vif_data["VIF"] = [variance_inflation_factor(X_df.values, i) 
                                 for i in range(len(X_df.columns))]
                return vif_data.sort_values('VIF', ascending=False)
            
            try:
                # 定数項を追加してVIF計算
                if STATSMODELS_AVAILABLE:
                    X_with_const = sm.add_constant(X_scaled_df)
                else:
                    X_with_const = X_scaled_df
                vif_df = calculate_vif(X_scaled_df)
                
                st.dataframe(vif_df.round(2), use_container_width=True, hide_index=True)
                
                # VIF解釈の説明
                high_vif = vif_df[vif_df['VIF'] > 5]
                if len(high_vif) > 0:
                    st.warning("""
                    ⚠️ **多重共線性の可能性があります**
                    - VIF > 5: 多重共線性の疑いあり
                    - VIF > 10: 深刻な多重共線性
                    """)
                    
                    # PCA実行の提案
                    if st.button("🔄 主成分分析で次元圧縮を実行"):
                        st.info("主成分分析を実行して多重共線性を解決します...")
                        
                        # PCA実行
                        pca = PCA()
                        X_pca = pca.fit_transform(X_scaled_df)
                        
                        # 累積寄与率95%までの成分を選択
                        cumsum_ratio = np.cumsum(pca.explained_variance_ratio_)
                        n_components = np.argmax(cumsum_ratio >= 0.95) + 1
                        
                        st.write(f"📊 95%の分散を説明するのに必要な主成分数: {n_components}")
                        
                        # 主成分での分析
                        pca_selected = PCA(n_components=n_components)
                        X_pca_selected = pca_selected.fit_transform(X_scaled_df)
                        
                        model_pca = LinearRegression()
                        model_pca.fit(X_pca_selected, y)
                        y_pred_pca = model_pca.predict(X_pca_selected)
                        
                        r2_pca = r2_score(y, y_pred_pca)
                        rmse_pca = np.sqrt(mean_squared_error(y, y_pred_pca))
                        
                        st.success(f"🎯 PCA後の精度: R² = {r2_pca:.3f}, RMSE = {rmse_pca:.3f}")
                        
                        # 主成分の解釈
                        components_df = pd.DataFrame(
                            pca_selected.components_.T,
                            columns=[f'PC{i+1}' for i in range(n_components)],
                            index=X.columns
                        )
                        
                        st.subheader("📋 主成分の構成")
                        st.dataframe(components_df.round(3), use_container_width=True)
                        
                else:
                    st.success("✅ 多重共線性の問題は検出されませんでした")
                    
            except Exception as e:
                st.error(f"VIF計算中にエラーが発生しました: {str(e)}")
                
        with tab3:
            st.subheader("📈 回帰係数の可視化")
            
            # 統計的有意性を色で表現
            coef_df['有意性_数値'] = coef_df['p値'].apply(lambda x: 
                0 if pd.isna(x) else 
                4 if x < 0.001 else 
                3 if x < 0.01 else 
                2 if x < 0.05 else 
                1 if x < 0.1 else 0
            )
            
            # 係数の棒グラフ（有意性で色分け）
            fig = px.bar(
                coef_df,
                x='標準化係数',
                y='説明変数',
                orientation='h',
                title=f'{selected_target}に対する各要因の影響力（有意性で色分け）',
                color='有意性_数値',
                color_continuous_scale=['lightgray', 'lightblue', 'yellow', 'orange', 'red'],
                hover_data=['p値', '有意性']
            )
            fig.update_layout(
                height=600,
                coloraxis_colorbar=dict(
                    title="有意性レベル",
                    tickvals=[0, 1, 2, 3, 4],
                    ticktext=["n.s.", "p<0.1", "p<0.05", "p<0.01", "p<0.001"]
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 信頼区間のプロット
            st.subheader("📊 回帰係数の信頼区間")
            
            # 信頼区間のプロット用データ準備
            plot_data = coef_df.copy()
            plot_data = plot_data.sort_values('標準化係数')
            
            fig_ci = go.Figure()
            
            # 点推定値
            fig_ci.add_trace(go.Scatter(
                x=plot_data['標準化係数'],
                y=plot_data['説明変数'],
                mode='markers',
                marker=dict(size=10, color='blue'),
                name='点推定値',
                text=plot_data['有意性'],
                textposition="middle right"
            ))
            
            # 信頼区間
            for idx, row in plot_data.iterrows():
                if not pd.isna(row['95%信頼区間下限']) and not pd.isna(row['95%信頼区間上限']):
                    fig_ci.add_trace(go.Scatter(
                        x=[row['95%信頼区間下限'], row['95%信頼区間上限']],
                        y=[row['説明変数'], row['説明変数']],
                        mode='lines',
                        line=dict(color='gray', width=2),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
            
            # ゼロライン
            fig_ci.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="ゼロライン")
            
            fig_ci.update_layout(
                title="回帰係数の95%信頼区間",
                xaxis_title="標準化回帰係数",
                yaxis_title="説明変数",
                height=600
            )
            
            st.plotly_chart(fig_ci, use_container_width=True)
            
            # 影響力の解釈
            st.subheader("📝 結果の解釈")
            top_positive = coef_df[coef_df['標準化係数'] > 0].head(3)
            top_negative = coef_df[coef_df['標準化係数'] < 0].head(3)
            
            if len(top_positive) > 0:
                st.write("**🔺 正の影響（向上要因）:**")
                for _, row in top_positive.iterrows():
                    st.write(f"- {row['説明変数']}: {row['標準化係数']:.3f}")
                    
            if len(top_negative) > 0:
                st.write("**🔻 負の影響（阻害要因）:**")
                for _, row in top_negative.iterrows():
                    st.write(f"- {row['説明変数']}: {row['標準化係数']:.3f}")
                    
        with tab4:
            st.subheader("🎯 予測精度の評価")
            
            # 実測値 vs 予測値のプロット
            fig = px.scatter(
                x=y, 
                y=y_pred,
                title='実測値 vs 予測値',
                labels={'x': f'実測値 ({selected_target})', 'y': f'予測値 ({selected_target})'}
            )
            
            # 完全予測線を追加
            min_val, max_val = min(y.min(), y_pred.min()), max(y.max(), y_pred.max())
            fig.add_shape(
                type="line",
                x0=min_val, y0=min_val,
                x1=max_val, y1=max_val,
                line=dict(color="red", dash="dash")
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 残差プロット
            residuals = y - y_pred
            fig_residual = px.scatter(
                x=y_pred,
                y=residuals,
                title='残差プロット',
                labels={'x': '予測値', 'y': '残差'}
            )
            fig_residual.add_hline(y=0, line_dash="dash", line_color="red")
            st.plotly_chart(fig_residual, use_container_width=True)
            
        with tab5:
            st.subheader("📈 詳細統計情報")
            
            # モデル全体の統計情報
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if STATSMODELS_AVAILABLE and ols_model is not None:
                    st.metric("調整済みR²", f"{ols_model.rsquared_adj:.4f}")
                    st.metric("AIC", f"{ols_model.aic:.2f}")
                else:
                    st.metric("調整済みR²", "利用不可")
                    st.metric("AIC", "利用不可")
                
            with col2:
                if STATSMODELS_AVAILABLE and ols_model is not None:
                    st.metric("BIC", f"{ols_model.bic:.2f}")
                    st.metric("F統計量", f"{ols_model.fvalue:.2f}")
                else:
                    st.metric("BIC", "利用不可")
                    st.metric("F統計量", "利用不可")
                
            with col3:
                if STATSMODELS_AVAILABLE and ols_model is not None:
                    st.metric("F検定p値", f"{ols_model.f_pvalue:.4f}")
                    st.metric("尤度比", f"{ols_model.llf:.2f}")
                else:
                    st.metric("F検定p値", "利用不可")
                    st.metric("尤度比", "利用不可")
            
            # 回帰分析の前提条件の検証
            st.subheader("🔍 回帰分析の前提条件チェック")
            
            # 正規性検定（Shapiro-Wilk検定）
            shapiro_stat, shapiro_p = stats.shapiro(residuals)
            
            # Durbin-Watson統計量（自己相関の検定）
            if STATSMODELS_AVAILABLE:
                dw_stat = durbin_watson(residuals)
                # Breusch-Pagan検定（等分散性の検定）
                bp_stat, bp_p, bp_f_stat, bp_f_p = het_breuschpagan(residuals, X_with_const)
            else:
                dw_stat = None
                bp_stat, bp_p, bp_f_stat, bp_f_p = None, None, None, None
            
            # 前提条件チェック結果
            st.markdown("### 📋 診断結果")
            
            # 正規性
            normality_status = "✅ 正規性OK" if shapiro_p > 0.05 else "⚠️ 正規性に問題あり"
            st.write(f"**残差の正規性:** {normality_status} (Shapiro-Wilk p={shapiro_p:.4f})")
            
            # 自己相関
            if STATSMODELS_AVAILABLE and dw_stat is not None:
                autocorr_status = "✅ 自己相関なし" if 1.5 <= dw_stat <= 2.5 else "⚠️ 自己相関の可能性"
                st.write(f"**自己相関:** {autocorr_status} (Durbin-Watson={dw_stat:.3f})")
            else:
                st.write("**自己相関:** ❌ 利用不可 (statsmodels未インストール)")
            
            # 等分散性
            if STATSMODELS_AVAILABLE and bp_p is not None:
                homoscedasticity_status = "✅ 等分散性OK" if bp_p > 0.05 else "⚠️ 不等分散の可能性"
                st.write(f"**等分散性:** {homoscedasticity_status} (Breusch-Pagan p={bp_p:.4f})")
            else:
                st.write("**等分散性:** ❌ 利用不可 (statsmodels未インストール)")
            
            # 詳細な診断プロット
            st.subheader("📊 診断プロット")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Q-Qプロット（正規性確認）
                fig_qq = go.Figure()
                
                # Q-Qプロットのデータ
                qq_data = probplot(residuals, dist="norm")
                theoretical_quantiles = qq_data[0][0]
                sample_quantiles = qq_data[0][1]
                
                # プロット
                fig_qq.add_trace(go.Scatter(
                    x=theoretical_quantiles,
                    y=sample_quantiles,
                    mode='markers',
                    name='残差',
                    marker=dict(color='blue', size=6)
                ))
                
                # 理論直線
                fig_qq.add_trace(go.Scatter(
                    x=theoretical_quantiles,
                    y=qq_data[1][0] * theoretical_quantiles + qq_data[1][1],
                    mode='lines',
                    name='理論直線',
                    line=dict(color='red', dash='dash')
                ))
                
                fig_qq.update_layout(
                    title="Q-Qプロット（正規性確認）",
                    xaxis_title="理論分位数",
                    yaxis_title="標本分位数",
                    height=400
                )
                
                st.plotly_chart(fig_qq, use_container_width=True)
                
            with col2:
                # Cook距離（外れ値検出）
                if STATSMODELS_AVAILABLE and ols_model is not None:
                    influence = ols_model.get_influence()
                    cooks_d = influence.cooks_distance[0]
                else:
                    cooks_d = np.zeros(len(residuals))  # Fallback to zeros
                
                fig_cook = px.scatter(
                    x=range(len(cooks_d)),
                    y=cooks_d,
                    title="Cook距離（外れ値検出）",
                    labels={'x': 'サンプル番号', 'y': 'Cook距離'}
                )
                
                # Cook距離の閾値線
                threshold = 4 / len(X)
                fig_cook.add_hline(y=threshold, line_dash="dash", line_color="red", 
                                 annotation_text=f"閾値={threshold:.3f}")
                
                fig_cook.update_layout(height=400)
                st.plotly_chart(fig_cook, use_container_width=True)
            
            # 実用的な解釈とアドバイス
            st.subheader("💡 分析結果の実用的解釈")
            
            # 統計的に有意な変数の抽出
            significant_vars = coef_df[coef_df['p値'] < 0.05]
            
            if len(significant_vars) > 0:
                st.success(f"📈 **統計的に有意な影響要因: {len(significant_vars)}個**")
                
                for _, row in significant_vars.head(5).iterrows():
                    direction = "向上" if row['標準化係数'] > 0 else "低下"
                    impact_size = "大" if abs(row['標準化係数']) > 0.3 else "中" if abs(row['標準化係数']) > 0.1 else "小"
                    
                    st.write(f"- **{row['説明変数']}**: {selected_target}を{direction}させる（影響度: {impact_size}, 係数: {row['標準化係数']:.3f}）")
                
                # 改善提案
                st.subheader("🎯 改善提案")
                
                top_positive = significant_vars[significant_vars['標準化係数'] > 0].head(3)
                top_negative = significant_vars[significant_vars['標準化係数'] < 0].head(3)
                
                if len(top_positive) > 0:
                    st.info("**🚀 重点的に改善すべき領域（正の影響）:**")
                    for _, row in top_positive.iterrows():
                        st.write(f"• {row['説明変数']}の向上 → {selected_target}が{abs(row['標準化係数']):.1%}向上期待")
                
                if len(top_negative) > 0:
                    st.warning("**⚠️ 注意が必要な領域（負の影響）:**")
                    for _, row in top_negative.iterrows():
                        st.write(f"• {row['説明変数']}の問題 → {selected_target}が{abs(row['標準化係数']):.1%}低下リスク")
                
            else:
                st.warning("統計的に有意な影響要因が見つかりませんでした。サンプルサイズの増加やデータ品質の向上を検討してください。")
            
    except Exception as e:
        st.error(f"分析中にエラーが発生しました: {str(e)}")
        st.info("データの形式や内容を確認してください")

if __name__ == "__main__":
    main()