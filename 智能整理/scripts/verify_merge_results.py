#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关键词合并结果验证脚本
功能：检查和展示WOS关键词合并的效果
作者：AI助手
日期：2025-01-27
"""

import pandas as pd
import os

def verify_merge_results():
    """验证合并结果"""
    
    # 文件路径
    v4_file = "/Users/tommy/Projects/projects/AI学术分析/智能整理/data/processed/Hinton_with_Affiliations_v4.xlsx"
    v5_file = "/Users/tommy/Projects/projects/AI学术分析/智能整理/data/processed/Hinton_with_Affiliations_v5.xlsx"
    report_file = "/Users/tommy/Projects/projects/AI学术分析/智能整理/data/processed/Hinton_with_Affiliations_v5_match_report.xlsx"
    
    print("=" * 60)
    print("📊 WOS关键词合并结果验证报告")
    print("=" * 60)
    
    # 读取文件
    try:
        df_v4 = pd.read_excel(v4_file)
        df_v5 = pd.read_excel(v5_file)
        df_report = pd.read_excel(report_file)
        
        print(f"\n✅ 成功读取所有文件")
        print(f"   - 原始文件 (v4): {len(df_v4)} 行, {len(df_v4.columns)} 列")
        print(f"   - 合并文件 (v5): {len(df_v5)} 行, {len(df_v5.columns)} 列")
        print(f"   - 匹配报告: {len(df_report)} 行")
        
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return
    
    # 检查新增列
    print(f"\n📋 新增列检查:")
    new_columns = ['author_keywords_wos', 'keywords_plus_wos']
    
    for col in new_columns:
        if col in df_v5.columns:
            print(f"   ✅ {col} - 已成功添加")
            non_empty_count = df_v5[col].notna().sum() - (df_v5[col] == "").sum()
            total_count = len(df_v5)
            print(f"      └─ 有数据记录: {non_empty_count}/{total_count} ({non_empty_count/total_count*100:.1f}%)")
        else:
            print(f"   ❌ {col} - 未找到")
    
    # 显示匹配统计
    print(f"\n📈 匹配统计:")
    match_types = df_report['match_type'].value_counts()
    total_matches = len(df_report)
    
    for match_type, count in match_types.items():
        percentage = (count / total_matches) * 100
        print(f"   • {match_type}: {count} 条 ({percentage:.1f}%)")
    
    # 显示合并示例
    print(f"\n📝 合并数据示例:")
    print("─" * 60)
    
    # 找几个有关键词数据的示例
    examples = df_v5[
        (df_v5['author_keywords_wos'].notna()) & 
        (df_v5['author_keywords_wos'] != "")
    ].head(3)
    
    for idx, row in examples.iterrows():
        print(f"\n【示例 {idx+1}】")
        print(f"标题: {row['标题'][:60]}...")
        print(f"DOI: {row.get('DOI', 'N/A')}")
        
        author_kw = row['author_keywords_wos']
        keywords_plus = row['keywords_plus_wos']
        
        if pd.notna(author_kw) and author_kw != "":
            print(f"作者关键词: {author_kw}")
        else:
            print(f"作者关键词: 无")
            
        if pd.notna(keywords_plus) and keywords_plus != "":
            print(f"关键词Plus: {keywords_plus}")
        else:
            print(f"关键词Plus: 无")
        print("─" * 40)
    
    # 显示无匹配的记录示例
    print(f"\n❌ 未匹配记录示例:")
    print("─" * 60)
    
    no_match_records = df_v5[
        (df_v5['author_keywords_wos'].isna()) | 
        (df_v5['author_keywords_wos'] == "")
    ].head(2)
    
    for idx, row in no_match_records.iterrows():
        print(f"\n【未匹配 {idx+1}】")
        print(f"标题: {row['标题'][:60]}...")
        print(f"DOI: {row.get('DOI', 'N/A')}")
        print(f"原因: 在WOS文件中未找到对应记录")
        print("─" * 40)
    
    # 文件大小对比
    print(f"\n📁 文件大小对比:")
    if os.path.exists(v4_file) and os.path.exists(v5_file):
        size_v4 = os.path.getsize(v4_file)
        size_v5 = os.path.getsize(v5_file)
        print(f"   - v4文件: {size_v4:,} 字节")
        print(f"   - v5文件: {size_v5:,} 字节")
        print(f"   - 增长: {size_v5-size_v4:,} 字节 ({(size_v5-size_v4)/size_v4*100:.1f}%)")
    
    print(f"\n✅ 验证完成!")
    print(f"💡 建议: 可以打开 {v5_file} 查看完整的合并结果")
    print("=" * 60)

def main():
    """主函数"""
    verify_merge_results()

if __name__ == "__main__":
    main() 