#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geoffrey Hinton机构信息查询脚本
功能：从CSV文件中提取Geoffrey Hinton的论文，查询OpenAlex API获取机构信息，生成Excel文件

作者：AI助手
创建时间：2025-01-27
"""

import pandas as pd
import requests
import time
import os
from datetime import datetime
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hinton_affiliations_query.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HintonAffiliationsQuery:
    """Geoffrey Hinton机构信息查询类"""
    
    def __init__(self, csv_file_path, pdf_dir_path):
        """
        初始化查询器
        
        Args:
            csv_file_path (str): 输入CSV文件路径
            pdf_dir_path (str): PDF文件目录路径
        """
        self.csv_file_path = csv_file_path
        self.pdf_dir_path = pdf_dir_path
        self.base_url = "https://api.openalex.org/works"
        
        # 结果存储
        self.results = []
        
    def read_csv_data(self):
        """读取CSV文件数据"""
        try:
            logger.info(f"正在读取CSV文件: {self.csv_file_path}")
            df = pd.read_csv(self.csv_file_path, encoding='utf-8')
            logger.info(f"成功读取 {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"读取CSV文件失败: {e}")
            raise
    
    def filter_hinton_papers(self, df):
        """筛选Geoffrey Hinton作为作者的论文"""
        try:
            # 筛选包含Geoffrey Hinton的论文
            hinton_papers = df[df['Author'].str.contains('Hinton, Geoffrey', na=False)]
            logger.info(f"找到 {len(hinton_papers)} 篇Geoffrey Hinton的论文")
            return hinton_papers
        except Exception as e:
            logger.error(f"筛选论文失败: {e}")
            raise
    
    def query_openalex_by_doi(self, doi):
        """
        通过DOI查询OpenAlex API获取机构信息
        
        Args:
            doi (str): 论文DOI
            
        Returns:
            dict: 包含机构信息的字典
        """
        try:
            # 构建查询URL
            url = f"{self.base_url}?filter=doi:{doi}"
            
            logger.info(f"正在查询DOI: {doi}")
            
            # 发送请求
            headers = {
                'User-Agent': 'HintonAffiliationsQuery/1.0 (mailto:support@example.com)'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['results']:
                    work = data['results'][0]
                    
                    # 查找Geoffrey Hinton的机构信息
                    hinton_affiliations = []
                    
                    for author in work.get('authorships', []):
                        # 检查作者姓名是否匹配Geoffrey Hinton
                        author_name = author.get('author', {}).get('display_name', '')
                        if 'Geoffrey' in author_name and 'Hinton' in author_name:
                            # 提取机构信息
                            institutions = author.get('institutions', [])
                            for inst in institutions:
                                inst_name = inst.get('display_name', 'Unknown')
                                hinton_affiliations.append(inst_name)
                    
                    logger.info(f"找到 {len(hinton_affiliations)} 个机构信息")
                    return hinton_affiliations
                else:
                    logger.warning(f"未找到DOI {doi} 的相关信息")
                    return []
            else:
                logger.error(f"API请求失败，状态码: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"查询DOI {doi} 时出错: {e}")
            return []
    
    def get_pdf_link(self, doi):
        """
        根据DOI生成PDF文件链接
        
        Args:
            doi (str): 论文DOI
            
        Returns:
            str: PDF文件的绝对路径链接
        """
        try:
            # 将DOI转换为文件名格式
            pdf_filename = f"[{doi.replace('/', '_')}].pdf"
            pdf_path = os.path.join(self.pdf_dir_path, pdf_filename)
            
            # 检查文件是否存在
            if os.path.exists(pdf_path):
                # 返回file://协议的绝对路径
                absolute_path = os.path.abspath(pdf_path)
                return f"file://{absolute_path}"
            else:
                logger.warning(f"PDF文件不存在: {pdf_filename}")
                return "PDF文件未找到"
                
        except Exception as e:
            logger.error(f"生成PDF链接时出错: {e}")
            return "链接生成失败"
    
    def process_papers(self, hinton_papers):
        """处理Geoffrey Hinton的论文"""
        logger.info("开始处理论文数据...")
        
        for index, paper in hinton_papers.iterrows():
            try:
                # 提取基本信息
                author = paper.get('Author', '')
                title = paper.get('Title', '')
                doi = paper.get('DOI', '')
                pub_date = paper.get('Date', paper.get('Publication Year', ''))
                
                logger.info(f"处理第 {index+1} 篇论文: {title[:50]}...")
                
                # 查询机构信息
                affiliations = self.query_openalex_by_doi(doi)
                affiliations_str = " | ".join(affiliations) if affiliations else "机构信息未找到"
                
                # 生成PDF链接
                pdf_link = self.get_pdf_link(doi)
                
                # 存储结果
                result = {
                    '作者': author,
                    '标题': title,
                    'DOI': doi,
                    '发表日期': pub_date,
                    '机构': affiliations_str,
                    'PDF链接': pdf_link
                }
                
                self.results.append(result)
                
                # 为避免频繁请求，添加延迟
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"处理论文 {index} 时出错: {e}")
                continue
    
    def save_to_excel(self, output_file):
        """保存结果到Excel文件"""
        try:
            logger.info(f"正在保存结果到Excel文件: {output_file}")
            
            # 创建DataFrame
            df_results = pd.DataFrame(self.results)
            
            # 使用openpyxl引擎保存，支持超链接
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df_results.to_excel(writer, sheet_name='Hinton论文机构信息', index=False)
                
                # 获取工作表
                worksheet = writer.sheets['Hinton论文机构信息']
                
                # 调整列宽
                for column in worksheet.columns:
                    max_length = 0
                    column_name = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_name].width = adjusted_width
                
                # 添加超链接功能到PDF链接列
                pdf_col = 6  # PDF链接是第6列
                for row in range(2, len(self.results) + 2):  # 从第2行开始（跳过标题行）
                    cell = worksheet.cell(row=row, column=pdf_col)
                    if cell.value and cell.value.startswith('file://'):
                        cell.hyperlink = cell.value
                        cell.style = "Hyperlink"
            
            logger.info(f"成功保存 {len(self.results)} 条记录到Excel文件")
            
        except Exception as e:
            logger.error(f"保存Excel文件失败: {e}")
            raise
    
    def run(self, output_file):
        """执行完整的查询流程"""
        try:
            logger.info("=== Geoffrey Hinton机构信息查询开始 ===")
            
            # 1. 读取CSV数据
            df = self.read_csv_data()
            
            # 2. 筛选Geoffrey Hinton的论文
            hinton_papers = self.filter_hinton_papers(df)
            
            # 3. 处理论文数据
            self.process_papers(hinton_papers)
            
            # 4. 保存到Excel
            self.save_to_excel(output_file)
            
            logger.info("=== 查询完成 ===")
            logger.info(f"处理了 {len(self.results)} 篇论文")
            logger.info(f"结果已保存到: {output_file}")
            
        except Exception as e:
            logger.error(f"查询流程执行失败: {e}")
            raise

def main():
    """主函数"""
    try:
        # 文件路径配置
        csv_file = "data/raw/202507271930_Hinton_Papers_30_v2.csv"
        pdf_dir = "data/processed/doi_renamed_pdfs_improved"
        output_file = f"data/processed/Geoffrey_Hinton_机构信息_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # 检查文件路径
        if not os.path.exists(csv_file):
            logger.error(f"CSV文件不存在: {csv_file}")
            return
        
        if not os.path.exists(pdf_dir):
            logger.error(f"PDF目录不存在: {pdf_dir}")
            return
        
        # 创建查询器并执行
        query = HintonAffiliationsQuery(csv_file, pdf_dir)
        query.run(output_file)
        
        print(f"\n✅ 处理完成！")
        print(f"📊 结果文件: {output_file}")
        print(f"📋 处理论文数量: {len(query.results)}")
        
    except Exception as e:
        logger.error(f"主程序执行失败: {e}")
        print(f"❌ 执行失败: {e}")

if __name__ == "__main__":
    main() 