#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
従業員調査可視化ダッシュボード（プロフェッショナル版）
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import os
import re

# ページ設定
st.set_page_config(
    page_title="Employee Survey Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# プロフェッショナルなCSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', 'Helvetica Neue', 'Arial', sans-serif;
        background-color: #f8fafc;
    }
    
    .main > div {
        padding-top: 2rem;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #1e293b;
        font-weight: 600;
        letter-spacing: -0.025em;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-left: 4px solid #3b82f6;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05));
        border-radius: 50%;
        transform: translate(20px, -20px);
    }
    
    .kpi-title {
        font-size: 0.875rem;
        font-weight: 500;
        color: #64748b;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
        line-height: 1;
    }
    
    .kpi-description {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 400;
    }
    
    .kpi-positive {
        border-left-color: #10b981;
    }
    
    .kpi-positive::before {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
    }
    
    .kpi-warning {
        border-left-color: #f59e0b;
    }
    
    .kpi-warning::before {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05));
    }
    
    .kpi-negative {
        border-left-color: #ef4444;
    }
    
    .kpi-negative::before {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
    }
    
    .section-header {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #3b82f6;
    }
    
    .section-header h2 {
        margin: 0;
        color: #1e293b;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
    }
    
    .sidebar .sidebar-content {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stSelectbox > div > div {
        background-color: white;
        border: 1px solid #d1d5db;
        border-radius: 8px;
    }
    
    .stRadio > div {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid #e5e7eb;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: #f1f5f9;
        border-radius: 8px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 6px;
        color: #64748b;
        font-weight: 500;
        background-color: transparent;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #1e293b !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .dataframe {
        border: none !important;
    }
    
    .dataframe thead th {
        background-color: #f8fafc !important;
        color: #374151 !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 12px !important;
    }
    
    .dataframe tbody td {
        border: none !important;
        padding: 12px !important;
        background-color: white !important;
    }
    
    .dataframe tbody tr:nth-child(even) td {
        background-color: #f9fafb !important;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# 実際のアンケート項目定義
SURVEY_CATEGORIES = {
    "Work Environment": {
        "work_hours": "自分に合った勤務時間で働ける",
        "holidays": "休日休暇がちゃんと取れる", 
        "paid_leave": "有給休暇がちゃんと取れる",
        "flex_work": "柔軟な勤務体系（リモートワーク、時短勤務、フレックス制など）",
        "commute": "自宅から適切な距離で働ける",
        "job_transfer": "自身の希望が十分に考慮されるような転勤体制",
        "internal_mobility": "自身の希望が十分に考慮されるような社内異動体制"
    },
    "Compensation & Recognition": {
        "overtime_pay": "残業したらその分しっかり給与が支払われる",
        "fair_evaluation": "自身の行った仕事が正当に評価される",
        "promotion": "成果に応じて早期の昇給・昇格が望める",
        "benefits": "充実した福利厚生"
    },
    "Workload & Stress": {
        "workload": "自分のキャパシティーに合った量の仕事で働ける",
        "physical_load": "仕事内容や量に対する身体的な負荷が少ない",
        "mental_load": "仕事内容や量に対する精神的な負荷が少ない",
        "achievable_goals": "達成可能性が見込まれる目標やノルマ"
    },
    "Growth & Development": {
        "specialized_skills": "専門的なスキルや技術・知識や経験の獲得",
        "general_skills": "汎用的なスキル（コミュニケーション能力や論理的思考力など）の獲得",
        "training": "整った教育体制",
        "career_path": "自分に合った将来のキャリアパス設計",
        "career_match": "将来自分のなりたい方向性とマッチした仕事",
        "role_models": "身近にロールモデルとなるような人がいる環境"
    },
    "Job Satisfaction": {
        "pride_in_work": "誇りやプライドを持てるような仕事内容",
        "social_contribution": "社会に対して貢献実感を持てるような仕事",
        "job_fulfillment": "やりがいを感じられるような仕事",
        "autonomy": "自分の判断で進められる裁量のある仕事",
        "sense_of_growth": "成長実感を感じられるような仕事",
        "sense_of_achievement": "達成感を得られるような仕事",
        "impactful_work": "規模の大きなプロジェクトや仕事",
        "use_of_strengths": "自分の強みを活かせるような仕事"
    },
    "Relationships & Culture": {
        "relationships": "人間関係が良好な環境",
        "harassment_free": "セクハラやパワハラがないような環境",
        "culture_fit": "自身の価値観や考え方と共感できるような会社の社風や文化",
        "open_communication": "意見や考え方などについて自由に言い合える風通しの良い環境",
        "learning_culture": "社内で相互に教えたり・学び合ったりするような環境",
        "work_environment": "働きやすい仕事環境やオフィス環境",
        "women_support": "女性が働きやすい環境"
    },
    "Company & Business": {
        "company_stability": "事業基盤の安心感",
        "management_strategy": "信頼できる経営戦略や戦術の実行",
        "competitive_edge": "同業他社と比較した事業内容の競合優位性や独自性",
        "brand_power": "ブランド力や知名度",
        "mission_vision_fit": "会社のミッション・バリュー",
        "compliance": "法令遵守が整った社内体制"
    }
}

# カラム名マッピング（実際のExcelファイル用）
COLUMN_MAPPING = {
    '入社年度を教えてください。※2019年入社の場合には、2019とお答えください。': 'start_year',
    '概算年収を教えてください。450万円の場合には、450と半角でお答えください。': 'annual_salary',
    '1ヶ月当たりの平均残業時間を教えてください。（残業時間が月100時間ほどある方は100とお答えください）': 'avg_monthly_overtime',
    '1年間当たりの平均有給休暇取得率を教えてください。（全て利用されていれば100、80%ほど利用されていれば80とお答えください。）': 'paid_leave_usage_rate',
    '総合評価：自分の親しい友人や家族に対して、この会社への転職・就職をどの程度勧めたいと思いますか？': 'recommend_score',
    '総合満足度：自社の現在の働く環境や条件、周りの人間関係なども含めあなたはどの程度満足されていますか？': 'overall_satisfaction',
    'あなたはこの会社でこれからも長く働きたいと思われますか？': 'long_term_intention',
    '活躍貢献度：現在の会社や所属組織であなたはどの程度、活躍貢献できていると感じますか？': 'sense_of_contribution'
}

@st.cache_data
def load_real_excel_data():
    """実際のExcelデータを読み込み、処理する"""
    try:
        excel_path = '/Users/sugayayoshiyuki/Desktop/採用可視化サーベイ/従業員調査.xlsx'
        
        if not os.path.exists(excel_path):
            return create_professional_dummy_data(), False
        
        # Excelファイルを読み込む
        excel_file = pd.ExcelFile(excel_path)
        
        if 'Responses' in excel_file.sheet_names:
            # 1行目をヘッダーとして読み込み
            df = pd.read_excel(excel_path, sheet_name='Responses', header=1)
            
            # データが十分にない場合はダミーデータを使用
            if len(df) <= 2:
                st.info("実データが少ないため、分析用のダミーデータを使用しています")
                return create_professional_dummy_data(), False
            
            # カラム名を正規化
            df = df.rename(columns=COLUMN_MAPPING)
            
            # 数値データの抽出と変換
            for col in ['recommend_score', 'overall_satisfaction', 'long_term_intention', 'sense_of_contribution']:
                if col in df.columns:
                    # 数値部分を抽出して数値に変換
                    extracted = df[col].astype(str).str.extract(r'(\d+)', expand=False)
                    df[col] = pd.to_numeric(extracted, errors='coerce')
            
            # 基本データの型変換
            for col in ['start_year', 'annual_salary', 'avg_monthly_overtime', 'paid_leave_usage_rate']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 満足度・期待度データの処理（実際のExcelファイル構造に基づく）
            satisfaction_mapping = {
                '自分に合った勤務時間で働ける（1: 満足していない': 'work_hours_satisfaction',
                '休日休暇がちゃんと取れる（1: 満足していない': 'holidays_satisfaction',
                '有給休暇がちゃんと取れる（1: 満足していない': 'paid_leave_satisfaction',
                '柔軟な勤務体系（リモートワーク、時短勤務、フレックス制など）のもとで働ける（1: 満足していない': 'flex_work_satisfaction',
                '自宅から適切な距離で働ける（1: 満足していない': 'commute_satisfaction',
                '誇りやプライドを持てるような仕事内容を提供してくれる環境について（1: 満足していない': 'pride_in_work_satisfaction',
                '人間関係が良好な環境について（1: 満足していない': 'relationships_satisfaction',
                '自身の行った仕事が正当に評価される体制について（1: 満足していない': 'fair_evaluation_satisfaction'
            }
            
            expectation_mapping = {
                '自分に合った勤務時間で働ける職場（1: 今の職場には期待していない': 'work_hours_expectation',
                '休日休暇がちゃんと取れる職場（1: 今の職場には期待していない': 'holidays_expectation',
                '有給休暇がちゃんと取れる職場（1: 今の職場には期待していない': 'paid_leave_expectation',
                '柔軟な勤務体系（リモートワーク、時短勤務、フレックス制など）のもとで働ける職場（1: 今の職場には期待していない': 'flex_work_expectation',
                '自宅から適切な距離で働ける職場（1: 今の職場には期待していない': 'commute_expectation',
                '誇りやプライドを持てるような仕事内容を提供してくれる職場（1: 今の職場には期待していない': 'pride_in_work_expectation',
                '人間関係が良好な職場（1: 今の職場には期待していない': 'relationships_expectation'
            }
            
            # 満足度データの処理
            for original_col, new_col in satisfaction_mapping.items():
                matching_cols = [col for col in df.columns if original_col in str(col)]
                if matching_cols:
                    df[new_col] = df[matching_cols[0]].astype(str).str.extract(r'(\d+)').astype(float)
            
            # 期待度データの処理
            for original_col, new_col in expectation_mapping.items():
                matching_cols = [col for col in df.columns if original_col in str(col)]
                if matching_cols:
                    df[new_col] = df[matching_cols[0]].astype(str).str.extract(r'(\d+)').astype(float)
            
            return df, True
        else:
            return create_professional_dummy_data(), False
            
    except Exception as e:
        st.error(f"データ読み込みエラー: {e}")
        return create_professional_dummy_data(), False

@st.cache_data
def create_professional_dummy_data():
    """プロフェッショナルなダミーデータを作成"""
    np.random.seed(42)
    n_employees = 180
    
    # より現実的な基本データ
    data = pd.DataFrame({
        'employee_id': range(1, n_employees + 1),
        'start_year': np.random.choice(range(2018, 2025), n_employees, p=[0.08, 0.12, 0.15, 0.20, 0.18, 0.15, 0.12]),
        'annual_salary': np.random.choice([350, 400, 450, 500, 550, 600, 650, 700, 800, 900, 1000, 1200], 
                                        n_employees, p=[0.05, 0.1, 0.15, 0.2, 0.15, 0.1, 0.08, 0.07, 0.05, 0.03, 0.015, 0.005]),
        'avg_monthly_overtime': np.random.choice([0, 5, 10, 15, 20, 25, 30, 40, 50, 60, 80], 
                                               n_employees, p=[0.05, 0.1, 0.15, 0.2, 0.2, 0.15, 0.08, 0.04, 0.02, 0.008, 0.002]),
        'paid_leave_usage_rate': np.random.choice([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], 
                                                n_employees, p=[0.02, 0.03, 0.05, 0.1, 0.15, 0.2, 0.25, 0.15, 0.04, 0.01])
    })
    
    # NPS（0-10のスケール）
    data['recommend_score'] = np.random.choice(range(0, 11), n_employees, 
                                             p=[0.02, 0.03, 0.05, 0.08, 0.12, 0.15, 0.18, 0.15, 0.12, 0.08, 0.02])
    
    # 総合的な評価（1-5のスケール）
    data['overall_satisfaction'] = np.random.choice(range(1, 6), n_employees, p=[0.05, 0.15, 0.35, 0.35, 0.1])
    data['long_term_intention'] = np.random.choice(range(1, 6), n_employees, p=[0.1, 0.2, 0.3, 0.3, 0.1])
    data['sense_of_contribution'] = np.random.choice(range(1, 6), n_employees, p=[0.05, 0.1, 0.25, 0.45, 0.15])
    
    # 各項目の満足度・期待度データ
    all_items = []
    for category, items in SURVEY_CATEGORIES.items():
        all_items.extend(items.keys())
    
    for item in all_items:
        # 満足度（総合満足度と相関）
        base_satisfaction = data['overall_satisfaction'].values
        noise = np.random.normal(0, 0.7, n_employees)
        satisfaction_scores = (base_satisfaction + noise).clip(1, 5).round().astype(int)
        data[f'{item}_satisfaction'] = satisfaction_scores
        
        # 期待度（満足度より若干高め）
        expectation_scores = (satisfaction_scores + np.random.normal(0.3, 0.5, n_employees)).clip(1, 5).round().astype(int)
        data[f'{item}_expectation'] = expectation_scores
    
    return data

@st.cache_data
def calculate_professional_kpis(data, is_real_data):
    """KPIを計算"""
    # NPS計算（recommend_scoreが存在しない場合の対処）
    if 'recommend_score' in data.columns and not data['recommend_score'].isna().all():
        promoters = len(data[data['recommend_score'] >= 9])
        detractors = len(data[data['recommend_score'] <= 6])
        nps = ((promoters - detractors) / len(data)) * 100
        avg_recommend_score = data['recommend_score'].mean()
    else:
        nps = 0
        avg_recommend_score = 0
    
    # 勤続年数計算（入社月のデータがないため、入社年度から概算）
    current_year = datetime.now().year
    if 'start_year' in data.columns:
        data['work_years'] = current_year - data['start_year']
    else:
        data['work_years'] = 3.5  # デフォルト値
    
    # カテゴリ別統計
    category_stats = {}
    for category, items in SURVEY_CATEGORIES.items():
        satisfaction_values = []
        expectation_values = []
        
        for item_key in items.keys():
            sat_col = f'{item_key}_satisfaction'
            exp_col = f'{item_key}_expectation'
            
            if sat_col in data.columns:
                satisfaction_values.append(data[sat_col].mean())
            if exp_col in data.columns:
                expectation_values.append(data[exp_col].mean())
        
        if satisfaction_values:
            category_stats[category] = {
                'satisfaction': np.mean(satisfaction_values),
                'expectation': np.mean(expectation_values) if expectation_values else 0,
                'gap': np.mean(satisfaction_values) - np.mean(expectation_values) if expectation_values else 0
            }
    
    # 個別項目統計
    item_stats = {}
    for category, items in SURVEY_CATEGORIES.items():
        for item_key, item_name in items.items():
            sat_col = f'{item_key}_satisfaction'
            exp_col = f'{item_key}_expectation'
            
            if sat_col in data.columns:
                item_stats[item_name] = {
                    'satisfaction': data[sat_col].mean(),
                    'expectation': data[exp_col].mean() if exp_col in data.columns else 0,
                    'gap': data[sat_col].mean() - data[exp_col].mean() if exp_col in data.columns else 0
                }
    
    # 安全にKPIを計算
    def safe_mean(col_name, default=0):
        return data[col_name].mean() if col_name in data.columns and not data[col_name].isna().all() else default
    
    return {
        'total_employees': len(data),
        'nps': nps,
        'avg_recommend_score': avg_recommend_score,
        'avg_satisfaction': safe_mean('overall_satisfaction', 3.5),
        'avg_contribution': safe_mean('sense_of_contribution', 3.5),
        'avg_long_term_intention': safe_mean('long_term_intention', 3.5),
        'avg_salary': safe_mean('annual_salary', 500),
        'median_salary': data['annual_salary'].median() if 'annual_salary' in data.columns and not data['annual_salary'].isna().all() else 500,
        'avg_overtime': safe_mean('avg_monthly_overtime', 25),
        'avg_leave_usage': safe_mean('paid_leave_usage_rate', 60),
        'avg_work_years': safe_mean('work_years', 3.5),
        'category_stats': category_stats,
        'item_stats': item_stats,
        'is_real_data': is_real_data
    }

def get_kpi_color_class(value, thresholds):
    """KPIの値に基づいて色クラスを返す"""
    if value >= thresholds['good']:
        return 'kpi-positive'
    elif value <= thresholds['bad']:
        return 'kpi-negative'
    else:
        return 'kpi-warning'

def show_professional_kpi_overview(data, kpis):
    """プロフェッショナルなKPI概要表示"""
    # メインヘッダー
    st.markdown("""
    <div class="main-header">
        <h1>Employee Survey Dashboard</h1>
        <p>Comprehensive analysis of employee satisfaction and engagement metrics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # データソース表示
    data_source = "Real Survey Data" if kpis['is_real_data'] else "Demo Data"
    st.markdown(f"**Data Source:** {data_source} | **Sample Size:** {kpis['total_employees']} employees")
    
    # KPIカード
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        nps_class = get_kpi_color_class(kpis['nps'], {'good': 10, 'bad': -10})
        st.markdown(f"""
        <div class="kpi-card {nps_class}">
            <div class="kpi-title">Employee NPS</div>
            <div class="kpi-value">{kpis['nps']:.1f}</div>
            <div class="kpi-description">Net Promoter Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        satisfaction_class = get_kpi_color_class(kpis['avg_satisfaction'], {'good': 4.0, 'bad': 2.5})
        st.markdown(f"""
        <div class="kpi-card {satisfaction_class}">
            <div class="kpi-title">Overall Satisfaction</div>
            <div class="kpi-value">{kpis['avg_satisfaction']:.2f}/5</div>
            <div class="kpi-description">Average satisfaction score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        contribution_class = get_kpi_color_class(kpis['avg_contribution'], {'good': 4.0, 'bad': 2.5})
        st.markdown(f"""
        <div class="kpi-card {contribution_class}">
            <div class="kpi-title">Contribution Level</div>
            <div class="kpi-value">{kpis['avg_contribution']:.2f}/5</div>
            <div class="kpi-description">Self-assessed performance</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        retention_class = get_kpi_color_class(kpis['avg_long_term_intention'], {'good': 4.0, 'bad': 2.5})
        st.markdown(f"""
        <div class="kpi-card {retention_class}">
            <div class="kpi-title">Retention Intent</div>
            <div class="kpi-value">{kpis['avg_long_term_intention']:.2f}/5</div>
            <div class="kpi-description">Long-term commitment</div>
        </div>
        """, unsafe_allow_html=True)
    
    # セカンダリメトリクス
    st.markdown("### Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("Average Salary", f"¥{kpis['avg_salary']:.0f}万", f"Median: ¥{kpis['median_salary']:.0f}万"),
        ("Overtime Hours", f"{kpis['avg_overtime']:.1f}h", "Monthly average"),
        ("Leave Usage", f"{kpis['avg_leave_usage']:.1f}%", "Annual vacation usage"),
        ("Avg Tenure", f"{kpis['avg_work_years']:.1f}年", "Years of service")
    ]
    
    for i, (title, value, desc) in enumerate(metrics):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-description">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

def show_professional_category_analysis(data, kpis):
    """プロフェッショナルなカテゴリ分析"""
    st.markdown('<div class="section-header"><h2>Category Analysis</h2></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Radar Analysis", "Category Ranking", "Gap Analysis"])
    
    with tab1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # レーダーチャート
        categories = list(kpis['category_stats'].keys())
        satisfaction_values = [kpis['category_stats'][cat]['satisfaction'] for cat in categories]
        expectation_values = [kpis['category_stats'][cat]['expectation'] for cat in categories]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=satisfaction_values,
            theta=categories,
            fill='toself',
            name='Satisfaction',
            line=dict(color='#3b82f6', width=3),
            fillcolor='rgba(59, 130, 246, 0.1)'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=expectation_values,
            theta=categories,
            fill='toself',
            name='Expectation',
            line=dict(color='#ef4444', width=3),
            fillcolor='rgba(239, 68, 68, 0.1)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5],
                    tickfont=dict(size=10),
                    gridcolor='#e5e7eb'
                ),
                angularaxis=dict(
                    tickfont=dict(size=11, color='#374151')
                ),
                bgcolor='rgba(255, 255, 255, 0)'
            ),
            title=dict(
                text="Satisfaction vs Expectation by Category",
                font=dict(size=16, color='#1e293b')
            ),
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            ),
            paper_bgcolor='rgba(255, 255, 255, 0)',
            plot_bgcolor='rgba(255, 255, 255, 0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # カテゴリランキング
        category_df = pd.DataFrame({
            'Category': categories,
            'Satisfaction': satisfaction_values,
            'Expectation': expectation_values,
            'Gap': [kpis['category_stats'][cat]['gap'] for cat in categories]
        }).sort_values('Satisfaction', ascending=True)
        
        fig = px.bar(
            category_df,
            x='Satisfaction',
            y='Category',
            orientation='h',
            title='Category Satisfaction Ranking',
            color='Satisfaction',
            color_continuous_scale='RdYlGn',
            range_color=[1, 5]
        )
        
        fig.update_layout(
            height=400,
            title_font_size=16,
            paper_bgcolor='rgba(255, 255, 255, 0)',
            plot_bgcolor='rgba(255, 255, 255, 0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # カテゴリ詳細テーブル
        st.markdown("#### Category Details")
        category_display = category_df.round(2)
        st.dataframe(category_display, use_container_width=True, hide_index=True)
    
    with tab3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # ギャップ分析
        gap_df = pd.DataFrame({
            'Category': categories,
            'Satisfaction': satisfaction_values,
            'Expectation': expectation_values,
            'Gap': [kpis['category_stats'][cat]['gap'] for cat in categories]
        })
        
        fig = px.scatter(
            gap_df,
            x='Satisfaction',
            y='Expectation',
            size=np.abs(gap_df['Gap']) + 0.1,
            color='Gap',
            hover_name='Category',
            title='Expectation vs Satisfaction Gap Analysis',
            color_continuous_scale='RdYlGn',
            range_x=[1, 5],
            range_y=[1, 5]
        )
        
        # 対角線追加
        fig.add_shape(
            type="line", x0=1, y0=1, x1=5, y1=5,
            line=dict(color="gray", width=2, dash="dash"),
        )
        
        fig.update_layout(
            height=500,
            title_font_size=16,
            paper_bgcolor='rgba(255, 255, 255, 0)',
            plot_bgcolor='rgba(255, 255, 255, 0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_professional_detailed_analysis(data, kpis):
    """詳細分析表示"""
    st.markdown('<div class="section-header"><h2>Detailed Item Analysis</h2></div>', unsafe_allow_html=True)
    
    # カテゴリ選択
    selected_category = st.selectbox(
        "Select category for detailed analysis:",
        list(SURVEY_CATEGORIES.keys()),
        index=0
    )
    
    if selected_category:
        st.markdown(f"### {selected_category} - Detailed Analysis")
        
        category_items = SURVEY_CATEGORIES[selected_category]
        
        # 項目別満足度
        item_data = []
        for item_key, item_name in category_items.items():
            if f'{item_key}_satisfaction' in data.columns:
                satisfaction = data[f'{item_key}_satisfaction'].mean()
                expectation = data[f'{item_key}_expectation'].mean() if f'{item_key}_expectation' in data.columns else 0
                item_data.append({
                    'Item': item_name,
                    'Satisfaction': satisfaction,
                    'Expectation': expectation,
                    'Gap': satisfaction - expectation
                })
        
        if item_data:
            item_df = pd.DataFrame(item_data).sort_values('Satisfaction', ascending=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                
                fig = px.bar(
                    item_df,
                    x='Satisfaction',
                    y='Item',
                    orientation='h',
                    title='Item Satisfaction Scores',
                    color='Satisfaction',
                    color_continuous_scale='RdYlGn',
                    range_color=[1, 5]
                )
                
                fig.update_layout(
                    height=400,
                    title_font_size=14,
                    paper_bgcolor='rgba(255, 255, 255, 0)',
                    plot_bgcolor='rgba(255, 255, 255, 0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                
                fig = px.scatter(
                    item_df,
                    x='Satisfaction',
                    y='Expectation',
                    size=np.abs(item_df['Gap']) + 0.1,
                    color='Gap',
                    hover_name='Item',
                    title='Satisfaction vs Expectation',
                    color_continuous_scale='RdYlGn',
                    range_x=[1, 5],
                    range_y=[1, 5]
                )
                
                fig.add_shape(
                    type="line", x0=1, y0=1, x1=5, y1=5,
                    line=dict(color="gray", width=2, dash="dash"),
                )
                
                fig.update_layout(
                    height=400,
                    title_font_size=14,
                    paper_bgcolor='rgba(255, 255, 255, 0)',
                    plot_bgcolor='rgba(255, 255, 255, 0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # テーブル表示
            st.markdown("#### Item Details")
            display_df = item_df.round(2)
            st.dataframe(display_df, use_container_width=True, hide_index=True)

def main():
    # サイドバー
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; text-align: center;">
            <h3 style="margin: 0; color: white;">Employee Survey</h3>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Analytics Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        # ページ選択
        page = st.radio(
            "Navigation",
            ["Dashboard Overview", "Category Analysis", "Detailed Analysis", "🤖 AI Text Analysis"],
            index=0
        )
        
        st.markdown("---")
        
        # データ情報
        st.markdown("### Data Information")
        st.info("""
        This dashboard automatically loads real Excel data when available. 
        If no real data is found, it displays professional demo data for illustration purposes.
        """)
        
        # 統計情報
        st.markdown("### Survey Metrics")
        st.markdown("""
        - **NPS Scale**: 0-10 (Net Promoter Score)
        - **Satisfaction Scale**: 1-5 (Likert Scale)
        - **Categories**: 7 main areas
        - **Total Items**: 55+ survey questions
        """)
        
        st.markdown("---")
        
        # フィルター（将来の拡張用）
        st.markdown("### Filters")
        dept_filter = st.selectbox("Department", ["All Departments", "Sales", "Engineering", "Marketing", "HR", "Finance"])
        role_filter = st.selectbox("Role Level", ["All Roles", "Junior", "Mid", "Senior", "Manager", "Director"])
        
        st.caption("*Filters will be active when real data with demographic information is loaded")
    
    # メインコンテンツ
    with st.spinner("Loading survey data..."):
        data, is_real_data = load_real_excel_data()
        kpis = calculate_professional_kpis(data, is_real_data)
    
    # ページ表示
    if page == "Dashboard Overview":
        show_professional_kpi_overview(data, kpis)
    elif page == "Category Analysis":
        show_professional_category_analysis(data, kpis)
    elif page == "Detailed Analysis":
        show_professional_detailed_analysis(data, kpis)
    
    elif page == "🤖 AI Text Analysis":
        # AIテキスト分析機能を表示
        try:
            from text_analysis_ml import show_text_analysis_ml_page
            show_text_analysis_ml_page()
        except ImportError as e:
            st.error(f"AIテキスト分析機能の読み込みに失敗しました: {e}")
            st.info("必要なライブラリ（janome, scikit-learn）がインストールされているか確認してください。")

if __name__ == "__main__":
    main()