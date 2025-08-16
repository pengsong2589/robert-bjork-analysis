#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOI格式修正脚本
将CSV中的下划线格式DOI转换为标准斜杠格式，用于Web of Science检索

创建时间：2025-01-27
作者：AI助手
"""

import pandas as pd
import os
from datetime import datetime

def fix_doi_format():
    """修正DOI格式并生成正确的检索语句"""
    
    # 读取原始CSV文件
    csv_file = "data/raw/202507271930_Hinton_Papers_30_v2.csv"
    df = pd.read_csv(csv_file)
    
    print("=== DOI格式修正工具 ===\n")
    print("检测到的问题：CSV中的DOI使用了下划线格式，需要转换为标准格式")
    print("例如：10.1038_306021a0 → 10.1038/306021a0\n")
    
    # 提取并修正DOI
    original_dois = []
    fixed_dois = []
    titles = []
    
    for index, row in df.iterrows():
        original_doi = row.get('DOI', '').strip()
        title = row.get('Title', '').strip()
        
        if original_doi:
            # 将下划线替换为斜杠
            fixed_doi = original_doi.replace('_', '/')
            original_dois.append(original_doi)
            fixed_dois.append(fixed_doi)
            titles.append(title)
    
    print(f"处理了 {len(fixed_dois)} 个DOI")
    print("修正示例：")
    for i in range(min(3, len(original_dois))):
        print(f"  原格式: {original_dois[i]}")
        print(f"  新格式: {fixed_dois[i]}")
        print()
    
    # 生成修正后的检索语句
    formats = {}
    
    # 方法1: 标准DOI格式检索
    doi_search_fixed = ' OR '.join([f'DO="{doi}"' for doi in fixed_dois])
    formats['doi_search_fixed'] = doi_search_fixed
    
    # 方法2: 尝试不同的字段标识符
    doi_search_alt1 = ' OR '.join([f'DI="{doi}"' for doi in fixed_dois])  # 有些数据库用DI
    formats['doi_search_alt1'] = doi_search_alt1
    
    # 方法3: 简化格式（去掉引号）
    doi_search_simple = ' OR '.join([f'DO={doi}' for doi in fixed_dois])
    formats['doi_search_simple'] = doi_search_simple
    
    # 方法4: 标题检索作为备用
    title_search = ' OR '.join([f'TI="{title}"' for title in titles[:10]])  # 限制10个标题
    formats['title_search'] = title_search
    
    # 保存修正后的文件
    output_dir = "data/processed/wos_import/fixed_format"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存修正后的DOI检索语句
    with open(os.path.join(output_dir, f'wos_fixed_doi_search_{timestamp}.txt'), 'w', encoding='utf-8') as f:
        f.write("=== Web of Science 修正后的DOI检索语句 ===\n")
        f.write("问题：原DOI格式使用下划线，已修正为斜杠格式\n\n")
        f.write("方法1 - 标准格式（推荐尝试）：\n")
        f.write(formats['doi_search_fixed'])
        f.write("\n\n" + "="*50 + "\n\n")
        f.write("方法2 - 备用字段标识符：\n")
        f.write(formats['doi_search_alt1'])
        f.write("\n\n" + "="*50 + "\n\n")
        f.write("方法3 - 简化格式（无引号）：\n")
        f.write(formats['doi_search_simple'])
    
    # 保存修正后的DOI列表
    with open(os.path.join(output_dir, f'fixed_doi_list_{timestamp}.txt'), 'w', encoding='utf-8') as f:
        f.write("=== 修正后的DOI列表 ===\n")
        f.write("格式已从下划线改为标准斜杠格式\n\n")
        for i, (original, fixed) in enumerate(zip(original_dois, fixed_dois), 1):
            f.write(f"{i:2d}. {original} → {fixed}\n")
    
    # 创建分批检索（修正版）
    batch_size = 5
    num_batches = (len(fixed_dois) + batch_size - 1) // batch_size
    
    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(fixed_dois))
        batch_dois = fixed_dois[start_idx:end_idx]
        
        search_query = ' OR '.join([f'DO="{doi}"' for doi in batch_dois])
        
        with open(os.path.join(output_dir, f'batch_{i+1:02d}_fixed_{timestamp}.txt'), 'w', encoding='utf-8') as f:
            f.write(f"=== 第 {i+1} 批修正后的DOI检索 ===\n")
            f.write(f"包含 {len(batch_dois)} 个DOI (序号 {start_idx+1}-{end_idx})\n\n")
            f.write("Web of Science检索语句：\n\n")
            f.write(search_query)
            f.write(f"\n\n修正后的DOI列表:\n")
            for j, doi in enumerate(batch_dois, 1):
                f.write(f"{j}. {doi}\n")
    
    # 创建故障排除指南
    with open(os.path.join(output_dir, f'故障排除指南_{timestamp}.md'), 'w', encoding='utf-8') as f:
        f.write("""# Web of Science 检索故障排除指南

## 🔍 问题诊断

**主要问题**：DOI格式不匹配
- 原始格式：`10.1038_306021a0`（使用下划线）
- 正确格式：`10.1038/306021a0`（使用斜杠）

## 🛠️ 解决方案

### 方案1：使用修正后的DOI格式（推荐）
复制以下检索语句到Web of Science：
```
""" + formats['doi_search_fixed'][:200] + "...\n```\n")
        
        f.write("""
### 方案2：分批检索
如果一次性检索仍然失败，使用分批文件：
- batch_01_fixed_*.txt（第1-5个论文）
- batch_02_fixed_*.txt（第6-10个论文）
- 依此类推...

### 方案3：单个DOI测试
先测试单个DOI是否能检索到：
1. 使用：`DO="10.1038/323533a0"`（Hinton经典反向传播论文）
2. 如果成功，说明格式正确，可以继续批量检索
3. 如果失败，可能需要尝试其他字段标识符

### 方案4：替代字段标识符
如果 DO= 不工作，尝试：
- `DI="DOI号码"`
- `DOI="DOI号码"`
- `DO=DOI号码`（无引号）

### 方案5：标题检索备用
使用论文标题进行检索（部分论文）：
""" + formats['title_search'][:200] + "...\n")
        
        f.write("""
## ❗ 常见问题

1. **数据库访问权限**：确保您的机构有Web of Science访问权限
2. **DOI收录情况**：某些较老的论文可能未收录DOI信息
3. **检索语句长度**：过长的语句可能被截断，建议分批检索
4. **特殊字符**：确保复制时没有多余的空格或换行符

## 📞 如需帮助

如果问题仍然存在：
1. 尝试联系图书馆技术支持
2. 使用Web of Science的帮助文档
3. 考虑使用其他学术数据库作为补充
""")
    
    print(f"\n✅ 修正后的检索文件已生成：{output_dir}")
    print(f"📁 生成了 {num_batches} 个分批检索文件")
    print(f"📋 包含详细的故障排除指南")
    
    # 显示第一个修正后的检索语句
    print(f"\n🔧 修正后的检索语句（前100字符）：")
    print(f"{formats['doi_search_fixed'][:100]}...")
    
    return formats

if __name__ == "__main__":
    fix_doi_format() 