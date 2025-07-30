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
    """従業員調査データを読み込む（実データ対応）"""
    try:
        excel_path = './data.xlsx'
        
        if not os.path.exists(excel_path):
            st.error("データファイル 'data.xlsx' が見つかりません")
            return create_dummy_data()
        
        # Responsesシートから実データを読み込む
        try:
            responses_df = pd.read_excel(excel_path, sheet_name='Responses')
            
            # ヘッダー行（1行目）を取得して列名として使用
            if len(responses_df) >= 1:
                # 1行目をヘッダーとして設定
                header_row = responses_df.iloc[0]
                responses_df = responses_df.iloc[1:].reset_index(drop=True)
                responses_df.columns = header_row
                
                # データが存在する場合は実データを処理
                if len(responses_df) > 0:
                    processed_data = process_real_survey_data(responses_df)
                    return processed_data
                
        except Exception as e:
            st.error(f"Responsesシートの読み込みエラー: {e}")
        
        # 実データの処理に失敗した場合はダミーデータを返す
        return create_dummy_data()
        
    except Exception as e:
        st.error(f"データ読み込みエラー: {e}")
        return create_dummy_data()

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
    n_employees = 50
    
    employee_data = pd.DataFrame({
        'response_id': range(1, n_employees + 1),
        'department': np.random.choice(['マーケティング部', 'エンジニアリング部', '人事部', '営業部'], n_employees),
        'position': np.random.choice(['役職なし', 'チームリーダー', 'マネージャー'], n_employees),
        'start_year': np.random.choice(range(2018, 2025), n_employees),
        'annual_salary': np.random.normal(500, 100, n_employees).clip(300, 1000).astype(int),
        'monthly_overtime': np.random.normal(20, 10, n_employees).clip(0, 60).astype(int),
        'paid_leave_rate': np.random.normal(60, 20, n_employees).clip(10, 100).astype(int),
        'nps_score': np.random.choice(range(0, 11), n_employees),
        'overall_satisfaction': np.random.choice(range(1, 6), n_employees),
        'long_term_intention': np.random.choice(range(1, 6), n_employees),
        'contribution_score': np.random.choice(range(1, 6), n_employees),
    })
    
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
    
    # NPS計算
    promoters = len(df[df['nps_score'] >= 9])
    detractors = len(df[df['nps_score'] <= 6])
    nps = ((promoters - detractors) / len(df)) * 100 if len(df) > 0 else 0
    
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
    """KPI概要を表示"""
    st.markdown('<div class="section-header"><h2>📊 総合KPIダッシュボード</h2></div>', unsafe_allow_html=True)
    
    # データ状況の表示
    df = data['employee_data']
    st.markdown(f"""
    <div class="data-status">
        <strong>📅 データ最終更新:</strong> {datetime.now().strftime('%Y/%m/%d %H:%M')} | 
        <strong>👥 回答者数:</strong> {len(df)}名 | 
        <strong>📋 調査項目:</strong> {len(df.columns)}項目
    </div>
    """, unsafe_allow_html=True)
    
    if not kpis:
        st.error("KPIデータが利用できません")
        return
    
    # メインKPI（改良版デザイン）
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        nps_class = "kpi-card-green" if kpis['nps'] > 0 else "kpi-card-red" if kpis['nps'] < -10 else "kpi-card-orange"
        st.markdown(f"""
        <div class="kpi-card {nps_class}">
            <div class="kpi-title">eNPS</div>
            <div class="kpi-value">{kpis['nps']:.1f}</div>
            <div class="kpi-change">
                <span class="kpi-icon">📈</span>
                推奨度指標
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        satisfaction = kpis['avg_satisfaction']
        sat_class = "kpi-card-green" if satisfaction >= 4 else "kpi-card-red" if satisfaction <= 2.5 else "kpi-card-orange"
        st.markdown(f"""
        <div class="kpi-card {sat_class}">
            <div class="kpi-title">総合満足度</div>
            <div class="kpi-value">{satisfaction:.2f}<span class="kpi-unit">/5</span></div>
            <div class="kpi-change">
                <span class="kpi-icon">😊</span>
                満足度平均
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        contribution = kpis['avg_contribution']
        cont_class = "kpi-card-green" if contribution >= 4 else "kpi-card-red" if contribution <= 2.5 else "kpi-card-orange"
        st.markdown(f"""
        <div class="kpi-card {cont_class}">
            <div class="kpi-title">活躍貢献度</div>
            <div class="kpi-value">{contribution:.2f}<span class="kpi-unit">/5</span></div>
            <div class="kpi-change">
                <span class="kpi-icon">⭐</span>
                パフォーマンス
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        intention = kpis['avg_long_term_intention']
        int_class = "kpi-card-green" if intention >= 4 else "kpi-card-red" if intention <= 2.5 else "kpi-card-orange"
        st.markdown(f"""
        <div class="kpi-card {int_class}">
            <div class="kpi-title">勤続意向</div>
            <div class="kpi-value">{intention:.2f}<span class="kpi-unit">/5</span></div>
            <div class="kpi-change">
                <span class="kpi-icon">🏢</span>
                定着意向
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # サブKPI（改良版デザイン）
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card kpi-card-blue">
            <div class="kpi-title">平均年収</div>
            <div class="kpi-value">{kpis['avg_salary']:.0f}<span class="kpi-unit">万円</span></div>
            <div class="kpi-change">
                <span class="kpi-icon">💰</span>
                年収レベル
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        overtime_class = "kpi-card-red" if kpis['avg_overtime'] >= 40 else "kpi-card-green" if kpis['avg_overtime'] <= 20 else "kpi-card-orange"
        st.markdown(f"""
        <div class="kpi-card {overtime_class}">
            <div class="kpi-title">月平均残業時間</div>
            <div class="kpi-value">{kpis['avg_overtime']:.1f}<span class="kpi-unit">h</span></div>
            <div class="kpi-change">
                <span class="kpi-icon">⏰</span>
                労働時間
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        leave_class = "kpi-card-green" if kpis['avg_leave_usage'] >= 80 else "kpi-card-red" if kpis['avg_leave_usage'] <= 50 else "kpi-card-orange"
        st.markdown(f"""
        <div class="kpi-card {leave_class}">
            <div class="kpi-title">有給取得率</div>
            <div class="kpi-value">{kpis['avg_leave_usage']:.1f}<span class="kpi-unit">%</span></div>
            <div class="kpi-change">
                <span class="kpi-icon">🏖️</span>
                休暇利用
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card kpi-card-blue">
            <div class="kpi-title">回答者数</div>
            <div class="kpi-value">{kpis['total_employees']}<span class="kpi-unit">名</span></div>
            <div class="kpi-change">
                <span class="kpi-icon">👥</span>
                全回答者
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_satisfaction_analysis(data, kpis):
    """満足度分析を表示"""
    st.markdown('<div class="section-header"><h2>📈 満足度・期待度分析</h2></div>', unsafe_allow_html=True)
    
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
        if 'gap_by_category' in kpis:
            gap_df = pd.DataFrame({
                'カテゴリ': list(kpis['gap_by_category'].keys()),
                'ギャップ': list(kpis['gap_by_category'].values()),
                '満足度': satisfaction_values,
                '期待度': list(kpis['expectation_by_category'].values())
            })
            
            # ギャップの散布図
            fig = px.scatter(
                gap_df,
                x='満足度',
                y='期待度',
                size=np.abs(gap_df['ギャップ']),
                color='ギャップ',
                hover_name='カテゴリ',
                title="期待度 vs 満足度 ギャップ分析",
                color_continuous_scale='RdYlGn',
                range_x=[1, 5],
                range_y=[1, 5]
            )
            
            # 基準線を追加
            fig.add_shape(type="line", x0=1, y0=1, x1=5, y1=5, 
                         line=dict(color="gray", width=2, dash="dash"))
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # ギャップテーブル
            st.subheader("期待度ギャップ詳細")
            gap_display = gap_df.sort_values('ギャップ').round(2)
            gap_display['判定'] = gap_display['ギャップ'].apply(
                lambda x: '😊 満足度>期待度' if x > 0.2 else '😔 期待度>満足度' if x < -0.2 else '😐 ほぼ同等'
            )
            st.dataframe(gap_display, use_container_width=True)

def show_department_analysis(data, kpis):
    """部署別分析を表示"""
    st.markdown('<div class="section-header"><h2>🏢 部署別・詳細分析</h2></div>', unsafe_allow_html=True)
    
    if 'employee_data' not in data:
        st.error("部署別データが利用できません")
        return
    
    df = data['employee_data']
    
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
            ["📊 KPI概要", "📈 満足度分析", "🏢 詳細分析"],
            index=0
        )
        
        st.divider()
        
        # データ更新ボタン
        if st.button("🔄 データ更新", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.info("💡 Excelファイル更新後は「データ更新」ボタンを押してください")
        
        st.divider()
        
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
        kpis = calculate_kpis(data)
    
    # ページ表示
    if page == "📊 KPI概要":
        show_kpi_overview(data, kpis)
    elif page == "📈 満足度分析":
        show_satisfaction_analysis(data, kpis)
    elif page == "🏢 詳細分析":
        show_department_analysis(data, kpis)

if __name__ == "__main__":
    main()