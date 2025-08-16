#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
识别未匹配的论文条目并获取PDF路径
"""

import pandas as pd
import os
from pathlib import Path

def main():
    """识别未匹配的条目"""
    excel_file = "data/processed/Hinton_with_Affiliations_v3.xlsx"
    
    try:
        # 读取Excel文件
        df = pd.read_excel(excel_file)
        print(f"📊 总条目数: {len(df)}")
        
        # 找出未匹配的条目（论文主题为空）
        unmatched = df[df['论文主题'].isna() | (df['论文主题'] == '')]
        print(f"❌ 未匹配条目数: {len(unmatched)}")
        
        print("\n📋 未匹配的条目详情:")
        print("=" * 80)
        
        unmatched_info = []
        
        for idx, row in unmatched.iterrows():
            title = str(row.get('标题', 'N/A'))
            doi = str(row.get('DOI', 'N/A'))
            year = str(row.get('发表年份', 'N/A'))
            pdf_path = str(row.get('PDF文件绝对路径', 'N/A'))
            
            print(f"\n{idx + 1}. 标题: {title}")
            print(f"   DOI: {doi}")
            print(f"   年份: {year}")
            print(f"   PDF路径: {pdf_path}")
            
            # 检查PDF文件是否存在
            if pdf_path != 'N/A' and pdf_path != 'nan':
                if os.path.exists(pdf_path):
                    print(f"   📄 PDF文件: ✅ 存在")
                    unmatched_info.append({
                        'index': idx + 1,
                        'title': title,
                        'doi': doi,
                        'year': year,
                        'pdf_path': pdf_path,
                        'exists': True
                    })
                else:
                    print(f"   📄 PDF文件: ❌ 不存在")
                    unmatched_info.append({
                        'index': idx + 1,
                        'title': title,
                        'doi': doi,
                        'year': year,
                        'pdf_path': pdf_path,
                        'exists': False
                    })
            else:
                print(f"   📄 PDF文件: ⚠️ 路径为空")
                unmatched_info.append({
                    'index': idx + 1,
                    'title': title,
                    'doi': doi,
                    'year': year,
                    'pdf_path': 'N/A',
                    'exists': False
                })
        
        # 保存未匹配信息到文件
        output_file = "data/processed/unmatched_papers_info.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("未匹配论文条目信息\n")
            f.write("=" * 50 + "\n\n")
            
            for info in unmatched_info:
                f.write(f"条目 {info['index']}:\n")
                f.write(f"标题: {info['title']}\n")
                f.write(f"DOI: {info['doi']}\n")
                f.write(f"年份: {info['year']}\n")
                f.write(f"PDF路径: {info['pdf_path']}\n")
                f.write(f"文件存在: {'是' if info['exists'] else '否'}\n")
                f.write("-" * 50 + "\n\n")
        
        print(f"\n💾 未匹配信息已保存到: {output_file}")
        
        # 统计可用PDF数量
        available_pdfs = sum(1 for info in unmatched_info if info['exists'])
        print(f"\n📊 统计信息:")
        print(f"   可用PDF文件: {available_pdfs}/{len(unmatched_info)}")
        
        return unmatched_info
        
    except Exception as e:
        print(f"❌ 处理过程中出错: {e}")
        return []

if __name__ == "__main__":
    main() 