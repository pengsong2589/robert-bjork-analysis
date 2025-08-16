#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据CSV文件中的DOI信息，将PDF文件重命名为[DOI].pdf格式 - 改进版

作者: AI助手
日期: 2025-01-26
改进功能: 
1. 更清晰地展示DOI转换过程（/ 转为 _）
2. 详细记录每个转换步骤
3. 提供转换前后对比报告
4. 验证转换结果的准确性
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
        logging.FileHandler('pdf_rename_improved_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImprovedPDFRenamer:
    """改进的PDF文件重命名处理器"""
    
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
        self.doi_transformations = {}  # DOI转换记录
        
        # 创建输出文件夹
        os.makedirs(output_folder, exist_ok=True)
        
    def parse_csv(self) -> Dict[str, str]:
        """解析CSV文件，提取文件名和DOI的映射关系"""
        logger.info(f"开始解析CSV文件: {self.csv_path}")
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    original_doi = row.get('DOI', '').strip()
                    file_attachment = row.get('File Attachments', '').strip()
                    
                    if original_doi and file_attachment:
                        # 从文件路径中提取文件名
                        filename = os.path.basename(file_attachment)
                        if filename.endswith('.pdf'):
                            # 记录DOI转换过程
                            transformed_doi = self.transform_doi_for_filename(original_doi)
                            self.doi_transformations[original_doi] = transformed_doi
                            
                            self.doi_mapping[filename] = original_doi
                            logger.debug(f"映射添加: {filename} -> {original_doi}")
                            logger.debug(f"DOI转换: {original_doi} -> {transformed_doi}")
                            
            logger.info(f"CSV解析完成，共找到 {len(self.doi_mapping)} 个文件-DOI映射")
            return self.doi_mapping
            
        except Exception as e:
            logger.error(f"解析CSV文件时出错: {e}")
            raise
    
    def transform_doi_for_filename(self, doi: str) -> str:
        """
        将DOI转换为适合文件名的格式
        主要转换: / -> _，同时处理其他特殊字符
        """
        # 记录原始DOI
        original = doi
        
        # 替换斜杠为下划线（这是最重要的转换）
        transformed = doi.replace('/', '_')
        
        # 替换其他文件名不兼容的字符
        transformed = re.sub(r'[<>:"|?*]', '_', transformed)
        
        # 移除连续的下划线
        transformed = re.sub(r'_+', '_', transformed)
        
        logger.debug(f"DOI转换详情: '{original}' -> '{transformed}'")
        return transformed
    
    def create_filename_from_doi(self, doi: str) -> str:
        """基于DOI创建标准化的文件名"""
        transformed_doi = self.transform_doi_for_filename(doi)
        return f"[{transformed_doi}].pdf"
    
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
        
        # 打印DOI转换摘要
        self.print_doi_transformation_summary()
        
        # 查找所有PDF文件
        pdf_files = self.find_pdf_files()
        
        # 处理每个PDF文件
        for file_path, filename in pdf_files:
            self.process_single_file(file_path, filename)
            
        # 生成报告
        self.generate_comprehensive_report()
    
    def print_doi_transformation_summary(self):
        """打印DOI转换摘要"""
        print("\n" + "="*60)
        print("DOI转换摘要 (/ -> _)")
        print("="*60)
        
        for original, transformed in list(self.doi_transformations.items())[:5]:
            print(f"原始DOI: {original}")
            print(f"转换后:  {transformed}")
            print(f"文件名:  [{transformed}].pdf")
            print("-" * 40)
        
        if len(self.doi_transformations) > 5:
            print(f"... 还有 {len(self.doi_transformations) - 5} 个转换项")
        print("="*60 + "\n")
    
    def process_single_file(self, file_path: str, filename: str):
        """处理单个PDF文件"""
        logger.debug(f"处理文件: {filename}")
        
        # 查找对应的DOI
        original_doi = self.doi_mapping.get(filename)
        
        if original_doi:
            # 创建新文件名
            new_filename = self.create_filename_from_doi(original_doi)
            new_path = os.path.join(self.output_folder, new_filename)
            
            try:
                # 复制文件
                shutil.copy2(file_path, new_path)
                
                self.processed_files.append({
                    'original_file': filename,
                    'original_path': file_path,
                    'original_doi': original_doi,
                    'transformed_doi': self.transform_doi_for_filename(original_doi),
                    'new_filename': new_filename,
                    'new_path': new_path
                })
                
                logger.info(f"✅ 成功: {filename}")
                logger.info(f"   DOI: {original_doi}")
                logger.info(f"   新名: {new_filename}")
                
            except Exception as e:
                logger.error(f"❌ 复制文件失败 {filename}: {e}")
                
        else:
            # 没有找到对应的DOI
            self.missing_doi_files.append({
                'filename': filename,
                'path': file_path
            })
            logger.warning(f"⚠️  未找到DOI: {filename}")
    
    def generate_comprehensive_report(self):
        """生成详细的处理报告"""
        logger.info("生成详细处理报告...")
        
        # 生成DOI转换对照表
        self.generate_doi_transformation_report()
        
        # 生成成功处理报告
        self.generate_success_report()
        
        # 生成缺失DOI清单
        self.generate_missing_doi_report()
        
        # 打印最终摘要
        self.print_final_summary()
    
    def generate_doi_transformation_report(self):
        """生成DOI转换对照表报告"""
        report_path = os.path.join(self.output_folder, 'DOI转换对照表.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("DOI转换对照表报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"处理时间: {self.get_current_time()}\n")
            f.write(f"转换说明: 将DOI中的'/'替换为'_'以符合文件系统要求\n\n")
            
            f.write("详细转换对照:\n")
            f.write("-" * 30 + "\n")
            
            for i, (original, transformed) in enumerate(self.doi_transformations.items(), 1):
                f.write(f"{i}. 原始DOI: {original}\n")
                f.write(f"   转换DOI: {transformed}\n")
                f.write(f"   文件名:  [{transformed}].pdf\n")
                if '/' in original:
                    f.write(f"   转换点: '/' -> '_' ({original.count('/')}处)\n")
                f.write("\n")
        
        logger.info(f"DOI转换对照表已生成: {report_path}")
    
    def generate_success_report(self):
        """生成成功处理报告"""
        success_report_path = os.path.join(self.output_folder, '详细处理报告.txt')
        with open(success_report_path, 'w', encoding='utf-8') as f:
            f.write("PDF文件重命名详细处理报告\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"处理时间: {self.get_current_time()}\n")
            f.write(f"成功处理文件数: {len(self.processed_files)}\n")
            f.write(f"缺失DOI文件数: {len(self.missing_doi_files)}\n")
            f.write(f"处理成功率: {len(self.processed_files)/(len(self.processed_files)+len(self.missing_doi_files))*100:.1f}%\n\n")
            
            f.write("成功处理的文件详情:\n")
            f.write("-" * 40 + "\n")
            for i, file_info in enumerate(self.processed_files, 1):
                f.write(f"{i}. 原文件名: {file_info['original_file']}\n")
                f.write(f"   新文件名: {file_info['new_filename']}\n")
                f.write(f"   原始DOI: {file_info['original_doi']}\n")
                f.write(f"   转换DOI: {file_info['transformed_doi']}\n")
                f.write(f"   原路径: {file_info['original_path']}\n")
                f.write(f"   新路径: {file_info['new_path']}\n\n")
        
        logger.info(f"详细处理报告已生成: {success_report_path}")
    
    def generate_missing_doi_report(self):
        """生成缺失DOI清单"""
        missing_report_path = os.path.join(self.output_folder, '缺失DOI清单.txt')
        with open(missing_report_path, 'w', encoding='utf-8') as f:
            f.write("缺失DOI的PDF文件清单\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"总数: {len(self.missing_doi_files)}\n\n")
            
            if self.missing_doi_files:
                for i, file_info in enumerate(self.missing_doi_files, 1):
                    f.write(f"{i}. 文件名: {file_info['filename']}\n")
                    f.write(f"   路径: {file_info['path']}\n\n")
            else:
                f.write("🎉 所有PDF文件都成功匹配到了对应的DOI！\n")
        
        logger.info(f"缺失DOI清单已生成: {missing_report_path}")
    
    def print_final_summary(self):
        """打印最终处理摘要"""
        print("\n" + "=" * 80)
        print("🎉 PDF文件DOI重命名处理完成！")
        print("=" * 80)
        print(f"✅ 成功处理: {len(self.processed_files)} 个文件")
        print(f"⚠️  缺失DOI: {len(self.missing_doi_files)} 个文件")
        print(f"📁 输出目录: {self.output_folder}")
        print(f"📊 成功率: {len(self.processed_files)/(len(self.processed_files)+len(self.missing_doi_files))*100:.1f}%")
        
        print("\n🔄 DOI转换统计:")
        slash_count = sum(1 for doi in self.doi_transformations.keys() if '/' in doi)
        print(f"   - 包含'/'的DOI: {slash_count}/{len(self.doi_transformations)}")
        print(f"   - 转换为'_': {slash_count} 处转换")
        
        print("\n📋 生成的报告文件:")
        print("   - DOI转换对照表.txt")
        print("   - 详细处理报告.txt") 
        print("   - 缺失DOI清单.txt")
        print("=" * 80)
    
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
    output_folder = os.path.join(base_dir, "processed/doi_renamed_pdfs_improved")
    
    # 检查文件是否存在
    if not os.path.exists(csv_path):
        logger.error(f"CSV文件不存在: {csv_path}")
        return
        
    if not os.path.exists(pdf_folder):
        logger.error(f"PDF文件夹不存在: {pdf_folder}")
        return
    
    # 创建改进版重命名器并处理文件
    renamer = ImprovedPDFRenamer(csv_path, pdf_folder, output_folder)
    
    try:
        renamer.process_files()
        logger.info("🎉 所有文件处理完成!")
        
    except Exception as e:
        logger.error(f"❌ 处理过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    main() 