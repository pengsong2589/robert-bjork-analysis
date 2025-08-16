#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geoffrey Hinton机构信息查询脚本（最终版）
功能：从CSV文件中提取Geoffrey Hinton的论文，查询OpenAlex API获取机构信息，生成Excel文件

最终版特性：
1. 处理所有论文（不限制数量）
2. 修复DOI格式问题
3. 完整的机构信息提取
4. 优化的Excel输出格式
5. 自动备份功能

作者：AI助手
版本：3.0 - 最终版
创建时间：2025-01-27
"""

import pandas as pd
import requests
import time
import os
import shutil
from datetime import datetime
import logging
from pathlib import Path
import re

# 配置日志
log_filename = f"hinton_affiliations_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HintonAffiliationsFinalQuery:
    """Geoffrey Hinton机构信息查询类（最终版）"""
    
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
        self.stats = {
            'total_papers': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'api_errors': 0
        }
        
    def backup_existing_files(self):
        """备份现有的结果文件"""
        try:
            backup_dir = "data/backup"
            os.makedirs(backup_dir, exist_ok=True)
            
            # 查找现有的结果文件
            existing_files = list(Path("data/processed").glob("Geoffrey_Hinton_机构信息_*.xlsx"))
            
            for file_path in existing_files:
                backup_path = os.path.join(backup_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_path.name}")
                shutil.copy2(str(file_path), backup_path)
                logger.info(f"已备份文件: {file_path.name} -> {backup_path}")
                
        except Exception as e:
            logger.warning(f"备份文件时出错: {e}")
    
    def normalize_doi(self, doi):
        """
        标准化DOI格式
        将下划线格式的DOI转换为标准格式
        
        Args:
            doi (str): 原始DOI字符串
            
        Returns:
            str: 标准化后的DOI
        """
        if not doi:
            return ""
        
        # 移除可能的前缀和空格
        doi = doi.strip()
        if doi.startswith('doi:'):
            doi = doi[4:]
        if doi.startswith('DOI:'):
            doi = doi[4:]
        
        # 将第一个下划线转换为斜杠
        if '_' in doi and '/' not in doi:
            first_underscore = doi.find('_')
            if first_underscore > 0:
                doi = doi[:first_underscore] + '/' + doi[first_underscore+1:]
        
        return doi
    
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
            hinton_papers = df[df['Author'].str.contains('Hinton, Geoffrey', na=False)]
            self.stats['total_papers'] = len(hinton_papers)
            logger.info(f"找到 {len(hinton_papers)} 篇Geoffrey Hinton的论文")
            
            return hinton_papers
        except Exception as e:
            logger.error(f"筛选论文失败: {e}")
            raise
    
    def query_openalex_by_doi(self, original_doi):
        """
        通过DOI查询OpenAlex API获取机构信息
        
        Args:
            original_doi (str): 原始DOI
            
        Returns:
            dict: 包含机构信息和其他元数据的字典
        """
        try:
            # 标准化DOI
            doi = self.normalize_doi(original_doi)
            
            # 尝试多种查询方式
            query_urls = [
                f"{self.base_url}?filter=doi:{doi}",
                f"{self.base_url}?search={doi.replace('/', '%2F')}",
                f"{self.base_url}?filter=doi:https://doi.org/{doi}"
            ]
            
            logger.info(f"正在查询DOI: {original_doi} -> {doi}")
            
            # 发送请求头
            headers = {
                'User-Agent': 'HintonAffiliationsQuery/3.0 (academic-research@example.com)',
                'Accept': 'application/json'
            }
            
            for i, url in enumerate(query_urls):
                try:
                    response = requests.get(url, headers=headers, timeout=20)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('results'):
                            work = data['results'][0]
                            
                            # 提取基本信息
                            paper_info = {
                                'title': work.get('title', 'Unknown'),
                                'publication_year': work.get('publication_year'),
                                'publication_date': work.get('publication_date'),
                                'venue': '',
                                'citations_count': work.get('cited_by_count', 0)
                            }
                            
                            # 提取期刊/会议信息
                            if work.get('primary_location', {}).get('source'):
                                source = work['primary_location']['source']
                                paper_info['venue'] = source.get('display_name', '')
                            
                            # 查找Geoffrey Hinton的机构信息
                            hinton_affiliations = []
                            
                            for authorship in work.get('authorships', []):
                                author = authorship.get('author', {})
                                author_name = author.get('display_name', '')
                                
                                # 检查是否为Geoffrey Hinton
                                if self.is_hinton_author(author_name):
                                    logger.info(f"找到匹配作者: {author_name}")
                                    
                                    # 提取机构信息
                                    institutions = authorship.get('institutions', [])
                                    for inst in institutions:
                                        inst_name = inst.get('display_name', 'Unknown Institution')
                                        inst_country = inst.get('country_code', '')
                                        inst_type = inst.get('type', '')
                                        
                                        # 构建完整的机构信息
                                        full_inst_name = inst_name
                                        if inst_country:
                                            full_inst_name += f" ({inst_country})"
                                        
                                        hinton_affiliations.append({
                                            'name': inst_name,
                                            'full_name': full_inst_name,
                                            'country': inst_country,
                                            'type': inst_type
                                        })
                            
                            if hinton_affiliations:
                                logger.info(f"找到 {len(hinton_affiliations)} 个机构信息")
                                self.stats['successful_queries'] += 1
                                
                                return {
                                    'affiliations': hinton_affiliations,
                                    'paper_info': paper_info,
                                    'status': 'success'
                                }
                            else:
                                logger.warning(f"在论文中未找到Geoffrey Hinton的机构信息")
                                
                except requests.exceptions.RequestException as e:
                    logger.debug(f"查询方法 {i+1} 请求异常: {e}")
                    continue
                
                # 避免频繁请求
                time.sleep(0.5)
            
            self.stats['failed_queries'] += 1
            logger.warning(f"所有查询方法都未找到DOI {original_doi} 的相关信息")
            return {'status': 'not_found'}
                
        except Exception as e:
            self.stats['api_errors'] += 1
            logger.error(f"查询DOI {original_doi} 时出错: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def is_hinton_author(self, author_name):
        """判断作者是否为Geoffrey Hinton"""
        if not author_name:
            return False
        
        author_name_lower = author_name.lower()
        
        # 多种可能的姓名变体
        hinton_variants = [
            'geoffrey hinton',
            'geoffrey e. hinton',
            'geoffrey everest hinton',
            'g. hinton',
            'g.e. hinton',
            'hinton, geoffrey',
            'hinton, g',
            'hinton, g.',
            'hinton, g.e.'
        ]
        
        for variant in hinton_variants:
            if variant in author_name_lower:
                return True
        
        # 更宽泛的匹配：包含geoffrey和hinton
        return 'geoffrey' in author_name_lower and 'hinton' in author_name_lower
    
    def get_pdf_link(self, doi):
        """根据DOI生成PDF文件链接"""
        try:
            # 使用原始DOI格式（带下划线）作为文件名
            pdf_filename = f"[{doi}].pdf"
            pdf_path = os.path.join(self.pdf_dir_path, pdf_filename)
            
            if os.path.exists(pdf_path):
                absolute_path = os.path.abspath(pdf_path)
                return f"file://{absolute_path}"
            else:
                return "PDF文件未找到"
                
        except Exception as e:
            logger.error(f"生成PDF链接时出错: {e}")
            return "链接生成失败"
    
    def process_papers(self, hinton_papers):
        """处理Geoffrey Hinton的论文"""
        logger.info("开始处理所有论文数据...")
        
        for index, paper in hinton_papers.iterrows():
            try:
                # 提取基本信息
                author = paper.get('Author', '')
                title = paper.get('Title', '')
                doi = paper.get('DOI', '')
                pub_year = paper.get('Publication Year', '')
                pub_date = paper.get('Date', '')
                publication_title = paper.get('Publication Title', '')
                
                logger.info(f"处理第 {len(self.results)+1}/{self.stats['total_papers']} 篇论文: {title[:50]}...")
                
                # 查询机构信息
                query_result = self.query_openalex_by_doi(doi)
                
                # 处理查询结果
                if query_result['status'] == 'success':
                    affiliations = query_result['affiliations']
                    paper_info = query_result['paper_info']
                    
                    # 构建机构字符串
                    affiliations_str = " | ".join([aff['full_name'] for aff in affiliations])
                    
                    # 使用API返回的更准确信息（如果可用）
                    actual_pub_year = paper_info.get('publication_year') or pub_year
                    actual_venue = paper_info.get('venue') or publication_title
                    citations = paper_info.get('citations_count', 0)
                    
                else:
                    affiliations_str = "机构信息未找到"
                    actual_pub_year = pub_year
                    actual_venue = publication_title
                    citations = 0
                
                # 生成PDF链接
                pdf_link = self.get_pdf_link(doi)
                
                # 存储结果
                result = {
                    '作者': author,
                    '标题': title,
                    'DOI': doi,
                    '标准化DOI': self.normalize_doi(doi),
                    '发表年份': actual_pub_year,
                    '发表日期': pub_date,
                    '期刊/会议': actual_venue,
                    '引用次数': citations,
                    '机构': affiliations_str,
                    'PDF链接': pdf_link,
                    '查询状态': query_result['status']
                }
                
                self.results.append(result)
                
                # 每5篇论文打印一次进度
                if len(self.results) % 5 == 0:
                    logger.info(f"已处理 {len(self.results)}/{self.stats['total_papers']} 篇论文")
                
                # 为避免频繁请求，添加延迟
                time.sleep(1.5)
                
            except Exception as e:
                logger.error(f"处理论文 {index} 时出错: {e}")
                continue
    
    def save_to_excel(self, output_file):
        """保存结果到Excel文件"""
        try:
            logger.info(f"正在保存结果到Excel文件: {output_file}")
            
            if not self.results:
                logger.warning("没有结果可以保存")
                return
            
            # 创建DataFrame
            df_results = pd.DataFrame(self.results)
            
            # 使用openpyxl引擎保存
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 主数据表
                df_results.to_excel(writer, sheet_name='Hinton论文机构信息', index=False)
                
                # 统计信息表
                stats_data = {
                    '统计项目': ['论文总数', '成功查询', '查询失败', 'API错误', '成功率'],
                    '数值': [
                        self.stats['total_papers'],
                        self.stats['successful_queries'],
                        self.stats['failed_queries'],
                        self.stats['api_errors'],
                        f"{(self.stats['successful_queries']/self.stats['total_papers']*100):.1f}%" if self.stats['total_papers'] > 0 else "0%"
                    ]
                }
                df_stats = pd.DataFrame(stats_data)
                df_stats.to_excel(writer, sheet_name='统计信息', index=False)
                
                # 调整主表列宽
                worksheet = writer.sheets['Hinton论文机构信息']
                for column in worksheet.columns:
                    max_length = 0
                    column_name = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 80)
                    worksheet.column_dimensions[column_name].width = adjusted_width
                
                # 添加超链接功能到PDF链接列
                pdf_col = df_results.columns.get_loc('PDF链接') + 1
                for row in range(2, len(self.results) + 2):
                    cell = worksheet.cell(row=row, column=pdf_col)
                    if cell.value and cell.value.startswith('file://'):
                        cell.hyperlink = cell.value
                        cell.style = "Hyperlink"
            
            logger.info(f"成功保存 {len(self.results)} 条记录到Excel文件")
            
        except Exception as e:
            logger.error(f"保存Excel文件失败: {e}")
            raise
    
    def generate_summary_report(self):
        """生成总结报告"""
        try:
            # 统计不同机构的出现次数
            affiliations_count = {}
            
            for result in self.results:
                if result['查询状态'] == 'success':
                    affiliations = result['机构'].split(' | ')
                    for aff in affiliations:
                        # 提取机构名称（去除国家代码）
                        clean_aff = aff.split(' (')[0]
                        affiliations_count[clean_aff] = affiliations_count.get(clean_aff, 0) + 1
            
            # 按出现次数排序
            sorted_affiliations = sorted(affiliations_count.items(), key=lambda x: x[1], reverse=True)
            
            logger.info("\n=== 总结报告 ===")
            logger.info(f"论文总数: {self.stats['total_papers']}")
            logger.info(f"成功查询: {self.stats['successful_queries']}")
            logger.info(f"查询失败: {self.stats['failed_queries']}")
            logger.info(f"成功率: {(self.stats['successful_queries']/self.stats['total_papers']*100):.1f}%")
            
            logger.info("\n主要关联机构:")
            for aff, count in sorted_affiliations[:10]:
                logger.info(f"  {aff}: {count} 篇论文")
            
            return sorted_affiliations
            
        except Exception as e:
            logger.error(f"生成总结报告时出错: {e}")
            return []
    
    def run(self, output_file):
        """执行完整的查询流程"""
        try:
            logger.info("=== Geoffrey Hinton机构信息查询开始（最终版） ===")
            
            # 0. 备份现有文件
            self.backup_existing_files()
            
            # 1. 读取CSV数据
            df = self.read_csv_data()
            
            # 2. 筛选Geoffrey Hinton的论文
            hinton_papers = self.filter_hinton_papers(df)
            
            # 3. 处理论文数据
            self.process_papers(hinton_papers)
            
            # 4. 保存到Excel
            self.save_to_excel(output_file)
            
            # 5. 生成总结报告
            affiliations_summary = self.generate_summary_report()
            
            logger.info("=== 查询完成 ===")
            logger.info(f"结果已保存到: {output_file}")
            
            return affiliations_summary
            
        except Exception as e:
            logger.error(f"查询流程执行失败: {e}")
            raise

def main():
    """主函数"""
    try:
        # 文件路径配置
        csv_file = "data/raw/202507271930_Hinton_Papers_30_v2.csv"
        pdf_dir = "data/processed/doi_renamed_pdfs_improved"
        output_file = f"data/processed/Geoffrey_Hinton_机构信息_完整版_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # 检查文件路径
        if not os.path.exists(csv_file):
            logger.error(f"CSV文件不存在: {csv_file}")
            return
        
        if not os.path.exists(pdf_dir):
            logger.error(f"PDF目录不存在: {pdf_dir}")
            return
        
        # 创建查询器并执行
        query = HintonAffiliationsFinalQuery(csv_file, pdf_dir)
        affiliations_summary = query.run(output_file)
        
        print(f"\n✅ 处理完成！")
        print(f"📊 结果文件: {output_file}")
        print(f"📋 处理论文数量: {len(query.results)}")
        print(f"🎯 成功率: {(query.stats['successful_queries']/query.stats['total_papers']*100):.1f}%")
        
        # 显示主要机构信息
        if affiliations_summary:
            print(f"\n🏫 Geoffrey Hinton主要关联机构:")
            for i, (aff, count) in enumerate(affiliations_summary[:5]):
                print(f"  {i+1}. {aff}: {count} 篇论文")
        
    except Exception as e:
        logger.error(f"主程序执行失败: {e}")
        print(f"❌ 执行失败: {e}")

if __name__ == "__main__":
    main() 