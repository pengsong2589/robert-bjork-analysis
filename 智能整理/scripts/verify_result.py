#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证结果脚本 - 查看生成的Excel文件内容
"""

import pandas as pd
import os

def main():
    file_path = "data/processed/Hinton_with_Affiliations_v3.xlsx"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        print(f"📊 文件信息:")
        print(f"   总行数: {len(df)}")
        print(f"   总列数: {len(df.columns)}")
        print(f"   列名: {list(df.columns)}")
        
        # 检查论文主题列
        if '论文主题' in df.columns:
            print(f"\n✅ '论文主题'列已成功添加!")
            topics_filled = df['论文主题'].notna() & (df['论文主题'] != '')
            print(f"   已填充主题的条目数: {topics_filled.sum()}")
            print(f"   未填充主题的条目数: {len(df) - topics_filled.sum()}")
            
            # 显示前几个有主题的条目
            print(f"\n📝 前5个有主题信息的条目:")
            filled_rows = df[topics_filled].head(5)
            for idx, row in filled_rows.iterrows():
                title = str(row.get('标题', 'N/A'))[:50] + "..." if len(str(row.get('标题', ''))) > 50 else str(row.get('标题', 'N/A'))
                topics = str(row['论文主题'])[:100] + "..." if len(str(row['论文主题'])) > 100 else str(row['论文主题'])
                print(f"   {idx+1}. {title}")
                print(f"      主题: {topics}")
                print()
        else:
            print("❌ 未找到'论文主题'列")
        
        # 检查PDF链接是否保留
        pdf_columns = [col for col in df.columns if 'PDF' in col or 'pdf' in col or '链接' in col]
        if pdf_columns:
            print(f"✅ PDF相关列已保留: {pdf_columns}")
        else:
            print("⚠️  未找到PDF相关列")
            
    except Exception as e:
        print(f"❌ 读取文件时出错: {e}")

if __name__ == "__main__":
    main() 