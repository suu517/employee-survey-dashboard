#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データ構造確認用スクリプト
"""

import pandas as pd
import os

def check_excel_data():
    """Excelファイルの構造を確認"""
    excel_path = './data.xlsx'
    
    if not os.path.exists(excel_path):
        print(f"❌ ファイルが見つかりません: {excel_path}")
        return
    
    try:
        # Excelファイルの全シートを確認
        excel_file = pd.ExcelFile(excel_path)
        print(f"✅ Excelファイルを読み込みました: {excel_path}")
        print(f"📊 シート数: {len(excel_file.sheet_names)}")
        print(f"📋 シート名: {excel_file.sheet_names}")
        
        for sheet_name in excel_file.sheet_names:
            print(f"\n=== シート: {sheet_name} ===")
            try:
                # まず最初の数行を確認
                print("\n--- 最初の5行を確認 ---")
                df_preview = pd.read_excel(excel_path, sheet_name=sheet_name, nrows=5)
                print(df_preview)
                
                # ヘッダーが1行目にない可能性があるので、複数のheader位置を試す
                for header_row in [0, 1, 2]:
                    try:
                        print(f"\n--- header={header_row}で読み込み ---")
                        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header_row)
                        print(f"データ形状: {df.shape}")
                        print(f"列数: {len(df.columns)}")
                        
                        # 最初の数列だけ表示
                        print("\n最初の10列の列名:")
                        for i, col in enumerate(df.columns[:10], 1):
                            print(f"{i:2d}. {col}")
                        
                        if len(df.columns) > 10:
                            print(f"... その他 {len(df.columns) - 10} 列")
                        
                        # 推奨度関連の列を検索
                        print("\n🔍 推奨度関連の列:")
                        recommendation_cols = []
                        for col in df.columns:
                            col_str = str(col).lower()
                            if any(keyword in col_str for keyword in ['推奨', '親しい友人', '家族', '転職', '就職', 'recommend', 'nps']):
                                recommendation_cols.append(col)
                                print(f"  ✓ {col}")
                        
                        # 満足度関連の列を検索
                        print("\n🔍 満足度関連の列:")
                        satisfaction_cols = []
                        for col in df.columns:
                            col_str = str(col).lower()
                            if any(keyword in col_str for keyword in ['満足', '評価', '度合い']):
                                satisfaction_cols.append(col)
                                print(f"  ✓ {col}")
                        
                        if len(satisfaction_cols) > 10:
                            print(f"  ... その他 {len(satisfaction_cols) - 10} 列")
                        
                        # 有効な列が見つかった場合は詳細情報を表示
                        if recommendation_cols:
                            print(f"\n📊 推奨度関連データのサンプル:")
                            for col in recommendation_cols[:2]:  # 最初の2列のサンプル
                                print(f"\n--- {col} ---")
                                print(df[col].value_counts().head())
                                print(f"データ型: {df[col].dtype}")
                                print(f"欠損値: {df[col].isnull().sum()}")
                        
                        if recommendation_cols or satisfaction_cols:
                            print(f"\n✅ header={header_row}で有効なデータが見つかりました")
                            break
                            
                    except Exception as e:
                        print(f"  ❌ header={header_row}でエラー: {e}")
                        continue
                
            except Exception as e:
                print(f"❌ シート {sheet_name} の読み込みエラー: {e}")
        
    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")

if __name__ == "__main__":
    check_excel_data()