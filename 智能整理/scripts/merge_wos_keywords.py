#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WOS关键词数据合并脚本
功能：将WOS文件中的Author Keywords和Keywords Plus列合并到现有Excel文件中
匹配规则：优先DOI精确匹配，其次标题模糊匹配
作者：AI助手
日期：2025-01-27
"""

import pandas as pd
import os
import shutil
from datetime import datetime
from fuzzywuzzy import fuzz
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keyword_merge_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def create_backup(file_path):
    """
    创建文件备份
    Args:
        file_path (str): 要备份的文件路径
    Returns:
        str: 备份文件路径
    """
    if not os.path.exists(file_path):
        logging.error(f"源文件不存在: {file_path}")
        return None
    
    # 创建备份目录
    backup_dir = "/Users/tommy/Projects/projects/AI学术分析/智能整理/data/backup"
    os.makedirs(backup_dir, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = os.path.basename(file_path)
    backup_path = os.path.join(backup_dir, f"backup_{timestamp}_{file_name}")
    
    # 执行备份
    shutil.copy2(file_path, backup_path)
    logging.info(f"备份创建成功: {backup_path}")
    return backup_path

def read_wos_file(wos_file_path):
    """
    读取WOS Excel文件
    Args:
        wos_file_path (str): WOS文件路径
    Returns:
        pandas.DataFrame: WOS数据
    """
    try:
        # 尝试不同的引擎读取Excel文件
        try:
            df = pd.read_excel(wos_file_path, engine='openpyxl')
        except:
            df = pd.read_excel(wos_file_path, engine='xlrd')
        
        logging.info(f"成功读取WOS文件: {wos_file_path}")
        logging.info(f"WOS文件包含 {len(df)} 行数据")
        logging.info(f"WOS文件列名: {list(df.columns)}")
        
        return df
    except Exception as e:
        logging.error(f"读取WOS文件失败: {e}")
        return None

def read_target_file(target_file_path):
    """
    读取目标Excel文件
    Args:
        target_file_path (str): 目标文件路径
    Returns:
        pandas.DataFrame: 目标数据
    """
    try:
        df = pd.read_excel(target_file_path, engine='openpyxl')
        logging.info(f"成功读取目标文件: {target_file_path}")
        logging.info(f"目标文件包含 {len(df)} 行数据")
        logging.info(f"目标文件列名: {list(df.columns)}")
        
        return df
    except Exception as e:
        logging.error(f"读取目标文件失败: {e}")
        return None

def normalize_doi(doi):
    """
    标准化DOI格式
    Args:
        doi (str): 原始DOI
    Returns:
        str: 标准化后的DOI
    """
    if pd.isna(doi) or doi == "":
        return None
    
    doi = str(doi).strip().lower()
    # 移除常见的DOI前缀
    prefixes = ['doi:', 'http://dx.doi.org/', 'https://dx.doi.org/', 
                'http://doi.org/', 'https://doi.org/']
    for prefix in prefixes:
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    
    return doi

def calculate_title_similarity(title1, title2):
    """
    计算标题相似度
    Args:
        title1 (str): 标题1
        title2 (str): 标题2
    Returns:
        int: 相似度分数 (0-100)
    """
    if pd.isna(title1) or pd.isna(title2):
        return 0
    
    title1 = str(title1).strip().lower()
    title2 = str(title2).strip().lower()
    
    return fuzz.ratio(title1, title2)

def find_matching_record(target_row, wos_df, doi_col_wos, title_col_wos, doi_col_target, title_col_target):
    """
    为目标记录查找匹配的WOS记录
    Args:
        target_row: 目标数据行
        wos_df: WOS数据框
        doi_col_wos: WOS中的DOI列名
        title_col_wos: WOS中的标题列名
        doi_col_target: 目标文件中的DOI列名
        title_col_target: 目标文件中的标题列名
    Returns:
        tuple: (匹配的行索引, 匹配类型)
    """
    target_doi = normalize_doi(target_row.get(doi_col_target))
    target_title = target_row.get(title_col_target)
    
    # 首先尝试DOI精确匹配
    if target_doi:
        for idx, wos_row in wos_df.iterrows():
            wos_doi = normalize_doi(wos_row.get(doi_col_wos))
            if wos_doi and target_doi == wos_doi:
                return idx, "DOI_EXACT"
    
    # DOI匹配失败，尝试标题模糊匹配
    if target_title:
        best_match_idx = None
        best_similarity = 0
        similarity_threshold = 85  # 相似度阈值
        
        for idx, wos_row in wos_df.iterrows():
            wos_title = wos_row.get(title_col_wos)
            similarity = calculate_title_similarity(target_title, wos_title)
            
            if similarity > best_similarity and similarity >= similarity_threshold:
                best_similarity = similarity
                best_match_idx = idx
        
        if best_match_idx is not None:
            return best_match_idx, f"TITLE_FUZZY_{best_similarity}"
    
    return None, "NO_MATCH"

def merge_keywords_data(wos_file_path, target_file_path, output_file_path):
    """
    合并关键词数据的主函数
    Args:
        wos_file_path (str): WOS文件路径
        target_file_path (str): 目标文件路径
        output_file_path (str): 输出文件路径
    Returns:
        bool: 操作是否成功
    """
    # 创建备份
    logging.info("开始创建备份...")
    backup_path = create_backup(target_file_path)
    if not backup_path:
        return False
    
    # 读取文件
    logging.info("读取WOS文件...")
    wos_df = read_wos_file(wos_file_path)
    if wos_df is None:
        return False
    
    logging.info("读取目标文件...")
    target_df = read_target_file(target_file_path)
    if target_df is None:
        return False
    
    # 显示可用列名，帮助用户确认
    print("\n=== WOS文件列名 ===")
    for i, col in enumerate(wos_df.columns):
        print(f"{i+1:2d}. {col}")
    
    print("\n=== 目标文件列名 ===")
    for i, col in enumerate(target_df.columns):
        print(f"{i+1:2d}. {col}")
    
    # 自动检测关键列名
    author_keywords_col = None
    keywords_plus_col = None
    doi_col_wos = None
    title_col_wos = None
    doi_col_target = None
    title_col_target = None
    
    # 在WOS文件中查找关键词列
    for col in wos_df.columns:
        col_lower = col.lower()
        if 'author keywords' == col_lower:
            author_keywords_col = col
        elif 'keywords plus' == col_lower:
            keywords_plus_col = col
        elif col_lower == 'doi':
            doi_col_wos = col
        elif 'article title' == col_lower:
            title_col_wos = col
    
    # 在目标文件中查找DOI和标题列
    for col in target_df.columns:
        if col in ['DOI', '标准化DOI']:
            doi_col_target = col
        elif col in ['标题', 'Title']:
            title_col_target = col
    
    logging.info(f"检测到的列名映射:")
    logging.info(f"  WOS Author Keywords: {author_keywords_col}")
    logging.info(f"  WOS Keywords Plus: {keywords_plus_col}")
    logging.info(f"  WOS DOI: {doi_col_wos}")
    logging.info(f"  WOS Title: {title_col_wos}")
    logging.info(f"  目标DOI: {doi_col_target}")
    logging.info(f"  目标Title: {title_col_target}")
    
    if not all([author_keywords_col, keywords_plus_col, doi_col_target, title_col_target]):
        logging.error("未能检测到所有必需的列，请检查文件格式")
        return False
    
    # 初始化新列
    target_df['author_keywords_wos'] = ""
    target_df['keywords_plus_wos'] = ""
    
    # 记录匹配统计
    match_stats = {
        'DOI_EXACT': 0,
        'TITLE_FUZZY': 0,
        'NO_MATCH': 0
    }
    
    detailed_matches = []
    
    # 执行匹配和合并
    logging.info("开始匹配和合并数据...")
    for idx, target_row in target_df.iterrows():
        match_idx, match_type = find_matching_record(
            target_row, wos_df, doi_col_wos, title_col_wos, 
            doi_col_target, title_col_target
        )
        
        if match_idx is not None:
            # 复制关键词数据
            author_keywords = wos_df.loc[match_idx, author_keywords_col]
            keywords_plus = wos_df.loc[match_idx, keywords_plus_col]
            
            target_df.loc[idx, 'author_keywords_wos'] = author_keywords if pd.notna(author_keywords) else ""
            target_df.loc[idx, 'keywords_plus_wos'] = keywords_plus if pd.notna(keywords_plus) else ""
            
            # 统计匹配类型
            match_category = match_type.split('_')[0] + '_' + match_type.split('_')[1] if '_' in match_type else match_type
            if match_category.startswith('TITLE_FUZZY'):
                match_stats['TITLE_FUZZY'] += 1
            else:
                match_stats[match_category] += 1
            
            # 记录详细匹配信息
            detailed_matches.append({
                'target_index': idx,
                'target_title': target_row.get(title_col_target, ''),
                'target_doi': target_row.get(doi_col_target, ''),
                'wos_index': match_idx,
                'wos_title': wos_df.loc[match_idx, title_col_wos] if title_col_wos else '',
                'wos_doi': wos_df.loc[match_idx, doi_col_wos] if doi_col_wos else '',
                'match_type': match_type,
                'author_keywords': author_keywords if pd.notna(author_keywords) else '',
                'keywords_plus': keywords_plus if pd.notna(keywords_plus) else ''
            })
        else:
            match_stats['NO_MATCH'] += 1
    
    # 保存结果
    logging.info(f"保存合并结果到: {output_file_path}")
    target_df.to_excel(output_file_path, index=False, engine='openpyxl')
    
    # 输出统计信息
    logging.info("\n=== 匹配统计 ===")
    total_records = len(target_df)
    for match_type, count in match_stats.items():
        percentage = (count / total_records) * 100
        logging.info(f"{match_type}: {count} 条记录 ({percentage:.1f}%)")
    
    # 保存详细匹配报告
    if detailed_matches:
        match_report_path = output_file_path.replace('.xlsx', '_match_report.xlsx')
        match_df = pd.DataFrame(detailed_matches)
        match_df.to_excel(match_report_path, index=False, engine='openpyxl')
        logging.info(f"详细匹配报告已保存: {match_report_path}")
    
    logging.info("关键词合并任务完成!")
    return True

def main():
    """主函数"""
    # 文件路径配置
    wos_file_path = "/Users/tommy/Projects/projects/AI学术分析/智能整理/data/raw/202507271400-Geoffery-Hinton-WOS-17.xls"
    target_file_path = "/Users/tommy/Projects/projects/AI学术分析/智能整理/data/processed/Hinton_with_Affiliations_v4.xlsx"
    output_file_path = "/Users/tommy/Projects/projects/AI学术分析/智能整理/data/processed/Hinton_with_Affiliations_v5.xlsx"
    
    # 执行合并操作
    success = merge_keywords_data(wos_file_path, target_file_path, output_file_path)
    
    if success:
        print(f"\n✅ 任务完成! 结果已保存到: {output_file_path}")
        print(f"📝 操作日志: keyword_merge_log.txt")
        print(f"🔄 备份文件已创建在 data/backup/ 目录中")
    else:
        print("\n❌ 任务失败，请查看日志了解详细信息")

if __name__ == "__main__":
    main() 