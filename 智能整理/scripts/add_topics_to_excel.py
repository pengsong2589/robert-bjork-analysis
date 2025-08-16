#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加论文主题到Excel文件
从CSV文件中提取主题信息，通过DOI或标题匹配，添加到Excel文件中
保留PDF路径的软链接功能

Author: AI Assistant
Date: 2025-01-27
"""

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import logging
from datetime import datetime
import re

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('add_topics_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def clean_doi(doi):
    """清理DOI格式，统一比较格式"""
    if pd.isna(doi) or not doi:
        return ""
    doi_str = str(doi).strip()
    # 移除常见的DOI前缀
    doi_str = re.sub(r'^(doi:|DOI:|https?://doi\.org/|https?://dx\.doi\.org/)', '', doi_str)
    # 将下划线替换为点，因为CSV中的DOI使用下划线格式
    doi_str = doi_str.replace('_', '.')
    return doi_str.lower()

def clean_title(title):
    """清理标题，用于匹配"""
    if pd.isna(title) or not title:
        return ""
    # 转换为小写，移除多余空格和标点
    title_clean = str(title).lower().strip()
    title_clean = re.sub(r'[^\w\s]', ' ', title_clean)
    title_clean = re.sub(r'\s+', ' ', title_clean)
    return title_clean

def extract_topics_from_tags(manual_tags, automatic_tags):
    """从标签中提取主题"""
    topics = []
    
    # 处理Manual Tags
    if pd.notna(manual_tags) and manual_tags:
        manual_topics = str(manual_tags).split(';')
        topics.extend([t.strip() for t in manual_topics if t.strip()])
    
    # 处理Automatic Tags（如果Manual Tags为空）
    if not topics and pd.notna(automatic_tags) and automatic_tags:
        auto_topics = str(automatic_tags).split(';')
        topics.extend([t.strip() for t in auto_topics if t.strip()])
    
    # 去重并返回
    unique_topics = list(set(topics))
    return '; '.join(unique_topics) if unique_topics else ""

def backup_file(file_path):
    """备份文件到data/backup/目录"""
    backup_dir = Path("data/backup")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}_{Path(file_path).name}"
    backup_path = backup_dir / backup_name
    
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        logging.info(f"文件已备份到: {backup_path}")
        return backup_path
    except Exception as e:
        logging.error(f"备份文件失败: {e}")
        return None

def main():
    """主函数"""
    try:
        # 定义文件路径
        excel_file = "data/processed/Geoffrey_Hinton_机构信息_链接修复版_20250727.xlsx"
        csv_file = "data/raw/202507271930_Hinton_Papers_30_v2.csv"
        output_file = "data/processed/Hinton_with_Affiliations_v3.xlsx"
        
        # 检查文件是否存在
        if not os.path.exists(excel_file):
            logging.error(f"Excel文件不存在: {excel_file}")
            return False
            
        if not os.path.exists(csv_file):
            logging.error(f"CSV文件不存在: {csv_file}")
            return False
        
        # 备份原始Excel文件
        backup_file(excel_file)
        
        # 读取Excel文件
        logging.info(f"正在读取Excel文件: {excel_file}")
        try:
            excel_df = pd.read_excel(excel_file)
            logging.info(f"Excel文件读取成功，共 {len(excel_df)} 行数据")
            logging.info(f"Excel文件列名: {list(excel_df.columns)}")
        except Exception as e:
            logging.error(f"读取Excel文件失败: {e}")
            return False
        
        # 读取CSV文件
        logging.info(f"正在读取CSV文件: {csv_file}")
        try:
            csv_df = pd.read_csv(csv_file, encoding='utf-8')
            logging.info(f"CSV文件读取成功，共 {len(csv_df)} 行数据")
            logging.info(f"CSV文件列名: {list(csv_df.columns)}")
        except Exception as e:
            logging.error(f"读取CSV文件失败: {e}")
            return False
        
        # 清理CSV数据中的DOI和标题
        csv_df['clean_doi'] = csv_df['DOI'].apply(clean_doi)
        csv_df['clean_title'] = csv_df['Title'].apply(clean_title)
        
        # 提取主题信息
        csv_df['topics'] = csv_df.apply(
            lambda row: extract_topics_from_tags(
                row.get('Manual Tags', ''), 
                row.get('Automatic Tags', '')
            ), 
            axis=1
        )
        
        # 初始化论文主题列
        excel_df['论文主题'] = ""
        
        # 统计匹配情况
        doi_matches = 0
        title_matches = 0
        no_matches = 0
        
        # 逐行匹配Excel数据
        for idx, excel_row in excel_df.iterrows():
            matched = False
            
            # 首先尝试通过DOI匹配
            if 'DOI' in excel_df.columns and pd.notna(excel_row.get('DOI')):
                excel_doi = clean_doi(excel_row['DOI'])
                if excel_doi:
                    csv_match = csv_df[csv_df['clean_doi'] == excel_doi]
                    if not csv_match.empty:
                        topics = csv_match.iloc[0]['topics']
                        if topics:
                            excel_df.at[idx, '论文主题'] = topics
                            matched = True
                            doi_matches += 1
                            logging.info(f"DOI匹配成功 {idx+1}: {excel_doi}")
            
            # 如果DOI匹配失败，尝试标题匹配
            if not matched and 'Title' in excel_df.columns:
                excel_title = clean_title(excel_row.get('Title', ''))
                if excel_title:
                    csv_match = csv_df[csv_df['clean_title'] == excel_title]
                    if not csv_match.empty:
                        topics = csv_match.iloc[0]['topics']
                        if topics:
                            excel_df.at[idx, '论文主题'] = topics
                            matched = True
                            title_matches += 1
                            logging.info(f"标题匹配成功 {idx+1}: {excel_title[:50]}...")
            
            if not matched:
                no_matches += 1
                title_preview = str(excel_row.get('Title', 'N/A'))[:50]
                logging.warning(f"未找到匹配 {idx+1}: {title_preview}...")
        
        # 输出匹配统计
        logging.info(f"匹配统计:")
        logging.info(f"  DOI匹配: {doi_matches}")
        logging.info(f"  标题匹配: {title_matches}")
        logging.info(f"  未匹配: {no_matches}")
        logging.info(f"  总计: {len(excel_df)}")
        
        # 确保输出目录存在
        output_dir = Path(output_file).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存新的Excel文件，保留原有格式
        logging.info(f"正在保存到: {output_file}")
        try:
            # 使用openpyxl引擎保持格式
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                excel_df.to_excel(writer, index=False, sheet_name='Sheet1')
            
            logging.info(f"文件保存成功: {output_file}")
            logging.info(f"新增了'论文主题'列，共填充了{doi_matches + title_matches}个条目的主题信息")
            
            return True
            
        except Exception as e:
            logging.error(f"保存文件失败: {e}")
            return False
            
    except Exception as e:
        logging.error(f"程序执行出错: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ 任务完成！论文主题已成功添加到Excel文件中。")
    else:
        print("❌ 任务失败，请检查日志文件获取详细信息。")
        sys.exit(1) 