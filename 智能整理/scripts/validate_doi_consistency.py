#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证CSV文件中的DOI和PDF文件名中的DOI是否完全一致

作者: AI助手
日期: 2025-01-26
功能: 
1. 读取CSV文件中的DOI列
2. 扫描PDF文件夹中的文件名
3. 比较两者的DOI是否完全匹配
4. 生成详细的验证报告
"""

import csv
import os
import re
from typing import List, Dict, Set
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('doi_validation_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DOIConsistencyValidator:
    """DOI一致性验证器"""
    
    def __init__(self, csv_path: str, pdf_folder: str):
        """
        初始化验证器
        
        参数:
        csv_path: CSV文件路径
        pdf_folder: PDF文件夹路径
        """
        self.csv_path = csv_path
        self.pdf_folder = pdf_folder
        self.csv_dois = set()  # CSV中的DOI集合
        self.pdf_dois = set()  # PDF文件名中的DOI集合
        self.csv_doi_list = []  # CSV中的DOI列表（保持顺序）
        self.pdf_files = []  # PDF文件列表
        
    def extract_csv_dois(self):
        """从CSV文件中提取DOI"""
        logger.info(f"开始从CSV文件提取DOI: {self.csv_path}")
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row_index, row in enumerate(reader, 1):
                    doi = row.get('DOI', '').strip()
                    if doi:
                        self.csv_dois.add(doi)
                        self.csv_doi_list.append({
                            'row': row_index,
                            'doi': doi,
                            'title': row.get('Title', '').strip()[:50] + '...' if len(row.get('Title', '')) > 50 else row.get('Title', '').strip()
                        })
                        logger.debug(f"CSV第{row_index}行 DOI: {doi}")
                        
            logger.info(f"从CSV中提取到 {len(self.csv_dois)} 个唯一DOI")
            
        except Exception as e:
            logger.error(f"读取CSV文件失败: {e}")
            raise
    
    def extract_pdf_dois(self):
        """从PDF文件名中提取DOI"""
        logger.info(f"开始从PDF文件名提取DOI: {self.pdf_folder}")
        
        # DOI文件名格式：[DOI].pdf
        doi_pattern = re.compile(r'^\[(.+)\]\.pdf$')
        
        try:
            for filename in os.listdir(self.pdf_folder):
                if filename.endswith('.pdf'):
                    match = doi_pattern.match(filename)
                    if match:
                        doi = match.group(1)
                        self.pdf_dois.add(doi)
                        self.pdf_files.append({
                            'filename': filename,
                            'doi': doi
                        })
                        logger.debug(f"PDF文件 {filename} -> DOI: {doi}")
                    else:
                        logger.warning(f"PDF文件名格式不符合[DOI].pdf: {filename}")
                        
            logger.info(f"从PDF文件名中提取到 {len(self.pdf_dois)} 个DOI")
            
        except Exception as e:
            logger.error(f"扫描PDF文件夹失败: {e}")
            raise
    
    def compare_dois(self):
        """比较CSV和PDF中的DOI"""
        logger.info("开始比较CSV和PDF中的DOI...")
        
        # 找出差异
        csv_only = self.csv_dois - self.pdf_dois  # 只在CSV中存在
        pdf_only = self.pdf_dois - self.csv_dois  # 只在PDF中存在
        common = self.csv_dois & self.pdf_dois    # 共同存在
        
        # 输出比较结果
        print("\n" + "="*80)
        print("📊 DOI一致性验证结果")
        print("="*80)
        print(f"📁 CSV文件DOI数量: {len(self.csv_dois)}")
        print(f"📁 PDF文件DOI数量: {len(self.pdf_dois)}")
        print(f"✅ 完全匹配DOI: {len(common)}")
        print(f"❌ 仅CSV存在: {len(csv_only)}")
        print(f"❌ 仅PDF存在: {len(pdf_only)}")
        
        # 计算一致性百分比
        if len(self.csv_dois) > 0:
            consistency_rate = (len(common) / len(self.csv_dois)) * 100
            print(f"📈 一致性比例: {consistency_rate:.1f}%")
        
        # 详细展示不匹配项
        if csv_only:
            print(f"\n⚠️  仅在CSV中存在的DOI ({len(csv_only)}个):")
            for doi in sorted(csv_only):
                # 找到对应的标题
                title = "未找到标题"
                for item in self.csv_doi_list:
                    if item['doi'] == doi:
                        title = item['title']
                        break
                print(f"   - {doi} ({title})")
        
        if pdf_only:
            print(f"\n⚠️  仅在PDF中存在的DOI ({len(pdf_only)}个):")
            for doi in sorted(pdf_only):
                # 找到对应的文件名
                filename = "未找到文件名"
                for item in self.pdf_files:
                    if item['doi'] == doi:
                        filename = item['filename']
                        break
                print(f"   - {doi} ({filename})")
        
        if len(common) == len(self.csv_dois) == len(self.pdf_dois):
            print(f"\n🎉 完美匹配！所有DOI都完全一致！")
        
        print("="*80)
        
        return {
            'csv_count': len(self.csv_dois),
            'pdf_count': len(self.pdf_dois),
            'common_count': len(common),
            'csv_only': csv_only,
            'pdf_only': pdf_only,
            'common': common,
            'consistency_rate': (len(common) / len(self.csv_dois) * 100) if len(self.csv_dois) > 0 else 0
        }
    
    def generate_detailed_report(self, comparison_result):
        """生成详细的验证报告"""
        report_path = os.path.join(os.path.dirname(self.csv_path), 'DOI一致性验证报告.txt')
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("DOI一致性验证详细报告\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"验证时间: {self.get_current_time()}\n")
                f.write(f"CSV文件: {self.csv_path}\n")
                f.write(f"PDF文件夹: {self.pdf_folder}\n\n")
                
                f.write("验证结果统计:\n")
                f.write("-" * 30 + "\n")
                f.write(f"CSV文件DOI数量: {comparison_result['csv_count']}\n")
                f.write(f"PDF文件DOI数量: {comparison_result['pdf_count']}\n")
                f.write(f"完全匹配DOI数量: {comparison_result['common_count']}\n")
                f.write(f"一致性比例: {comparison_result['consistency_rate']:.1f}%\n\n")
                
                # 写入完全匹配的DOI列表
                f.write(f"完全匹配的DOI列表 ({len(comparison_result['common'])}个):\n")
                f.write("-" * 40 + "\n")
                for i, doi in enumerate(sorted(comparison_result['common']), 1):
                    f.write(f"{i:2d}. {doi}\n")
                f.write("\n")
                
                # 写入不匹配的详情
                if comparison_result['csv_only']:
                    f.write(f"仅在CSV中存在的DOI ({len(comparison_result['csv_only'])}个):\n")
                    f.write("-" * 40 + "\n")
                    for i, doi in enumerate(sorted(comparison_result['csv_only']), 1):
                        # 找标题
                        title = "未找到标题"
                        for item in self.csv_doi_list:
                            if item['doi'] == doi:
                                title = item['title']
                                break
                        f.write(f"{i:2d}. {doi}\n")
                        f.write(f"    标题: {title}\n\n")
                
                if comparison_result['pdf_only']:
                    f.write(f"仅在PDF中存在的DOI ({len(comparison_result['pdf_only'])}个):\n")
                    f.write("-" * 40 + "\n")
                    for i, doi in enumerate(sorted(comparison_result['pdf_only']), 1):
                        # 找文件名
                        filename = "未找到文件名"
                        for item in self.pdf_files:
                            if item['doi'] == doi:
                                filename = item['filename']
                                break
                        f.write(f"{i:2d}. {doi}\n")
                        f.write(f"    文件名: {filename}\n\n")
                
                # 建议
                f.write("处理建议:\n")
                f.write("-" * 20 + "\n")
                if comparison_result['consistency_rate'] == 100.0:
                    f.write("🎉 所有DOI完全一致，无需处理！\n")
                else:
                    if comparison_result['csv_only']:
                        f.write("• 检查缺失的PDF文件，可能需要重新下载或重命名\n")
                    if comparison_result['pdf_only']:
                        f.write("• 检查多余的PDF文件，可能需要更新CSV数据\n")
            
            logger.info(f"详细验证报告已生成: {report_path}")
            
        except Exception as e:
            logger.error(f"生成验证报告失败: {e}")
    
    def validate(self):
        """执行完整的验证流程"""
        logger.info("开始DOI一致性验证...")
        
        # 提取CSV中的DOI
        self.extract_csv_dois()
        
        # 提取PDF文件名中的DOI
        self.extract_pdf_dois()
        
        # 比较DOI
        comparison_result = self.compare_dois()
        
        # 生成详细报告
        self.generate_detailed_report(comparison_result)
        
        logger.info("DOI一致性验证完成")
        
        return comparison_result
    
    def get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """主函数"""
    # 文件路径配置
    base_dir = "projects/AI学术分析/智能整理/data"
    csv_path = os.path.join(base_dir, "raw/202507271930_Hinton_Papers_30_v2.csv")
    pdf_folder = os.path.join(base_dir, "processed/doi_renamed_pdfs_improved")
    
    # 检查文件是否存在
    if not os.path.exists(csv_path):
        logger.error(f"❌ CSV文件不存在: {csv_path}")
        return
        
    if not os.path.exists(pdf_folder):
        logger.error(f"❌ PDF文件夹不存在: {pdf_folder}")
        return
    
    # 创建验证器
    validator = DOIConsistencyValidator(csv_path, pdf_folder)
    
    try:
        # 执行验证
        result = validator.validate()
        
        # 输出最终结果
        print(f"\n🏁 验证完成！一致性比例: {result['consistency_rate']:.1f}%")
        
        if result['consistency_rate'] == 100.0:
            print("✅ 所有DOI完全匹配，数据一致性完美！")
        else:
            print("⚠️  发现不一致项，请查看详细报告")
        
    except Exception as e:
        logger.error(f"❌ 验证过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    main() 