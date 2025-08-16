#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改CSV文件中DOI列的格式，将'/'替换为'_'

作者: AI助手
日期: 2025-01-26
功能: 
1. 读取CSV文件
2. 修改DOI列（第I列）格式：/ -> _
3. 保持其他列内容不变
4. 生成新的CSV文件
"""

import csv
import os
import shutil
from typing import List, Dict
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('csv_doi_update_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CSVDOIUpdater:
    """CSV文件DOI格式更新器"""
    
    def __init__(self, input_csv_path: str, output_csv_path: str):
        """
        初始化更新器
        
        参数:
        input_csv_path: 输入CSV文件路径
        output_csv_path: 输出CSV文件路径
        """
        self.input_csv_path = input_csv_path
        self.output_csv_path = output_csv_path
        self.doi_column_index = 8  # DOI列是第I列（第9列，索引为8）
        self.updated_rows = []
        self.doi_changes = []  # 记录DOI变更
        
    def backup_original_file(self):
        """备份原始文件"""
        backup_path = self.input_csv_path + '.backup'
        try:
            shutil.copy2(self.input_csv_path, backup_path)
            logger.info(f"✅ 原始文件已备份: {backup_path}")
        except Exception as e:
            logger.error(f"❌ 备份文件失败: {e}")
            raise
    
    def transform_doi(self, doi: str) -> str:
        """
        转换DOI格式：/ -> _
        
        参数:
        doi: 原始DOI字符串
        
        返回:
        转换后的DOI字符串
        """
        if not doi or not isinstance(doi, str):
            return doi
            
        # 记录原始DOI
        original_doi = doi.strip()
        
        # 执行转换：/ -> _
        transformed_doi = original_doi.replace('/', '_')
        
        # 记录变更（如果有变化）
        if original_doi != transformed_doi:
            self.doi_changes.append({
                'original': original_doi,
                'transformed': transformed_doi,
                'change_count': original_doi.count('/')
            })
            logger.debug(f"DOI转换: '{original_doi}' -> '{transformed_doi}'")
        
        return transformed_doi
    
    def process_csv(self):
        """处理CSV文件"""
        logger.info(f"开始处理CSV文件: {self.input_csv_path}")
        
        try:
            # 读取CSV文件
            with open(self.input_csv_path, 'r', encoding='utf-8', newline='') as infile:
                # 使用csv.reader读取所有行
                reader = csv.reader(infile)
                rows = list(reader)
                
            logger.info(f"读取到 {len(rows)} 行数据")
            
            # 处理每一行
            for row_index, row in enumerate(rows):
                if row_index == 0:
                    # 标题行，直接保留
                    self.updated_rows.append(row)
                    logger.debug(f"标题行: {len(row)} 列")
                else:
                    # 数据行，处理DOI列
                    updated_row = row.copy()
                    
                    # 检查是否有足够的列
                    if len(updated_row) > self.doi_column_index:
                        original_doi = updated_row[self.doi_column_index]
                        updated_doi = self.transform_doi(original_doi)
                        updated_row[self.doi_column_index] = updated_doi
                        
                        logger.debug(f"第{row_index}行 DOI更新: '{original_doi}' -> '{updated_doi}'")
                    else:
                        logger.warning(f"第{row_index}行列数不足: {len(updated_row)} < {self.doi_column_index + 1}")
                    
                    self.updated_rows.append(updated_row)
            
            # 写入新的CSV文件
            self.write_updated_csv()
            
            # 生成报告
            self.generate_report()
            
            logger.info(f"✅ CSV文件处理完成")
            
        except Exception as e:
            logger.error(f"❌ 处理CSV文件时出错: {e}")
            raise
    
    def write_updated_csv(self):
        """写入更新后的CSV文件"""
        logger.info(f"写入新CSV文件: {self.output_csv_path}")
        
        try:
            with open(self.output_csv_path, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.writer(outfile)
                writer.writerows(self.updated_rows)
            
            logger.info(f"✅ 新CSV文件已生成: {self.output_csv_path}")
            
        except Exception as e:
            logger.error(f"❌ 写入CSV文件失败: {e}")
            raise
    
    def generate_report(self):
        """生成处理报告"""
        report_path = os.path.join(os.path.dirname(self.output_csv_path), 'DOI格式更新报告.txt')
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("CSV文件DOI格式更新报告\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"处理时间: {self.get_current_time()}\n")
                f.write(f"输入文件: {self.input_csv_path}\n")
                f.write(f"输出文件: {self.output_csv_path}\n")
                f.write(f"处理行数: {len(self.updated_rows)} 行\n")
                f.write(f"DOI更新数: {len(self.doi_changes)} 个\n\n")
                
                f.write("DOI格式变更详情:\n")
                f.write("-" * 30 + "\n")
                
                for i, change in enumerate(self.doi_changes, 1):
                    f.write(f"{i}. 原始DOI: {change['original']}\n")
                    f.write(f"   转换DOI: {change['transformed']}\n")
                    f.write(f"   转换点数: {change['change_count']} 处 '/' -> '_'\n\n")
                
                f.write(f"\n总转换统计:\n")
                f.write(f"- 总转换点数: {sum(c['change_count'] for c in self.doi_changes)} 处\n")
                f.write(f"- 平均每个DOI转换: {sum(c['change_count'] for c in self.doi_changes) / len(self.doi_changes):.1f} 处\n")
            
            logger.info(f"✅ 处理报告已生成: {report_path}")
            
        except Exception as e:
            logger.error(f"❌ 生成报告失败: {e}")
    
    def print_summary(self):
        """打印处理摘要"""
        print("\n" + "=" * 70)
        print("🎉 CSV文件DOI格式更新完成！")
        print("=" * 70)
        print(f"📁 输入文件: {os.path.basename(self.input_csv_path)}")
        print(f"📁 输出文件: {os.path.basename(self.output_csv_path)}")
        print(f"📊 处理行数: {len(self.updated_rows)} 行")
        print(f"🔄 DOI更新: {len(self.doi_changes)} 个")
        
        if self.doi_changes:
            total_transformations = sum(c['change_count'] for c in self.doi_changes)
            print(f"✏️  转换点数: {total_transformations} 处 '/' -> '_'")
            
            # 显示几个示例
            print(f"\n📝 转换示例:")
            for i, change in enumerate(self.doi_changes[:3], 1):
                print(f"   {i}. {change['original']} -> {change['transformed']}")
            
            if len(self.doi_changes) > 3:
                print(f"   ... 还有 {len(self.doi_changes) - 3} 个转换项")
        
        print("=" * 70)
    
    def get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """主函数"""
    # 文件路径配置
    base_dir = "projects/AI学术分析/智能整理/data/raw"
    input_csv = os.path.join(base_dir, "202507271930_Hinton_Papers_30.csv")
    output_csv = os.path.join(base_dir, "202507271930_Hinton_Papers_30_v2.csv")
    
    # 检查输入文件是否存在
    if not os.path.exists(input_csv):
        logger.error(f"❌ 输入CSV文件不存在: {input_csv}")
        return
    
    # 创建更新器
    updater = CSVDOIUpdater(input_csv, output_csv)
    
    try:
        # 备份原始文件
        updater.backup_original_file()
        
        # 处理CSV文件
        updater.process_csv()
        
        # 打印摘要
        updater.print_summary()
        
        logger.info("🎉 所有操作完成!")
        
    except Exception as e:
        logger.error(f"❌ 操作过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    main() 