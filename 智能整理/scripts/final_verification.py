#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证：检查所有论文主题是否完整
"""

import pandas as pd
import os

def main():
    """验证最终结果"""
    v3_file = "data/processed/Hinton_with_Affiliations_v3.xlsx"
    v4_file = "data/processed/Hinton_with_Affiliations_v4.xlsx"
    
    print("🔍 最终验证报告")
    print("=" * 80)
    
    # 检查v4文件是否存在
    if not os.path.exists(v4_file):
        print(f"❌ v4文件不存在: {v4_file}")
        return
    
    try:
        # 读取最新文件
        df = pd.read_excel(v4_file)
        
        print(f"📊 总条目数: {len(df)}")
        print(f"📋 文件列名: {list(df.columns)}")
        
        # 检查论文主题列的完整性
        if '论文主题' in df.columns:
            # 统计主题完整性
            total_count = len(df)
            filled_count = df['论文主题'].notna().sum()
            empty_count = df['论文主题'].isna().sum()
            
            print(f"\n✅ '论文主题'列存在")
            print(f"   总条目: {total_count}")
            print(f"   已填充: {filled_count}")
            print(f"   未填充: {empty_count}")
            print(f"   完成率: {filled_count/total_count*100:.1f}%")
            
            if empty_count == 0:
                print(f"🎉 恭喜！所有{total_count}个条目的主题都已填充完成！")
            else:
                print(f"⚠️  还有{empty_count}个条目未填充主题")
                
                # 显示未填充的条目
                empty_items = df[df['论文主题'].isna()]
                print("\n未填充的条目:")
                for idx, row in empty_items.iterrows():
                    title = str(row.get('标题', 'N/A'))[:60]
                    print(f"   {idx+1}. {title}...")
            
            # 显示主题统计
            print(f"\n📈 主题分类统计:")
            topics_flat = []
            for topics in df['论文主题'].dropna():
                if pd.notna(topics) and topics:
                    topics_list = [t.strip() for t in str(topics).split(';') if t.strip()]
                    topics_flat.extend(topics_list)
            
            if topics_flat:
                from collections import Counter
                topic_counts = Counter(topics_flat)
                
                print("   热门主题 (出现频次):")
                for topic, count in topic_counts.most_common(10):
                    print(f"     {topic}: {count}")
            
            # 显示所有条目及其主题
            print(f"\n📋 完整论文主题列表:")
            print("-" * 80)
            
            for idx, row in df.iterrows():
                title = str(row.get('标题', 'N/A'))
                topics = str(row.get('论文主题', 'N/A'))
                year = str(row.get('发表年份', 'N/A'))
                
                # 截断过长的标题
                title_display = title[:55] + "..." if len(title) > 55 else title
                topics_display = topics[:60] + "..." if len(topics) > 60 else topics
                
                print(f"{idx+1:2d}. [{year}] {title_display}")
                print(f"    🏷️  {topics_display}")
                print()
            
        else:
            print("❌ '论文主题'列不存在")
            
        # 比较v3和v4的差异
        if os.path.exists(v3_file):
            df_v3 = pd.read_excel(v3_file)
            v3_filled = df_v3['论文主题'].notna().sum()
            v4_filled = df['论文主题'].notna().sum()
            
            print(f"\n📊 版本对比:")
            print(f"   v3版本已填充: {v3_filled}")
            print(f"   v4版本已填充: {v4_filled}")
            print(f"   新增填充: {v4_filled - v3_filled}")
            
    except Exception as e:
        print(f"❌ 验证过程中出错: {e}")

if __name__ == "__main__":
    main() 