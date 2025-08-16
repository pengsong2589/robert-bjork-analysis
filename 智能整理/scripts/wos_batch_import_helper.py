#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web of Science 批量导入助手
功能：从CSV文件中提取论文信息，生成适合WOS检索的格式

创建时间：2025-01-27
作者：AI助手
"""

import pandas as pd
import os
from datetime import datetime

def extract_dois_from_csv(csv_file_path):
    """
    从CSV文件中提取DOI信息
    
    参数：
    csv_file_path: CSV文件路径
    
    返回：
    dict: 包含提取结果的字典
    """
    try:
        # 读取CSV文件
        print(f"正在读取文件: {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        
        print(f"文件共包含 {len(df)} 条记录")
        
        # 提取DOI列
        dois = []
        titles = []
        authors = []
        years = []
        
        for index, row in df.iterrows():
            doi = row.get('DOI', '').strip()
            title = row.get('Title', '').strip()
            author = row.get('Author', '').strip()
            year = row.get('Publication Year', '')
            
            if doi:  # 只处理有DOI的记录
                dois.append(doi)
                titles.append(title)
                authors.append(author)
                years.append(year)
        
        print(f"成功提取 {len(dois)} 个有效DOI")
        
        return {
            'dois': dois,
            'titles': titles,
            'authors': authors,
            'years': years,
            'total_count': len(dois)
        }
        
    except Exception as e:
        print(f"处理文件时出错: {str(e)}")
        return None

def create_wos_search_formats(data):
    """
    创建多种WOS检索格式
    
    参数：
    data: extract_dois_from_csv返回的数据字典
    
    返回：
    dict: 包含各种检索格式的字典
    """
    
    formats = {}
    
    # 方法1: DOI批量检索格式
    # WOS支持用OR连接多个DOI进行检索
    doi_search = ' OR '.join([f'DO="{doi}"' for doi in data['dois']])
    formats['doi_search'] = doi_search
    
    # 方法2: DOI列表（纯文本，每行一个）
    formats['doi_list'] = '\n'.join(data['dois'])
    
    # 方法3: 标题检索格式（备用方案）
    title_search = ' OR '.join([f'TI="{title}"' for title in data['titles'][:10]])  # 限制前10个，避免过长
    formats['title_search'] = title_search
    
    # 方法4: 作者+年份组合检索（用于验证）
    author_year_searches = []
    for i in range(min(5, len(data['authors']))):  # 只取前5个作为示例
        author = data['authors'][i].split(',')[0].strip()  # 取第一作者
        year = data['years'][i]
        if author and year:
            author_year_searches.append(f'AU="{author}" AND PY={year}')
    
    formats['author_year_sample'] = ' OR '.join(author_year_searches)
    
    return formats

def save_search_files(formats, output_dir):
    """
    将检索格式保存到文件
    
    参数：
    formats: 检索格式字典
    output_dir: 输出目录
    """
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存DOI批量检索语句
    with open(os.path.join(output_dir, f'wos_doi_search_{timestamp}.txt'), 'w', encoding='utf-8') as f:
        f.write("=== Web of Science DOI批量检索语句 ===\n")
        f.write("使用方法：复制下面的检索语句到WOS高级检索框中\n\n")
        f.write(formats['doi_search'])
        f.write(f"\n\n总计DOI数量: {len(formats['doi_list'].split())}")
    
    # 保存DOI列表
    with open(os.path.join(output_dir, f'doi_list_{timestamp}.txt'), 'w', encoding='utf-8') as f:
        f.write("=== DOI列表 ===\n")
        f.write("每行一个DOI，可用于其他数据库检索\n\n")
        f.write(formats['doi_list'])
    
    # 保存标题检索语句（备用）
    with open(os.path.join(output_dir, f'wos_title_search_{timestamp}.txt'), 'w', encoding='utf-8') as f:
        f.write("=== Web of Science 标题检索语句（备用方案）===\n")
        f.write("注意：由于长度限制，只包含前10个标题\n\n")
        f.write(formats['title_search'])
    
    # 保存使用说明
    with open(os.path.join(output_dir, f'使用说明_{timestamp}.md'), 'w', encoding='utf-8') as f:
        f.write("""# Web of Science 批量检索使用说明

## 方法一：DOI批量检索（推荐）

1. 打开 Web of Science 网站
2. 选择"高级检索"
3. 复制 `wos_doi_search_*.txt` 文件中的检索语句
4. 粘贴到检索框中，点击检索

**优点：**
- 最准确，直接通过DOI匹配
- 一次性检索所有论文
- 结果最可靠

**注意事项：**
- 检索语句可能很长，确保完整复制
- 如果检索失败，可能是语句太长，建议分批检索

## 方法二：分批DOI检索

如果检索语句太长，可以将DOI列表分成几批：

1. 每批5-10个DOI
2. 格式：`DO="DOI1" OR DO="DOI2" OR DO="DOI3"`
3. 分别检索后合并结果

## 方法三：标题检索（备用）

如果DOI检索有问题，可以使用标题检索：
- 复制 `wos_title_search_*.txt` 中的语句
- 注意只包含部分论文，需要分批处理

## 导出设置建议

检索到结果后，导出时建议选择：
- 记录内容：完整记录
- 文件格式：Tab分隔或Excel
- 包含：引用信息、摘要、关键词等

## 后续处理

导出的WOS数据可以用于：
- 引文分析
- 影响因子查询
- 学科分类信息
- 期刊信息完善
""")
    
    print(f"检索文件已保存到: {output_dir}")
    print("文件列表:")
    for file in os.listdir(output_dir):
        if timestamp in file:
            print(f"  - {file}")

def main():
    """主函数"""
    print("=== Web of Science 批量导入助手 ===\n")
    
    # 设置文件路径
    csv_file = "data/raw/202507271930_Hinton_Papers_30_v2.csv"
    output_dir = "data/processed/wos_import"
    
    # 检查CSV文件是否存在
    if not os.path.exists(csv_file):
        print("错误：CSV文件不存在，请检查路径")
        print(f"期望路径: {csv_file}")
        return
    
    # 提取DOI信息
    print("步骤1: 提取DOI信息...")
    data = extract_dois_from_csv(csv_file)
    
    if not data:
        print("提取DOI失败，程序结束")
        return
    
    # 显示统计信息
    print(f"\n统计信息:")
    print(f"- 总记录数: {data['total_count']}")
    print(f"- 年份范围: {min(data['years'])} - {max(data['years'])}")
    print(f"- 样例DOI: {data['dois'][0]}")
    
    # 创建检索格式
    print("\n步骤2: 生成检索格式...")
    formats = create_wos_search_formats(data)
    
    # 显示DOI检索语句长度
    doi_search_length = len(formats['doi_search'])
    print(f"DOI检索语句长度: {doi_search_length} 字符")
    
    if doi_search_length > 2000:
        print("⚠️  警告：检索语句较长，建议分批检索")
    
    # 保存文件
    print("\n步骤3: 保存检索文件...")
    save_search_files(formats, output_dir)
    
    print("\n✅ 处理完成！")
    print("\n下一步操作：")
    print("1. 查看生成的检索文件")
    print("2. 复制DOI检索语句到Web of Science")
    print("3. 执行检索并导出结果")

if __name__ == "__main__":
    main() 