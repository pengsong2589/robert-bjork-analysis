#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOI分批检索脚本
将30个DOI分成多个小批次，便于在Web of Science中分别检索

创建时间：2025-01-27
作者：AI助手
"""

import pandas as pd
import os
from datetime import datetime

def create_batch_searches():
    """创建分批检索语句"""
    
    # 读取原始CSV文件
    csv_file = "data/raw/202507271930_Hinton_Papers_30_v2.csv"
    df = pd.read_csv(csv_file)
    
    # 提取所有DOI
    dois = []
    for index, row in df.iterrows():
        doi = row.get('DOI', '').strip()
        if doi:
            dois.append(doi)
    
    # 分批设置：每批5个DOI
    batch_size = 5
    total_dois = len(dois)
    num_batches = (total_dois + batch_size - 1) // batch_size  # 向上取整
    
    output_dir = "data/processed/wos_import/batch_searches"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"总共 {total_dois} 个DOI，将分成 {num_batches} 批")
    
    # 生成每批检索语句
    batch_info = []
    
    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, total_dois)
        batch_dois = dois[start_idx:end_idx]
        
        # 创建检索语句
        search_query = ' OR '.join([f'DO="{doi}"' for doi in batch_dois])
        
        # 保存到文件
        batch_filename = f"batch_{i+1:02d}_search_{timestamp}.txt"
        with open(os.path.join(output_dir, batch_filename), 'w', encoding='utf-8') as f:
            f.write(f"=== 第 {i+1} 批 DOI 检索语句 ===\n")
            f.write(f"包含 {len(batch_dois)} 个DOI (序号 {start_idx+1}-{end_idx})\n\n")
            f.write("复制下面的语句到Web of Science高级检索：\n\n")
            f.write(search_query)
            f.write(f"\n\n包含的DOI:\n")
            for j, doi in enumerate(batch_dois, 1):
                f.write(f"{j}. {doi}\n")
        
        batch_info.append({
            'batch': i+1,
            'filename': batch_filename,
            'doi_count': len(batch_dois),
            'start_idx': start_idx+1,
            'end_idx': end_idx
        })
        
        print(f"批次 {i+1}: {len(batch_dois)} 个DOI -> {batch_filename}")
    
    # 创建总览文件
    summary_file = os.path.join(output_dir, f"batch_summary_{timestamp}.md")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# DOI分批检索总览\n\n")
        f.write(f"**总DOI数量**: {total_dois}\n")
        f.write(f"**批次数量**: {num_batches}\n")
        f.write(f"**每批大小**: 最多{batch_size}个DOI\n\n")
        
        f.write("## 使用步骤\n\n")
        f.write("1. 按顺序使用每个批次的检索语句\n")
        f.write("2. 在Web of Science中逐一检索\n")
        f.write("3. 将所有结果导出并合并\n\n")
        
        f.write("## 批次详情\n\n")
        f.write("| 批次 | 文件名 | DOI数量 | 序号范围 |\n")
        f.write("|------|--------|---------|----------|\n")
        
        for info in batch_info:
            f.write(f"| {info['batch']} | {info['filename']} | {info['doi_count']} | {info['start_idx']}-{info['end_idx']} |\n")
        
        f.write("\n## 注意事项\n\n")
        f.write("- 建议按批次顺序检索，避免遗漏\n")
        f.write("- 每次检索后建议导出结果，最后合并\n")
        f.write("- 如果某批次检索结果为空，检查DOI格式是否正确\n")
    
    print(f"\n✅ 分批检索文件已生成在: {output_dir}")
    print(f"📋 总览文件: batch_summary_{timestamp}.md")
    
    return output_dir

if __name__ == "__main__":
    create_batch_searches() 