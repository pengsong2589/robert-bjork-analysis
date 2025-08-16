#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按年份整理PDF文件脚本
根据CSV元数据中的发表年份，将PDF文件分类到对应年份的文件夹中

作者：AI助手
创建时间：2025-01-28
功能：
1. 读取CSV元数据，建立DOI到年份的映射
2. 扫描PDF文件，根据文件名中的DOI匹配年份  
3. 按年份创建目录结构并复制文件
4. 生成详细的处理日志
"""

import os
import csv
import shutil
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
import logging

class PaperOrganizer:
    """论文按年份整理器"""
    
    def __init__(self, csv_path, input_dir, output_dir):
        """
        初始化整理器
        
        Args:
            csv_path: CSV元数据文件路径
            input_dir: PDF文件输入目录
            output_dir: 按年份整理后的输出目录
        """
        self.csv_path = csv_path
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.doi_to_year = {}
        self.processing_log = []
        self.stats = {
            'total_papers': 0,
            'organized_papers': 0,
            'unknown_year_papers': 0,
            'missing_files': 0,
            'years_found': set()
        }
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('paper_organization.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_csv_metadata(self):
        """
        加载CSV元数据，建立DOI到年份的映射
        """
        self.logger.info(f"正在加载CSV元数据文件: {self.csv_path}")
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                # 跳过可能的BOM标记
                content = file.read()
                if content.startswith('\ufeff'):
                    content = content[1:]
                
                # 重新处理CSV内容
                lines = content.strip().split('\n')
                reader = csv.reader(lines)
                
                headers = next(reader)
                # 找到相关列的索引
                doi_col = headers.index('DOI') if 'DOI' in headers else 8
                year_col = headers.index('Publication Year') if 'Publication Year' in headers else 2
                
                for row_num, row in enumerate(reader, start=2):
                    if len(row) > max(doi_col, year_col):
                        doi = row[doi_col].strip()
                        year = row[year_col].strip()
                        
                        if doi and year and year.isdigit():
                            # 标准化DOI格式（移除可能的前缀）
                            if doi.startswith('https://doi.org/'):
                                doi = doi.replace('https://doi.org/', '')
                            
                            self.doi_to_year[doi] = int(year)
                            self.stats['years_found'].add(int(year))
                        else:
                            self.logger.warning(f"第{row_num}行数据不完整: DOI='{doi}', Year='{year}'")
            
            self.logger.info(f"成功加载 {len(self.doi_to_year)} 条DOI-年份映射记录")
            self.logger.info(f"年份范围: {min(self.stats['years_found'])} - {max(self.stats['years_found'])}")
            
        except Exception as e:
            self.logger.error(f"加载CSV文件失败: {e}")
            raise
    
    def extract_doi_from_filename(self, filename):
        """
        从PDF文件名中提取DOI
        
        Args:
            filename: PDF文件名，如 "[10.1038_306021a0].pdf"
            
        Returns:
            str: 提取的DOI，如 "10.1038_306021a0"
        """
        # 匹配方括号中的DOI格式
        match = re.match(r'\[([^\]]+)\]\.pdf$', filename)
        if match:
            return match.group(1)
        return None
    
    def create_year_directories(self):
        """
        创建年份目录结构
        """
        self.logger.info("正在创建年份目录结构...")
        
        # 创建输出根目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 为每个年份创建目录
        for year in sorted(self.stats['years_found']):
            year_dir = self.output_dir / str(year)
            year_dir.mkdir(exist_ok=True)
            self.logger.debug(f"创建目录: {year_dir}")
        
        # 创建unknown目录用于存放无法匹配年份的文件
        unknown_dir = self.output_dir / 'unknown'
        unknown_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"成功创建 {len(self.stats['years_found'])} 个年份目录和1个unknown目录")
    
    def organize_papers(self):
        """
        按年份整理PDF文件
        """
        self.logger.info("开始整理PDF文件...")
        
        # 获取所有PDF文件
        pdf_files = list(self.input_dir.glob("*.pdf"))
        self.stats['total_papers'] = len(pdf_files)
        
        self.logger.info(f"发现 {self.stats['total_papers']} 个PDF文件")
        
        year_counts = Counter()
        
        for pdf_file in pdf_files:
            filename = pdf_file.name
            
            # 跳过非DOI命名的辅助文件
            if not filename.startswith('['):
                self.logger.debug(f"跳过非DOI文件: {filename}")
                continue
            
            # 提取DOI
            doi = self.extract_doi_from_filename(filename)
            if not doi:
                self.logger.warning(f"无法从文件名提取DOI: {filename}")
                self._copy_to_unknown(pdf_file)
                continue
            
            # 查找对应年份
            year = self.doi_to_year.get(doi)
            if year:
                # 复制到对应年份目录
                target_dir = self.output_dir / str(year)
                target_file = target_dir / filename
                
                try:
                    shutil.copy2(pdf_file, target_file)
                    year_counts[year] += 1
                    self.stats['organized_papers'] += 1
                    
                    log_entry = {
                        'action': '复制成功',
                        'file': filename,
                        'doi': doi,
                        'year': year,
                        'source': str(pdf_file),
                        'target': str(target_file)
                    }
                    self.processing_log.append(log_entry)
                    
                    self.logger.debug(f"复制文件: {filename} -> {year}年目录")
                    
                except Exception as e:
                    self.logger.error(f"复制文件失败 {filename}: {e}")
                    
            else:
                self.logger.warning(f"未找到DOI对应年份: {doi} (文件: {filename})")
                self._copy_to_unknown(pdf_file)
        
        # 输出各年份统计
        self.logger.info("各年份文件分布:")
        for year in sorted(year_counts.keys()):
            self.logger.info(f"  {year}年: {year_counts[year]} 篇")
        
        if self.stats['unknown_year_papers'] > 0:
            self.logger.info(f"  未知年份: {self.stats['unknown_year_papers']} 篇")
    
    def _copy_to_unknown(self, pdf_file):
        """
        将无法确定年份的文件复制到unknown目录
        
        Args:
            pdf_file: PDF文件路径对象
        """
        unknown_dir = self.output_dir / 'unknown'
        target_file = unknown_dir / pdf_file.name
        
        try:
            shutil.copy2(pdf_file, target_file)
            self.stats['unknown_year_papers'] += 1
            
            log_entry = {
                'action': '复制到未知目录',
                'file': pdf_file.name,
                'doi': 'unknown',
                'year': 'unknown',
                'source': str(pdf_file),
                'target': str(target_file)
            }
            self.processing_log.append(log_entry)
            
        except Exception as e:
            self.logger.error(f"复制到unknown目录失败 {pdf_file.name}: {e}")
    
    def generate_processing_report(self):
        """
        生成详细的处理报告
        """
        report_file = self.output_dir / '整理报告.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("PDF文件按年份整理报告\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"输入目录: {self.input_dir}\n")
            f.write(f"输出目录: {self.output_dir}\n\n")
            
            f.write("处理统计:\n")
            f.write(f"  总文件数: {self.stats['total_papers']}\n")
            f.write(f"  成功整理: {self.stats['organized_papers']}\n")
            f.write(f"  未知年份: {self.stats['unknown_year_papers']}\n")
            f.write(f"  覆盖年份: {len(self.stats['years_found'])} 个\n")
            f.write(f"  年份范围: {min(self.stats['years_found'])} - {max(self.stats['years_found'])}\n\n")
            
            # 目录结构
            f.write("创建的目录结构:\n")
            f.write(f"{self.output_dir.name}/\n")
            for year in sorted(self.stats['years_found']):
                year_dir = self.output_dir / str(year)
                file_count = len(list(year_dir.glob("*.pdf")))
                f.write(f"  ├── {year}/ ({file_count} files)\n")
            
            unknown_dir = self.output_dir / 'unknown'
            unknown_count = len(list(unknown_dir.glob("*.pdf")))
            f.write(f"  └── unknown/ ({unknown_count} files)\n\n")
            
            # 详细处理日志
            f.write("详细处理日志:\n")
            f.write("-" * 80 + "\n")
            for i, entry in enumerate(self.processing_log, 1):
                f.write(f"{i:3d}. {entry['action']}: {entry['file']}\n")
                f.write(f"     DOI: {entry['doi']}\n")
                f.write(f"     年份: {entry['year']}\n")
                f.write(f"     源文件: {entry['source']}\n")
                f.write(f"     目标文件: {entry['target']}\n\n")
        
        self.logger.info(f"处理报告已生成: {report_file}")
    
    def run(self):
        """
        执行完整的整理流程
        """
        try:
            self.logger.info("开始PDF文件按年份整理流程...")
            
            # 1. 加载CSV元数据
            self.load_csv_metadata()
            
            # 2. 创建目录结构
            self.create_year_directories()
            
            # 3. 整理文件
            self.organize_papers()
            
            # 4. 生成报告
            self.generate_processing_report()
            
            self.logger.info("PDF文件整理完成！")
            self.logger.info(f"总计处理 {self.stats['total_papers']} 个文件")
            self.logger.info(f"成功整理 {self.stats['organized_papers']} 个文件")
            self.logger.info(f"无法确定年份 {self.stats['unknown_year_papers']} 个文件")
            
        except Exception as e:
            self.logger.error(f"整理过程出现错误: {e}")
            raise


def main():
    """主函数"""
    # 配置路径
    current_dir = Path(__file__).parent
    csv_path = current_dir.parent / 'data' / 'raw' / '202507271930_Hinton_Papers_30_v2.csv'
    input_dir = current_dir.parent / 'data' / 'processed' / 'doi_renamed_pdfs_improved'
    output_dir = current_dir.parent / 'data' / 'processed' / 'organized_papers_by_year'
    
    # 创建整理器并执行
    organizer = PaperOrganizer(csv_path, input_dir, output_dir)
    organizer.run()


if __name__ == '__main__':
    main() 