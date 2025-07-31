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
    """KPI概要を表示（Streamlit標準コンポーネント使用）"""
    st.header("📊 総合KPIダッシュボード")
    
    # データ状況の表示
    df = data['employee_data']
    
    # 情報ボックス
    st.info(f"📅 **データ最終更新:** {datetime.now().strftime('%Y/%m/%d %H:%M')} | 👥 **回答者数:** {len(df)}名 | 📋 **調査項目:** {len(df.columns)}項目")
    
    if not kpis:
        st.error("KPIデータが利用できません")
        return
    
    st.subheader("🎯 主要指標")
    
    # メインKPI（Streamlit標準メトリクス使用）
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        nps_delta = "📈 良好" if kpis['nps'] > 0 else "📉 要改善" if kpis['nps'] < -10 else "⚠️ 普通"
        nps_color = "normal" if kpis['nps'] > 0 else "inverse" if kpis['nps'] < -10 else "off"
        st.metric(
            label="📈 eNPS",
            value=f"{kpis['nps']:.1f}",
            delta=nps_delta,
            delta_color=nps_color
        )
        st.caption("従業員推奨度指標")
    
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
        st.metric(
            label="👥 回答者数",
            value=f"{kpis['total_employees']}名",
            delta="全回答者"
        )
        st.caption("調査参加者")

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
        if 'gap_by_category' in kpis:
            gap_df = pd.DataFrame({
                'カテゴリ': list(kpis['gap_by_category'].keys()),
                'ギャップ': list(kpis['gap_by_category'].values()),
                '満足度': satisfaction_values,
                '期待度': list(kpis['expectation_by_category'].values())
            })
            
            # 4象限プロット（大幅改善版）
            fig = go.Figure()
            
            # 4象限の背景色を追加
            mid_x, mid_y = 3, 3  # 中央値
            
            # 象限の背景色
            fig.add_shape(
                type="rect", x0=1, y0=mid_y, x1=mid_x, y1=5,
                fillcolor="rgba(255, 99, 132, 0.1)", line=dict(width=0),
                name="高期待・低満足"
            )
            fig.add_shape(
                type="rect", x0=mid_x, y0=mid_y, x1=5, y1=5,
                fillcolor="rgba(75, 192, 192, 0.1)", line=dict(width=0),
                name="高期待・高満足"
            )
            fig.add_shape(
                type="rect", x0=1, y0=1, x1=mid_x, y1=mid_y,
                fillcolor="rgba(255, 206, 86, 0.1)", line=dict(width=0),
                name="低期待・低満足"
            )
            fig.add_shape(
                type="rect", x0=mid_x, y0=1, x1=5, y1=mid_y,
                fillcolor="rgba(153, 102, 255, 0.1)", line=dict(width=0),
                name="低期待・高満足"
            )
            
            # 区切り線を追加
            fig.add_hline(y=mid_y, line_dash="dash", line_color="rgba(128, 128, 128, 0.8)", line_width=2)
            fig.add_vline(x=mid_x, line_dash="dash", line_color="rgba(128, 128, 128, 0.8)", line_width=2)
            
            # データポイントを追加
            colors = []
            sizes = []
            symbols = []
            for _, row in gap_df.iterrows():
                x, y = row['満足度'], row['期待度']
                gap = row['ギャップ']
                
                # 象限によって色を決定
                if x >= mid_x and y >= mid_y:
                    colors.append('#48BB78')  # 緑 - 理想的
                    symbols.append('circle')
                elif x < mid_x and y >= mid_y:
                    colors.append('#F56565')  # 赤 - 要改善
                    symbols.append('triangle-up')
                elif x >= mid_x and y < mid_y:
                    colors.append('#9F7AEA')  # 紫 - 満足超過
                    symbols.append('diamond')
                else:
                    colors.append('#ED8936')  # オレンジ - 機会領域
                    symbols.append('square')
                
                sizes.append(max(10, abs(gap) * 20 + 15))
            
            fig.add_trace(go.Scatter(
                x=gap_df['満足度'],
                y=gap_df['期待度'],
                mode='markers+text',
                marker=dict(
                    size=sizes,
                    color=colors,
                    symbol=symbols,
                    line=dict(width=2, color='white'),
                    opacity=0.8
                ),
                text=gap_df['カテゴリ'],
                textposition="top center",
                textfont=dict(size=10, color='black'),
                hovertemplate='<b>%{text}</b><br>' +
                            '満足度: %{x:.1f}<br>' +
                            '期待度: %{y:.1f}<br>' +
                            'ギャップ: %{customdata:.2f}<extra></extra>',
                customdata=gap_df['ギャップ'],
                showlegend=False
            ))
            
            # レイアウト設定
            fig.update_layout(
                title={
                    'text': "期待度 vs 満足度 4象限分析",
                    'x': 0.5,
                    'font': {'size': 18, 'color': '#1f2937'}
                },
                xaxis=dict(
                    title="満足度 →",
                    range=[0.8, 5.2],
                    showgrid=True,
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    dtick=1
                ),
                yaxis=dict(
                    title="↑ 期待度",
                    range=[0.8, 5.2],
                    showgrid=True,
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    dtick=1
                ),
                height=600,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            # 象限ラベルを追加
            annotations = [
                dict(x=4.2, y=4.2, text="<b>🎯 理想的</b><br>(高満足・高期待)", 
                     showarrow=False, font=dict(size=11, color='#22543d'), bgcolor='rgba(72, 187, 120, 0.2)', bordercolor='#48BB78'),
                dict(x=1.8, y=4.2, text="<b>🚨 要改善</b><br>(低満足・高期待)", 
                     showarrow=False, font=dict(size=11, color='#742a2a'), bgcolor='rgba(245, 101, 101, 0.2)', bordercolor='#F56565'),
                dict(x=4.2, y=1.8, text="<b>💎 満足超過</b><br>(高満足・低期待)", 
                     showarrow=False, font=dict(size=11, color='#553c9a'), bgcolor='rgba(159, 122, 234, 0.2)', bordercolor='#9F7AEA'),
                dict(x=1.8, y=1.8, text="<b>🔄 機会領域</b><br>(低満足・低期待)", 
                     showarrow=False, font=dict(size=11, color='#c05621'), bgcolor='rgba(237, 137, 54, 0.2)', bordercolor='#ED8936')
            ]
            
            for ann in annotations:
                fig.add_annotation(**ann)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 象限別の説明
            st.info("""
            **📊 4象限の解釈**
            - 🎯 **理想的（右上）**: 満足度・期待度ともに高い項目。現状維持・さらなる強化
            - 🚨 **要改善（左上）**: 期待は高いが満足度が低い項目。最優先で改善が必要
            - 💎 **満足超過（右下）**: 満足度は高いが期待度が低い項目。アピールや認知向上の機会
            - 🔄 **機会領域（左下）**: 期待・満足ともに低い項目。将来的な改善検討領域
            """)
            
            # ギャップテーブル（改善版）
            st.subheader("📋 象限別分析結果")
            
            # 象限分類を追加
            def classify_quadrant(row):
                x, y = row['満足度'], row['期待度']
                if x >= 3 and y >= 3:
                    return '🎯 理想的'
                elif x < 3 and y >= 3:
                    return '🚨 要改善'
                elif x >= 3 and y < 3:
                    return '💎 満足超過'
                else:
                    return '🔄 機会領域'
            
            gap_display = gap_df.copy()
            gap_display['象限'] = gap_display.apply(classify_quadrant, axis=1)
            gap_display['ギャップ評価'] = gap_display['ギャップ'].apply(
                lambda x: '😊 満足>期待' if x > 0.3 else '😔 期待>満足' if x < -0.3 else '😐 ほぼ同等'
            )
            
            # 優先度を設定
            priority_map = {'🚨 要改善': 1, '🔄 機会領域': 2, '💎 満足超過': 3, '🎯 理想的': 4}
            gap_display['優先度'] = gap_display['象限'].map(priority_map)
            
            # 表示用に整理
            display_df = gap_display[['カテゴリ', '満足度', '期待度', 'ギャップ', '象限', 'ギャップ評価', '優先度']].sort_values('優先度')
            display_df = display_df.round({'満足度': 1, '期待度': 1, 'ギャップ': 2})
            display_df = display_df.drop_duplicates().reset_index(drop=True)
            
            # 優先度カラムを除外して表示
            st.dataframe(
                display_df[['カテゴリ', '満足度', '期待度', 'ギャップ', '象限', 'ギャップ評価']], 
                use_container_width=True,
                hide_index=True
            )

def show_department_analysis(data, kpis):
    """部署別分析を表示"""
    st.header("🏢 部署別・詳細分析")
    
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