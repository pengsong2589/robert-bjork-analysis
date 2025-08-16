#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据CSV文件中的DOI信息，将PDF文件重命名为[DOI].pdf格式

作者: AI助手
日期: 2025-01-26
功能: 
1. 解析CSV文件获取DOI信息
2. 遍历PDF文件夹，匹配文件名
3. 复制并重命名PDF文件为[DOI].pdf格式
4. 生成处理报告和缺失清单
"""

import csv
import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_rename_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PDFRenamer:
    """PDF文件重命名处理器"""
    
    def __init__(self, csv_path: str, pdf_folder: str, output_folder: str):
        """
        初始化重命名器
        
        参数:
        csv_path: CSV文件路径
        pdf_folder: PDF文件夹路径
        output_folder: 输出文件夹路径
        """
        self.csv_path = csv_path
        self.pdf_folder = pdf_folder
        self.output_folder = output_folder
        self.doi_mapping = {}  # 文件名 -> DOI的映射
        self.processed_files = []  # 已处理的文件列表
        self.missing_doi_files = []  # 缺失DOI的文件列表
        
        # 创建输出文件夹
        os.makedirs(output_folder, exist_ok=True)
        
    def parse_csv(self) -> Dict[str, str]:
        """解析CSV文件，提取文件名和DOI的映射关系"""
        logger.info(f"开始解析CSV文件: {self.csv_path}")
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    doi = row.get('DOI', '').strip()
                    file_attachment = row.get('File Attachments', '').strip()
                    
                    if doi and file_attachment:
                        # 从文件路径中提取文件名
                        filename = os.path.basename(file_attachment)
                        if filename.endswith('.pdf'):
                            self.doi_mapping[filename] = doi
                            logger.debug(f"映射添加: {filename} -> {doi}")
                            
            logger.info(f"CSV解析完成，共找到 {len(self.doi_mapping)} 个文件-DOI映射")
            return self.doi_mapping
            
        except Exception as e:
            logger.error(f"解析CSV文件时出错: {e}")
            raise
    
    def sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除或替换不合法的字符"""
        # 替换文件名中的特殊字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 移除连续的点
        filename = re.sub(r'\.+', '.', filename)
        # 限制文件名长度
        if len(filename) > 255:
            name_part = filename[:-4]  # 移除.pdf
            filename = name_part[:251] + '.pdf'
        return filename
    
    def find_pdf_files(self) -> List[Tuple[str, str]]:
        """查找所有PDF文件，返回(文件路径, 文件名)的列表"""
        logger.info(f"开始搜索PDF文件: {self.pdf_folder}")
        
        pdf_files = []
        for root, dirs, files in os.walk(self.pdf_folder):
            for file in files:
                if file.endswith('.pdf'):
                    file_path = os.path.join(root, file)
                    pdf_files.append((file_path, file))
                    
        logger.info(f"找到 {len(pdf_files)} 个PDF文件")
        return pdf_files
    
    def process_files(self):
        """处理所有PDF文件"""
        logger.info("开始处理PDF文件...")
        
        # 解析CSV文件
        self.parse_csv()
        
        # 查找所有PDF文件
        pdf_files = self.find_pdf_files()
        
        # 处理每个PDF文件
        for file_path, filename in pdf_files:
            self.process_single_file(file_path, filename)
            
        # 生成报告
        self.generate_report()
    
    def process_single_file(self, file_path: str, filename: str):
        """处理单个PDF文件"""
        logger.debug(f"处理文件: {filename}")
        
        # 查找对应的DOI
        doi = self.doi_mapping.get(filename)
        
        if doi:
            # 清理DOI，创建新文件名
            clean_doi = self.sanitize_filename(f"[{doi}].pdf")
            new_path = os.path.join(self.output_folder, clean_doi)
            
            try:
                # 复制文件
                shutil.copy2(file_path, new_path)
                self.processed_files.append({
                    'original_file': filename,
                    'original_path': file_path,
                    'new_name': clean_doi,
                    'new_path': new_path,
                    'doi': doi
                })
                logger.info(f"成功处理: {filename} -> {clean_doi}")
                
            except Exception as e:
                logger.error(f"复制文件失败 {filename}: {e}")
                
        else:
            # 没有找到对应的DOI
            self.missing_doi_files.append({
                'filename': filename,
                'path': file_path
            })
            logger.warning(f"未找到DOI: {filename}")
    
    def generate_report(self):
        """生成处理报告"""
        logger.info("生成处理报告...")
        
        # 生成成功处理报告
        success_report_path = os.path.join(self.output_folder, '处理成功报告.txt')
        with open(success_report_path, 'w', encoding='utf-8') as f:
            f.write("PDF文件重命名处理报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"处理时间: {self.get_current_time()}\n")
            f.write(f"成功处理文件数: {len(self.processed_files)}\n")
            f.write(f"缺失DOI文件数: {len(self.missing_doi_files)}\n\n")
            
            f.write("成功处理的文件:\n")
            f.write("-" * 30 + "\n")
            for i, file_info in enumerate(self.processed_files, 1):
                f.write(f"{i}. 原文件名: {file_info['original_file']}\n")
                f.write(f"   新文件名: {file_info['new_name']}\n")
                f.write(f"   DOI: {file_info['doi']}\n")
                f.write(f"   原路径: {file_info['original_path']}\n")
                f.write(f"   新路径: {file_info['new_path']}\n\n")
        
        # 生成缺失DOI清单
        missing_report_path = os.path.join(self.output_folder, '缺失DOI清单.txt')
        with open(missing_report_path, 'w', encoding='utf-8') as f:
            f.write("缺失DOI的PDF文件清单\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"总数: {len(self.missing_doi_files)}\n\n")
            
            for i, file_info in enumerate(self.missing_doi_files, 1):
                f.write(f"{i}. 文件名: {file_info['filename']}\n")
                f.write(f"   路径: {file_info['path']}\n\n")
        
        logger.info(f"报告已生成:")
        logger.info(f"  - 成功处理报告: {success_report_path}")
        logger.info(f"  - 缺失DOI清单: {missing_report_path}")
        
        # 打印摘要
        print("\n" + "=" * 60)
        print("处理完成摘要:")
        print(f"✅ 成功处理: {len(self.processed_files)} 个文件")
        print(f"⚠️  缺失DOI: {len(self.missing_doi_files)} 个文件")
        print(f"📁 输出目录: {self.output_folder}")
        print("=" * 60)
    
    def get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """主函数"""
    # 文件路径配置
    base_dir = "projects/AI学术分析/智能整理/data"
    csv_path = os.path.join(base_dir, "raw/202507271930_Hinton_Papers_30.csv")
    pdf_folder = os.path.join(base_dir, "raw/Hinton_papers_PDF_30/files")
    output_folder = os.path.join(base_dir, "processed/doi_renamed_pdfs")
    
    # 检查文件是否存在
    if not os.path.exists(csv_path):
        logger.error(f"CSV文件不存在: {csv_path}")
        return
        
    if not os.path.exists(pdf_folder):
        logger.error(f"PDF文件夹不存在: {pdf_folder}")
        return
    
    # 创建重命名器并处理文件
    renamer = PDFRenamer(csv_path, pdf_folder, output_folder)
    
    try:
        renamer.process_files()
        logger.info("所有文件处理完成!")
        
    except Exception as e:
        logger.error(f"处理过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    main() 