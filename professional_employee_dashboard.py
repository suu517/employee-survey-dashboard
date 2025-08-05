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

# 日本語フォント設定
try:
    import japanize_matplotlib
except ImportError:
    # japanize_matplotlibがない場合はmatplotlibで日本語フォントを設定
    import matplotlib.pyplot as plt
    plt.rcParams['font.family'] = 'DejaVu Sans'

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
    
    /* KPIカードスタイル */
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
</style>
""", unsafe_allow_html=True)

# 実際のアンケート項目定義
SURVEY_CATEGORIES = {
    "勤務環境": {
        "work_hours": "自分に合った勤務時間で働ける",
        "holidays": "休日休暇がちゃんと取れる", 
        "paid_leave": "有給休暇がちゃんと取れる",
        "flex_work": "柔軟な勤務体系（リモートワーク、時短勤務、フレックス制など）",
        "commute": "自宅から適切な距離で働ける",
        "job_transfer": "自身の希望が十分に考慮されるような転勤体制",
        "internal_mobility": "自身の希望が十分に考慮されるような社内異動体制"
    },
    "待遇・評価": {
        "overtime_pay": "残業したらその分しっかり給与が支払われる",
        "fair_evaluation": "自身の行った仕事が正当に評価される",
        "promotion": "成果に応じて早期の昇給・昇格が望める",
        "benefits": "充実した福利厚生"
    },
    "業務量・ストレス": {
        "workload": "自分のキャパシティーに合った量の仕事で働ける",
        "physical_load": "仕事内容や量に対する身体的な負荷が少ない",
        "mental_load": "仕事内容や量に対する精神的な負荷が少ない",
        "achievable_goals": "達成可能性が見込まれる目標やノルマ"
    },
    "成長・能力開発": {
        "specialized_skills": "専門的なスキルや技術・知識や経験の獲得",
        "general_skills": "汎用的なスキル（コミュニケーション能力や論理的思考力など）の獲得",
        "training": "整った教育体制",
        "career_path": "自分に合った将来のキャリアパス設計",
        "career_match": "将来自分のなりたい方向性とマッチした仕事",
        "role_models": "身近にロールモデルとなるような人がいる環境"
    },
    "仕事のやりがい": {
        "pride_in_work": "誇りやプライドを持てるような仕事内容",
        "social_contribution": "社会に対して貢献実感を持てるような仕事",
        "job_fulfillment": "やりがいを感じられるような仕事",
        "autonomy": "自分の判断で進められる裁量のある仕事",
        "sense_of_growth": "成長実感を感じられるような仕事",
        "sense_of_achievement": "達成感を得られるような仕事",
        "impactful_work": "規模の大きなプロジェクトや仕事",
        "use_of_strengths": "自分の強みを活かせるような仕事"
    },
    "人間関係・企業文化": {
        "relationships": "人間関係が良好な環境",
        "harassment_free": "セクハラやパワハラがないような環境",
        "culture_fit": "自身の価値観や考え方と共感できるような会社の社風や文化",
        "open_communication": "意見や考え方などについて自由に言い合える風通しの良い環境",
        "learning_culture": "社内で相互に教えたり・学び合ったりするような環境",
        "work_environment": "働きやすい仕事環境やオフィス環境",
        "women_support": "女性が働きやすい環境"
    },
    "会社・事業": {
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
    """新しいExcelファイル構造に対応したデータ読み込み"""
    try:
        # Streamlit Cloud対応: プロジェクト内のdata.xlsxを優先
        excel_paths = [
            'data.xlsx',  # Streamlit Cloud用
            '/Users/sugayayoshiyuki/Desktop/採用可視化サーベイ/従業員調査.xlsx'  # ローカル用
        ]
        
        excel_path = None
        for path in excel_paths:
            if os.path.exists(path):
                excel_path = path
                break
        
        if excel_path is None:
            st.error("❌ 従業員調査データファイルが見つかりません")
            st.info("📁 data.xlsx ファイルをプロジェクトルートに配置してください")
            return create_professional_dummy_data(), False
        
        # Excelファイルを読み込む
        excel_file = pd.ExcelFile(excel_path)
        
        if 'Responses' in excel_file.sheet_names:
            # 1行目をヘッダーとして読み込み
            df = pd.read_excel(excel_path, sheet_name='Responses', header=0)
            
            print(f"読み込んだデータの形状: {df.shape}")
            
            # データの有効性を確認
            if len(df) <= 1:
                st.error(f"❌ データ件数が不足しています（{len(df)}件）")
                return create_professional_dummy_data(), False
            
            # 正常なデータを読み込み
            st.success(f"✅ 従業員調査データを正常に読み込みました（{len(df)}件）")
            
            # 基本カラムの正規化
            df = df.rename(columns=COLUMN_MAPPING)
            
            # 実際のカラム名を使用したマッピング
            actual_column_mapping = {
                '総合評価：自分の親しい友人や家族に対して、この会社への転職・就職をどの程度勧めたいと思いますか？': 'recommend_score',
                '総合満足度：自社の現在の働く環境や条件、周りの人間関係なども含めあなたはどの程度満足されていますか？': 'overall_satisfaction', 
                'あなたはこの会社でこれからも長く働きたいと思われますか？': 'long_term_intention',
                '活躍貢献度：現在の会社や所属組織であなたはどの程度、活躍貢献できていると感じますか？': 'sense_of_contribution',
                '入社年度を教えてください。※2019年入社の場合には、2019とお答えください。': 'start_year',
                '概算年収を教えてください。450万円の場合には、450と半角でお答えください。': 'annual_salary',
                '1ヶ月当たりの平均残業時間を教えてください。（残業時間が月100時間ほどある方は100とお答えください）': 'avg_monthly_overtime',
                '1年間当たりの平均有給休暇取得率を教えてください。（全て利用されていれば100、80%ほど利用されていれば80とお答えください。）': 'paid_leave_usage_rate',
                '雇用形態': 'employment_type',
                '所属事業部': 'department',
                '役職': 'position',
                '職種': 'job_type',
                '最も期待が高い項目についてあなたが期待していると回答した項目の中で最もこの会社に期待していることについて、具体的にご記載ください。どのような内容が満たせるとあなたの期待を大きく上回ることができるのか教えていただける幸いです。': 'expectation_comments',
                '最も満足度が高い項目についてあなたが今の会社に満足していると回答した項目の中で最もこの会社に満足・評価している内容について、具体的に教えていただけますと幸いです。': 'satisfaction_comments',
                '満足度が低い項目についてあなたが今の会社に満足していないと回答した項目の中で、具体的に自社のどのような点に対してそのように感じられたのか教えていただけますと幸いです。': 'dissatisfaction_comments'
            }
            
            # カラム名を正規化
            df = df.rename(columns=actual_column_mapping)
            
            # 数値データの抽出と変換
            numeric_columns = ['recommend_score', 'overall_satisfaction', 'long_term_intention', 'sense_of_contribution',
                             'start_year', 'annual_salary', 'avg_monthly_overtime', 'paid_leave_usage_rate']
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 期待度項目の識別パターン
            expectation_patterns = {
                '勤務時間': 'work_hours',
                '休日休暇がちゃんと取れる': 'holidays',
                '有給休暇がちゃんと取れる': 'paid_leave',
                '柔軟な勤務体系': 'flex_work',
                '自宅から適切な距離': 'commute',
                '転勤体制': 'job_transfer',
                '社内異動': 'internal_mobility',
                '残業代': 'overtime_pay',
                '仕事量': 'workload',
                '身体的負荷': 'physical_load',
                '精神的負荷': 'mental_load',
                '福利厚生': 'benefits',
                '正当に評価': 'fair_evaluation',
                '昇給・昇格': 'promotion',
                '目標やノルマ': 'achievable_goals',
                '専門的なスキル': 'specialized_skills',
                '汎用的なスキル': 'general_skills',
                '教育体制': 'training',
                'キャリアパス': 'career_path',
                '将来.*マッチ': 'career_match',
                'ロールモデル': 'role_models',
                '誇り.*プライド': 'pride_in_work',
                '社会.*貢献': 'social_contribution',
                'やりがい': 'job_fulfillment',
                '裁量': 'autonomy',
                '成長実感': 'sense_of_growth',
                '達成感': 'sense_of_achievement',
                '大きな.*プロジェクト': 'impactful_work',
                '強み.*活かす': 'use_of_strengths',
                '人間関係': 'relationships',
                'ハラスメント': 'harassment_free',
                '社風.*文化': 'culture_fit',
                '風通し': 'open_communication',
                '相互.*学び': 'learning_culture',
                '事業基盤': 'company_stability',
                '経営戦略': 'management_strategy',
                '競合優位性': 'competitive_edge',
                'ブランド力': 'brand_power',
                'ミッション.*バリュー': 'mission_vision_fit',
                '法令遵守': 'compliance',
                'オフィス環境': 'work_environment',
                '女性.*働きやすい': 'women_support'
            }
            
            # 期待度・満足度データの処理
            expectation_columns = {}
            satisfaction_columns = {}
            
            for col in df.columns:
                col_str = str(col)
                
                # 期待度項目の識別
                if '今の職場には期待' in col_str or '期待していない' in col_str:
                    for pattern, key in expectation_patterns.items():
                        if re.search(pattern, col_str):
                            expectation_columns[col] = f'{key}_expectation'
                            break
                
                # 満足度項目の識別  
                elif '満足していない' in col_str or '満足している' in col_str:
                    for pattern, key in expectation_patterns.items():
                        if re.search(pattern, col_str):
                            satisfaction_columns[col] = f'{key}_satisfaction'
                            break
            
            # 期待度・満足度データの変換
            for original_col, new_col in expectation_columns.items():
                if original_col in df.columns:
                    df[new_col] = pd.to_numeric(df[original_col], errors='coerce')
            
            for original_col, new_col in satisfaction_columns.items():
                if original_col in df.columns:
                    df[new_col] = pd.to_numeric(df[original_col], errors='coerce')
            
            print(f"処理後のデータ形状: {df.shape}")
            print(f"期待度項目数: {len(expectation_columns)}")
            print(f"満足度項目数: {len(satisfaction_columns)}")
            
            # 最終的なデータを返す（150件の実データ）
            return df, True
        else:
            st.warning("'Responses'シートが見つかりません。ダミーデータを使用します。")
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
    
    # テキストマイニング用のサンプルコメントを追加
    positive_comments = [
        '職場の人間関係が良好で働きやすい環境です',
        'リモートワークが導入されてワークライフバランスが改善されました',
        '上司からのサポートが充実していて成長できる環境です',
        '福利厚生が充実していて安心して働けます',
        '挑戦的なプロジェクトに参加できて成長実感があります',
        '社内研修制度が整っていてスキルアップできます',
        'フレックス制度があり自分のペースで仕事ができます',
        '評価制度が透明で公正な評価を受けられます'
    ]
    
    negative_comments = [
        '残業時間が多くワークライフバランスが取りにくい',
        '昇進・昇格の基準が不透明で将来が見えにくい',
        '業務量が多すぎて精神的な負担が大きい',
        '有給休暇が取りにくい職場環境です',
        'コミュニケーション不足で情報共有が不十分',
        '給与水準が他社と比べて低いと感じます',
        '教育体制が不十分でスキルアップが困難',
        '職場の設備が古く作業効率が悪い'
    ]
    
    neutral_comments = [
        '全体的には普通の職場だと思います',
        '良い面と悪い面が両方あります',
        '可もなく不可もない職場環境です',
        '改善の余地はありますが悪くはありません'
    ]
    
    # 満足度に応じてコメントを分配
    comments = []
    expectation_detail_comments = []
    
    for i in range(n_employees):
        satisfaction = data.loc[i, 'overall_satisfaction']
        
        if satisfaction >= 4:
            comment = np.random.choice(positive_comments)
            exp_comment = 'さらなる成長機会とキャリア開発支援を期待しています'
        elif satisfaction <= 2:
            comment = np.random.choice(negative_comments)
            exp_comment = 'ワークライフバランスの改善と労働環境の整備を強く希望します'
        else:
            comment = np.random.choice(neutral_comments)
            exp_comment = '職場環境の改善と業務効率化を期待しています'
        
        comments.append(comment)
        expectation_detail_comments.append(exp_comment)
    
    data['satisfaction_comments'] = comments
    data['dissatisfaction_comments'] = [c for c in comments if any(neg in c for neg in ['残業', '負担', '不透明', '困難', '不十分', '低い'])]
    data['expectation_comments'] = expectation_detail_comments
    
    # dissatisfaction_commentsが空の場合は、ダミーコメントを追加
    if len(data['dissatisfaction_comments']) == 0:
        data.loc[:min(30, len(data)-1), 'dissatisfaction_comments'] = negative_comments[:min(31, len(data))]
    
    return data

@st.cache_data
def calculate_professional_kpis(data, is_real_data):
    """更新されたKPI計算"""
    # 勤続年数計算
    current_year = datetime.now().year
    if 'start_year' in data.columns:
        data['work_years'] = current_year - data['start_year']
    else:
        data['work_years'] = 3.5
    
    # NPS計算（1-5スケールを0-10に変換）
    if 'recommend_score' in data.columns and not data['recommend_score'].isna().all():
        recommend_scaled = data['recommend_score'] * 2  # 1-5 → 2-10
        promoters = len(recommend_scaled[recommend_scaled >= 9])
        detractors = len(recommend_scaled[recommend_scaled <= 6])
        nps = ((promoters - detractors) / len(data)) * 100
        avg_recommend_score = data['recommend_score'].mean()
    else:
        nps = 0
        avg_recommend_score = 0
    
    # カテゴリ別統計
    category_stats = {}
    for category, items in SURVEY_CATEGORIES.items():
        satisfaction_values = []
        expectation_values = []
        
        for item_key in items.keys():
            sat_col = f'{item_key}_satisfaction'
            exp_col = f'{item_key}_expectation'
            
            if sat_col in data.columns and not data[sat_col].isna().all():
                satisfaction_values.append(data[sat_col].mean())
            if exp_col in data.columns and not data[exp_col].isna().all():
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
            
            if sat_col in data.columns and not data[sat_col].isna().all():
                item_stats[item_name] = {
                    'satisfaction': data[sat_col].mean(),
                    'expectation': data[exp_col].mean() if exp_col in data.columns and not data[exp_col].isna().all() else 0,
                    'gap': data[sat_col].mean() - data[exp_col].mean() if exp_col in data.columns and not data[exp_col].isna().all() else 0
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
        'is_real_data': is_real_data,
        'data_source': "Real Survey Data (150 responses)" if is_real_data else "Demo Data"
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
    """KPI概要を表示（カスタムボックス使用）"""
    st.header("📊 従業員調査ダッシュボード")
    
    # 情報ボックス
    data_source = kpis.get('data_source', "デモデータ")
    st.info(f"📅 **データ最終更新:** {datetime.now().strftime('%Y/%m/%d %H:%M')} | 📋 **データソース:** {data_source} | 👥 **サンプルサイズ:** {kpis['total_employees']}人")
    
    if not kpis:
        st.error("KPIデータが利用できません")
        return
    
    st.subheader("🎯 主要指標")
    
    # メインKPI（カスタムボックス使用）
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        nps_class = "kpi-card-blue" if kpis['nps'] >= 7 else "kpi-card-red" if kpis['nps'] <= 5 else "kpi-card-orange"
        nps_status = "良好" if kpis['nps'] >= 7 else "要改善" if kpis['nps'] <= 5 else "普通"
        st.markdown(f"""
        <div class="kpi-card {nps_class}">
            <div class="kpi-title">📈 従業員NPS</div>
            <div class="kpi-value">{kpis['nps']:.1f}</div>
            <div class="kpi-change">{nps_status} • 推奨度スコア</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        satisfaction = kpis['avg_satisfaction']
        sat_class = "kpi-card-green" if satisfaction >= 4 else "kpi-card-red" if satisfaction <= 2.5 else "kpi-card-orange"
        sat_status = "良好" if satisfaction >= 4 else "要改善" if satisfaction <= 2.5 else "普通"
        st.markdown(f"""
        <div class="kpi-card {sat_class}">
            <div class="kpi-title">😊 総合満足度</div>
            <div class="kpi-value">{satisfaction:.2f}<span class="kpi-unit">/5</span></div>
            <div class="kpi-change">{sat_status} • 平均満足度スコア</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        contribution = kpis['avg_contribution']
        cont_class = "kpi-card-green" if contribution >= 4 else "kpi-card-red" if contribution <= 2.5 else "kpi-card-orange"
        cont_status = "高い" if contribution >= 4 else "低い" if contribution <= 2.5 else "普通"
        st.markdown(f"""
        <div class="kpi-card {cont_class}">
            <div class="kpi-title">⭐ 活躍貢献度</div>
            <div class="kpi-value">{contribution:.2f}<span class="kpi-unit">/5</span></div>
            <div class="kpi-change">{cont_status} • 自己評価パフォーマンス</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        intention = kpis['avg_long_term_intention']
        int_class = "kpi-card-green" if intention >= 4 else "kpi-card-red" if intention <= 2.5 else "kpi-card-orange"
        int_status = "高い" if intention >= 4 else "低い" if intention <= 2.5 else "普通"
        st.markdown(f"""
        <div class="kpi-card {int_class}">
            <div class="kpi-title">🏢 勤続意向</div>
            <div class="kpi-value">{intention:.2f}<span class="kpi-unit">/5</span></div>
            <div class="kpi-change">{int_status} • 長期コミットメント</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("📊 基本指標")
    
    # サブKPI（カスタムボックス使用）
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">💰 平均年収</div>
            <div class="kpi-value">¥{kpis['avg_salary']:.0f}<span class="kpi-unit">万</span></div>
            <div class="kpi-change">中央値: ¥{kpis['median_salary']:.0f}万 • 給与水準</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        overtime_class = "kpi-card-red" if kpis['avg_overtime'] >= 40 else "kpi-card-green" if kpis['avg_overtime'] <= 20 else "kpi-card-orange"
        overtime_status = "多い" if kpis['avg_overtime'] >= 40 else "適正" if kpis['avg_overtime'] <= 20 else "普通"
        st.markdown(f"""
        <div class="kpi-card {overtime_class}">
            <div class="kpi-title">⏰ 残業時間</div>
            <div class="kpi-value">{kpis['avg_overtime']:.1f}<span class="kpi-unit">時間</span></div>
            <div class="kpi-change">{overtime_status} • 月平均</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        leave_class = "kpi-card-green" if kpis['avg_leave_usage'] >= 80 else "kpi-card-red" if kpis['avg_leave_usage'] <= 50 else "kpi-card-orange"
        leave_status = "良好" if kpis['avg_leave_usage'] >= 80 else "低い" if kpis['avg_leave_usage'] <= 50 else "普通"
        st.markdown(f"""
        <div class="kpi-card {leave_class}">
            <div class="kpi-title">🏖️ 有給取得率</div>
            <div class="kpi-value">{kpis['avg_leave_usage']:.1f}<span class="kpi-unit">%</span></div>
            <div class="kpi-change">{leave_status} • 年間休暇利用率</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">👤 平均勤続年数</div>
            <div class="kpi-value">{kpis['avg_work_years']:.1f}<span class="kpi-unit">年</span></div>
            <div class="kpi-change">組織定着度 • 勤続年数</div>
        </div>
        """, unsafe_allow_html=True)

def show_professional_category_analysis(data, kpis):
    """満足度分析を表示"""
    st.header("📈 カテゴリ別満足度分析")
    
    if not kpis or 'category_stats' not in kpis:
        st.error("満足度データが利用できません")
        return
    
    tab1, tab2, tab3 = st.tabs(["📊 レーダーチャート", "📋 満足度ランキング", "🎯 期待度ギャップ分析"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # 満足度レーダーチャート
            categories = list(kpis['category_stats'].keys())
            satisfaction_values = [kpis['category_stats'][cat]['satisfaction'] for cat in categories]
            
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
            if 'category_stats' in kpis:
                expectation_values = [kpis['category_stats'][cat]['expectation'] for cat in categories]
                
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
        categories = list(kpis['category_stats'].keys())
        satisfaction_values = [kpis['category_stats'][cat]['satisfaction'] for cat in categories]
        
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
        
        # 詳細テーブル
        st.subheader("📋 カテゴリ詳細データ")
        display_df = satisfaction_df.sort_values('満足度', ascending=False).round(2)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    with tab3:
        # ギャップ分析（4象限マトリックス）
        if 'category_stats' in kpis:
            expectation_values = [kpis['category_stats'][cat]['expectation'] for cat in categories]
            gap_values = [kpis['category_stats'][cat]['gap'] for cat in categories]
            
            gap_df = pd.DataFrame({
                'カテゴリ': categories,
                '満足度': satisfaction_values,
                '期待度': expectation_values,
                'ギャップ': gap_values
            })
            
            # 4象限マトリックス分析
            st.subheader("📊 期待度 vs 満足度 マトリックス分析")
            
            # 中央値を基準とした4象限
            satisfaction_median = np.median(satisfaction_values)
            expectation_median = np.median(expectation_values)
            
            # 4象限の分類
            def classify_quadrant(satisfaction, expectation, sat_med, exp_med):
                if satisfaction >= sat_med and expectation >= exp_med:
                    return "🔥 重点改善領域\n(高期待・高満足)"
                elif satisfaction < sat_med and expectation >= exp_med:
                    return "⚠️ 最優先改善領域\n(高期待・低満足)"
                elif satisfaction >= sat_med and expectation < exp_med:
                    return "✅ 維持領域\n(低期待・高満足)"
                else:
                    return "💤 低優先度領域\n(低期待・低満足)"
            
            gap_df['象限'] = gap_df.apply(
                lambda row: classify_quadrant(row['満足度'], row['期待度'], satisfaction_median, expectation_median), 
                axis=1
            )
            
            # 4象限散布図
            fig = px.scatter(
                gap_df,
                x='満足度',
                y='期待度',
                size=np.abs(gap_df['ギャップ']) + 0.1,
                color='象限',
                hover_name='カテゴリ',
                title='期待度 vs 満足度 4象限マトリックス',
                range_x=[1, 5],
                range_y=[1, 5],
                color_discrete_map={
                    '⚠️ 最優先改善領域\n(高期待・低満足)': '#ef4444',
                    '🔥 重点改善領域\n(高期待・高満足)': '#f59e0b', 
                    '💤 低優先度領域\n(低期待・低満足)': '#94a3b8',
                    '✅ 維持領域\n(低期待・高満足)': '#22c55e'
                }
            )
            
            # 中央線を追加
            fig.add_hline(y=expectation_median, line_dash="dash", line_color="gray", opacity=0.7)
            fig.add_vline(x=satisfaction_median, line_dash="dash", line_color="gray", opacity=0.7)
            
            # 対角線追加
            fig.add_shape(
                type="line", x0=1, y0=1, x1=5, y1=5,
                line=dict(color="lightgray", width=1, dash="dot"),
            )
            
            # 象限ラベルを追加
            fig.add_annotation(x=satisfaction_median + 0.8, y=expectation_median + 0.8, 
                             text="🔥重点改善", showarrow=False, font=dict(size=12, color="orange"))
            fig.add_annotation(x=satisfaction_median - 0.8, y=expectation_median + 0.8,
                             text="⚠️最優先改善", showarrow=False, font=dict(size=12, color="red"))
            fig.add_annotation(x=satisfaction_median + 0.8, y=expectation_median - 0.8,
                             text="✅維持", showarrow=False, font=dict(size=12, color="green"))
            fig.add_annotation(x=satisfaction_median - 0.8, y=expectation_median - 0.8,
                             text="💤低優先度", showarrow=False, font=dict(size=12, color="gray"))
            
            fig.update_layout(
                height=600,
                xaxis_title="満足度 (1-5点)",
                yaxis_title="期待度 (1-5点)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 象限別分析
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📋 象限別カテゴリ分類")
                quadrant_summary = gap_df.groupby('象限')['カテゴリ'].apply(list).to_dict()
                
                for quadrant, categories_list in quadrant_summary.items():
                    with st.expander(f"{quadrant} ({len(categories_list)}項目)"):
                        for cat in categories_list:
                            cat_data = gap_df[gap_df['カテゴリ'] == cat].iloc[0]
                            st.write(f"• **{cat}** (満足度: {cat_data['満足度']:.2f}, 期待度: {cat_data['期待度']:.2f})")
            
            with col2:
                st.subheader("🎯 改善優先度ランキング")
                
                # 改善優先度の計算（期待度が高く満足度が低いものほど優先度高）
                gap_df['改善優先度'] = gap_df['期待度'] - gap_df['満足度']
                priority_df = gap_df.sort_values('改善優先度', ascending=False)
                
                for i, (_, row) in enumerate(priority_df.head(5).iterrows(), 1):
                    priority_emoji = "🔴" if i <= 2 else "🟡" if i <= 4 else "🟢"
                    st.write(f"{priority_emoji} **{i}. {row['カテゴリ']}**")
                    st.write(f"   期待度: {row['期待度']:.2f} | 満足度: {row['満足度']:.2f} | ギャップ: {row['改善優先度']:.2f}")
            
            # 詳細データテーブル
            st.subheader("📊 詳細分析データ")
            display_df = gap_df[['カテゴリ', '満足度', '期待度', 'ギャップ', '象限', '改善優先度']].round(2)
            display_df = display_df.sort_values('改善優先度', ascending=False)
            st.dataframe(display_df, use_container_width=True, hide_index=True)

def show_professional_detailed_analysis(data, kpis):
    """詳細分析表示"""
    st.markdown('<div class="section-header"><h2>🏢 詳細項目分析</h2></div>', unsafe_allow_html=True)
    
    # カテゴリ選択
    selected_category = st.selectbox(
        "📊 詳細分析するカテゴリを選択してください:",
        list(SURVEY_CATEGORIES.keys()),
        index=0
    )
    
    if selected_category:
        st.markdown(f"### {selected_category} - 詳細分析")
        
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
            ["📊 ダッシュボード概要", "📈 カテゴリ別分析", "🏢 詳細分析", "🔬 重回帰分析", "📝 テキストマイニング", "🤖 AIテキスト分析"],
            index=0
        )
        
        st.markdown("---")
        
        # データ情報
        st.markdown("### 📊 データ情報")
        st.info("""
        このダッシュボードは150件の従業員調査データを自動読み込みし、
        総合的な分析結果を提供します。
        """)
        
        # 統計情報
        st.markdown("### 📊 調査指標")
        st.markdown("""
        - **推奨度スケール**: 0-10 (Net Promoter Score)
        - **満足度スケール**: 1-5 (リッカート尺度)
        - **分析カテゴリ**: 7つの主要領域
        - **調査項目数**: 55項目以上
        """)
        
        st.markdown("---")
        
        # フィルター（将来の拡張用）
        st.markdown("### 🔍 フィルター")
        dept_filter = st.selectbox("所属部署", ["全部署", "営業部", "開発部", "マーケティング部", "人事部", "経理部"])
        role_filter = st.selectbox("役職前り", ["全役職", "ジュニア", "ミドル", "シニア", "マネージャー", "ディレクター"])
        
        st.caption("*フィルター機能は現在開発中です")
    
    # メインコンテンツ
    with st.spinner("📊 従業員調査データを読み込み中..."):
        data, is_real_data = load_real_excel_data()
        kpis = calculate_professional_kpis(data, is_real_data)
    
    # データ状況の表示
    if is_real_data:
        st.success(f"✅ 従業員調査データ（{len(data)}件）を正常に読み込みました")
        st.info("📊 このダッシュボードは最新の従業員調査結果を分析しています")
    else:
        st.error("❌ 従業員調査データファイルが見つかりません")
        st.info("📁 data.xlsx ファイルをプロジェクトルートに配置してください")
    
    # ページ表示
    if page == "📊 ダッシュボード概要":
        show_professional_kpi_overview(data, kpis)
    elif page == "📈 カテゴリ別分析":
        show_professional_category_analysis(data, kpis)
    elif page == "🏢 詳細分析":
        show_professional_detailed_analysis(data, kpis)
    elif page == "🔬 重回帰分析":
        show_professional_regression_analysis(data, kpis)
    elif page == "📝 テキストマイニング":
        show_professional_text_mining(data, kpis)
    elif page == "🤖 AIテキスト分析":
        # AIテキスト分析機能を表示
        try:
            from text_analysis_ml import show_text_analysis_ml_page
            show_text_analysis_ml_page()
        except ImportError as e:
            st.error(f"AIテキスト分析機能の読み込みに失敗しました: {e}")
            st.info("必要なライブラリ（janome, scikit-learn）がインストールされているか確認してください。")

def show_professional_regression_analysis(data, kpis):
    """重回帰分析を表示"""
    st.markdown('<div class="section-header"><h2>🔬 Multiple Regression Analysis</h2></div>', unsafe_allow_html=True)
    st.markdown("主要指標に対する満足度項目の影響力を分析します")
    
    # 目的変数の選択
    target_options = {
        'eNPS (推奨度)': 'recommend_score',
        '総合満足度': 'overall_satisfaction', 
        '勤続意向': 'long_term_intention',
        '活躍貢献度': 'sense_of_contribution'
    }
    
    selected_target = st.selectbox(
        "🎯 分析対象（目的変数）を選択してください",
        list(target_options.keys())
    )
    
    target_col = target_options[selected_target]
    
    if target_col not in data.columns:
        st.error(f"目的変数 '{target_col}' がデータに含まれていません")
        return
    
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import r2_score, mean_squared_error
        import scipy.stats as stats
        
        # 説明変数（満足度項目）を準備
        explanatory_vars = []
        var_names = []
        
        # 実データの満足度項目を検索
        satisfaction_patterns = [
            '自分に合った勤務時間で働ける',
            '休日休暇がちゃんと取れる', 
            '有給休暇がちゃんと取れる',
            '柔軟な勤務体系',
            '人間関係が良好な',
            '仕事内容や量に対する精神的な負荷',
            '充実した福利厚生',
            '自身の行った仕事が正当に評価される',
            '成果に応じて早期の昇給・昇格'
        ]
        
        for col in data.columns:
            col_str = str(col)
            # 満足度項目を検索（「満足している」を含むカラム）
            if any(pattern in col_str for pattern in satisfaction_patterns) and '満足している' in col_str:
                explanatory_vars.append(col)
                # 簡潔な名前を抽出
                short_name = col_str.split('（')[0].replace('満足している', '').replace('について', '')
                var_names.append(short_name[:20])  # 20文字まで
        
        # ダミーデータの場合は従来の方法を使用
        if len(explanatory_vars) == 0 and hasattr(data, 'columns') and any('_satisfaction' in str(col) for col in data.columns):
            for category, items in SURVEY_CATEGORIES.items():
                for item_key, item_name in items.items():
                    sat_col = f'{item_key}_satisfaction'
                    if sat_col in data.columns:
                        explanatory_vars.append(sat_col)
                        var_names.append(item_name)
        
        if len(explanatory_vars) < 2:
            st.error("分析に必要な説明変数が不足しています")
            return
        
        # データの準備
        try:
            X = data[explanatory_vars]
            y = data[target_col]
            
            st.info(f"分析対象: {len(explanatory_vars)}個の説明変数、{len(data)}件のデータ")
            
        except KeyError as e:
            st.error(f"必要なカラムが見つかりません: {e}")
            st.info("利用可能なカラム:")
            st.write(list(data.columns))
            return
        
        # データの数値化とクリーニング
        X_clean = X.copy()
        y_clean = y.copy()
        
        # 数値化
        for col in X_clean.columns:
            X_clean[col] = pd.to_numeric(X_clean[col], errors='coerce')
        y_clean = pd.to_numeric(y_clean, errors='coerce')
        
        # 欠損値処理
        X_clean = X_clean.fillna(X_clean.mean())
        y_clean = y_clean.fillna(y_clean.mean())
        
        # 無効なデータを除外
        valid_mask = ~(X_clean.isna().any(axis=1) | y_clean.isna())
        X_final = X_clean[valid_mask]
        y_final = y_clean[valid_mask]
        
        if len(X_final) < 10:
            st.error(f"有効なデータが不足です（{len(X_final)}件）。分析には最低10件が必要です。")
            return
            
        # 重回帰分析実行
        model = LinearRegression()
        model.fit(X_final, y_final)
        
        y_pred = model.predict(X_final)
        r2 = r2_score(y_final, y_pred)
        mse = mean_squared_error(y_final, y_pred)
        
        # 結果表示
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>📊 モデル性能</h3>
                <p style="font-size: 1.5rem; font-weight: bold; color: #3b82f6;">
                    R² = {r2:.3f}
                </p>
                <p>決定係数（予測精度）</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>🎯 予測誤差</h3>
                <p style="font-size: 1.5rem; font-weight: bold; color: #10b981;">
                    RMSE = {np.sqrt(mse):.3f}
                </p>
                <p>平均二乗誤差の平方根</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 係数の重要度をプロット
        if len(var_names) == len(model.coef_):
            coefficients = pd.DataFrame({
                'Variable': var_names,
                'Coefficient': model.coef_,
                'Abs_Coefficient': np.abs(model.coef_)
            }).sort_values('Abs_Coefficient', ascending=True)
        else:
            # フォールバック: カラム名を使用
            coefficients = pd.DataFrame({
                'Variable': [f'Var_{i}' for i in range(len(model.coef_))],
                'Coefficient': model.coef_,
                'Abs_Coefficient': np.abs(model.coef_)
            }).sort_values('Abs_Coefficient', ascending=True)
        
        fig = px.bar(
            coefficients.tail(15), 
            x='Coefficient', 
            y='Variable',
            orientation='h',
            title=f"{selected_target}への影響度（回帰係数）",
            color='Coefficient',
            color_continuous_scale='RdBu_r'
        )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            template="plotly_white",
            font=dict(family="Arial, sans-serif")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 詳細統計
        with st.expander("📋 詳細統計"):
            if len(var_names) == len(model.coef_):
                results_df = pd.DataFrame({
                    '項目': var_names,
                    '回帰係数': model.coef_.round(4),
                    '絶対値': np.abs(model.coef_).round(4)
                }).sort_values('絶対値', ascending=False)
            else:
                results_df = pd.DataFrame({
                    '項目': [f'Variable_{i}' for i in range(len(model.coef_))],
                    '回帰係数': model.coef_.round(4),
                    '絶対値': np.abs(model.coef_).round(4)
                }).sort_values('絶対値', ascending=False)
            
            st.dataframe(results_df, use_container_width=True)
            
            # デバッグ情報
            st.write(f"説明変数数: {len(explanatory_vars)}")
            st.write(f"使用したカラム: {explanatory_vars[:5]}...") # 最初の5個を表示
            
    except ImportError as e:
        st.error(f"必要なライブラリが見つかりません: {e}")
        st.info("scikit-learn, scipy をインストールしてください")
    except Exception as e:
        st.error(f"回帰分析中にエラーが発生しました: {e}")

def show_professional_text_mining(data, kpis):
    """テキストマイニングを表示"""
    st.markdown('<div class="section-header"><h2>📝 テキストマイニング分析</h2></div>', unsafe_allow_html=True)
    
    # テキストデータの確認
    text_columns = []
    for col in data.columns:
        if 'comment' in col.lower() or 'コメント' in str(col):
            if data[col].notna().sum() > 0:
                text_columns.append(col)
    
    if not text_columns:
        st.warning("テキストデータが見つかりません")
        return
    
    selected_text_col = st.selectbox(
        "分析するテキスト項目を選択してください",
        text_columns
    )
    
    try:
        from collections import Counter
        import re
        
        # テキストデータの前処理
        text_data = data[selected_text_col].dropna()
        
        if len(text_data) == 0:
            st.warning("選択された項目にテキストデータがありません")
            return
        
        # 日本語テキストの前処理とキーワード抽出
        all_text = ' '.join(text_data.astype(str))
        
        # ノイズ文字を除去
        all_text = re.sub(r'[\n\r\t]+', ' ', all_text)  # 改行、タブをスペースに
        all_text = re.sub(r'[0-9０-９]+', '', all_text)  # 数字を除去
        
        # 日本語の単語を抽出（ひらがな、カタカナ、漢字）
        japanese_pattern = r'[ぁ-んァ-ヶー一-龯]{2,}'
        words = re.findall(japanese_pattern, all_text)
        
        # 一般的なストップワードを除外
        stop_words = [
            'です', 'である', 'であり', 'あります', 'います', 'します', 'している',
            'こと', 'もの', 'この', 'その', 'あの', 'どの', 'など', 'などの',
            'ことが', 'ことで', 'ことに', 'ことを', 'ため', 'よう', 'ように',
            'ている', 'ています', 'ており', 'てあり'
        ]
        words = [word for word in words if word not in stop_words and len(word) >= 2]
        
        # 頻出単語をカウント
        word_freq = Counter(words)
        
        # デバッグ情報
        st.info(f"🔍 抽出した全単語数: {len(words)}, ユニーク単語数: {len(word_freq)}")
        
        if len(word_freq) == 0:
            st.warning("キーワードが抽出されませんでした")
            st.info("テキストデータの内容を確認してください。")
            # デバッグ: 元テキストを表示
            with st.expander("🔍 デバッグ: 元テキストサンプル"):
                st.write(f"全テキストの最初の500文字:")
                st.text(all_text[:500])
            return
        
        # 結果表示
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔤 頻出キーワード トップ20")
            top_words = word_freq.most_common(20)
            
            if top_words:
                words_df = pd.DataFrame(top_words, columns=['単語', '出現回数'])
                st.dataframe(words_df, use_container_width=True)
            else:
                st.info("抽出されたキーワードがありません")
        
        with col2:
            st.subheader("📊 キーワード出現頻度")
            if top_words:
                words_df = pd.DataFrame(top_words[:10], columns=['単語', '出現回数'])
                
                fig = px.bar(
                    words_df, 
                    x='出現回数', 
                    y='単語',
                    orientation='h',
                    title="トップ10 キーワード",
                    color='出現回数',
                    color_continuous_scale='Blues'
                )
                
                fig.update_layout(
                    height=400,
                    template="plotly_white",
                    yaxis={'categoryorder': 'total ascending'},
                    font=dict(family="Arial, sans-serif")
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # テキスト統計
        st.subheader("📈 テキスト統計")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("総コメント数", len(text_data))
        
        with col2:
            avg_length = text_data.str.len().mean()
            st.metric("平均文字数", f"{avg_length:.1f}")
        
        with col3:
            st.metric("ユニークキーワード数", len(word_freq))
        
        # 代表的なコメント
        with st.expander("💬 代表的なコメント"):
            sample_comments = text_data.sample(min(5, len(text_data)))
            for i, comment in enumerate(sample_comments, 1):
                st.write(f"**{i}.** {comment}")
                
    except Exception as e:
        st.error(f"テキスト分析中にエラーが発生しました: {e}")
        st.info("テキストデータの形式を確認してください")

if __name__ == "__main__":
    main()