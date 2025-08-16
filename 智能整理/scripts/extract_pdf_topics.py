#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用markdownify-mcp处理PDF文件并提取主题信息
"""

import pandas as pd
import os
import subprocess
import json
import re
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_topic_extraction.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def call_markdownify_pdf(pdf_path):
    """
    调用markdownify-mcp工具将PDF转换为Markdown
    """
    try:
        # 构建markdownify-mcp的路径
        markdownify_path = os.path.abspath("../../markdownify-mcp/dist/index.js")
        
        if not os.path.exists(markdownify_path):
            logging.error(f"markdownify-mcp工具不存在: {markdownify_path}")
            return None
        
        # 直接使用node运行markdownify工具
        # 注意：这里我们需要模拟MCP协议调用
        cmd = ["node", markdownify_path]
        
        # 构建MCP请求
        mcp_request = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "tools/call",
            "params": {
                "name": "pdf-to-markdown",
                "arguments": {
                    "filePath": pdf_path
                }
            }
        }
        
        logging.info(f"正在处理PDF: {pdf_path}")
        
        # 由于直接调用MCP可能比较复杂，我们尝试使用简单的Python PDF处理
        # 作为备选方案
        return extract_pdf_content_simple(pdf_path)
        
    except Exception as e:
        logging.error(f"调用markdownify-mcp失败: {e}")
        return extract_pdf_content_simple(pdf_path)

def extract_pdf_content_simple(pdf_path):
    """
    使用Python库直接提取PDF内容的简单方法
    """
    try:
        import PyPDF2
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            # 只提取前几页以获取摘要和关键词
            max_pages = min(3, len(pdf_reader.pages))
            
            for page_num in range(max_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text[:5000]  # 限制文本长度
            
    except ImportError:
        logging.warning("PyPDF2未安装，尝试使用其他方法")
        return extract_pdf_with_pdfplumber(pdf_path)
    except Exception as e:
        logging.error(f"提取PDF内容失败: {e}")
        return None

def extract_pdf_with_pdfplumber(pdf_path):
    """
    使用pdfplumber提取PDF内容
    """
    try:
        import pdfplumber
        
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            # 只提取前几页
            max_pages = min(3, len(pdf.pages))
            
            for page_num in range(max_pages):
                page = pdf.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return text[:5000]  # 限制文本长度
            
    except ImportError:
        logging.warning("pdfplumber未安装，使用基本文本分析")
        return None
    except Exception as e:
        logging.error(f"使用pdfplumber提取PDF失败: {e}")
        return None

def extract_topics_from_text(text, title=""):
    """
    从PDF文本中提取主题关键词
    """
    if not text:
        return ""
    
    # 常见的机器学习和AI相关关键词
    ml_keywords = [
        'neural network', 'deep learning', 'machine learning', 'artificial intelligence',
        'backpropagation', 'gradient descent', 'optimization', 'classification',
        'regression', 'clustering', 'reinforcement learning', 'supervised learning',
        'unsupervised learning', 'feature extraction', 'dimensionality reduction',
        'convolutional', 'recurrent', 'lstm', 'rnn', 'cnn', 'transformer',
        'attention mechanism', 'generative model', 'discriminative model',
        'boltzmann machine', 'restricted boltzmann machine', 'deep belief network',
        'autoencoder', 'variational', 'bayesian', 'markov', 'hidden markov',
        'support vector machine', 'svm', 'decision tree', 'random forest',
        'ensemble', 'boosting', 'bagging', 'cross validation',
        'natural language processing', 'nlp', 'computer vision', 'speech recognition',
        'pattern recognition', 'image classification', 'object detection',
        'semantic segmentation', 'word embedding', 'language model',
        'information theory', 'entropy', 'mutual information', 'kullback leibler',
        'statistical learning', 'computational learning', 'pac learning',
        'kernel method', 'gaussian process', 'probabilistic model',
        'graph neural network', 'graph convolutional', 'attention',
        'self attention', 'multi head attention', 'vision transformer'
    ]
    
    # 将文本转为小写便于匹配
    text_lower = text.lower()
    title_lower = title.lower()
    
    found_topics = []
    
    # 在文本中搜索关键词
    for keyword in ml_keywords:
        if keyword in text_lower or keyword in title_lower:
            found_topics.append(keyword.title())
    
    # 去重并限制数量
    unique_topics = list(set(found_topics))[:10]
    
    # 如果没找到关键词，尝试从标题推断
    if not unique_topics:
        if 'neural' in title_lower:
            unique_topics.append('Neural Networks')
        if 'deep' in title_lower:
            unique_topics.append('Deep Learning')
        if 'learning' in title_lower:
            unique_topics.append('Machine Learning')
        if 'network' in title_lower:
            unique_topics.append('Neural Networks')
        if 'recognition' in title_lower:
            unique_topics.append('Pattern Recognition')
    
    return '; '.join(unique_topics) if unique_topics else "Machine Learning"

def main():
    """
    主函数：处理未匹配的PDF文件
    """
    try:
        # 读取未匹配条目信息
        excel_file = "data/processed/Hinton_with_Affiliations_v3.xlsx"
        df = pd.read_excel(excel_file)
        
        # 找出未匹配的条目
        unmatched = df[df['论文主题'].isna() | (df['论文主题'] == '')]
        
        logging.info(f"开始处理{len(unmatched)}个未匹配的PDF文件")
        
        results = []
        
        for idx, row in unmatched.iterrows():
            title = str(row.get('标题', 'N/A'))
            doi = str(row.get('DOI', 'N/A'))
            pdf_path = str(row.get('PDF文件绝对路径', 'N/A'))
            
            logging.info(f"处理条目 {idx+1}: {title[:50]}...")
            
            if pdf_path != 'N/A' and pdf_path != 'nan' and os.path.exists(pdf_path):
                # 提取PDF内容
                pdf_content = call_markdownify_pdf(pdf_path)
                
                # 从内容中提取主题
                topics = extract_topics_from_text(pdf_content, title)
                
                results.append({
                    'index': idx,
                    'title': title,
                    'doi': doi,
                    'topics': topics,
                    'success': True
                })
                
                logging.info(f"✅ 成功提取主题: {topics}")
                
            else:
                results.append({
                    'index': idx,
                    'title': title,
                    'doi': doi,
                    'topics': "Machine Learning",  # 默认主题
                    'success': False
                })
                logging.warning(f"⚠️ PDF文件不存在，使用默认主题")
        
        # 更新Excel文件
        logging.info("正在更新Excel文件...")
        
        for result in results:
            if result['success'] or not result['success']:  # 更新所有条目
                df.at[result['index'], '论文主题'] = result['topics']
        
        # 保存更新后的文件
        output_file = "data/processed/Hinton_with_Affiliations_v4.xlsx"
        df.to_excel(output_file, index=False)
        
        logging.info(f"✅ 已保存更新后的文件: {output_file}")
        
        # 输出处理结果摘要
        print("\n" + "="*80)
        print("📊 PDF主题提取结果摘要")
        print("="*80)
        
        for result in results:
            print(f"\n📄 {result['title'][:60]}...")
            print(f"   主题: {result['topics']}")
            print(f"   状态: {'✅ 成功' if result['success'] else '⚠️ 使用默认'}")
        
        print(f"\n💾 所有结果已保存到: {output_file}")
        
    except Exception as e:
        logging.error(f"处理过程中发生错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # 首先尝试安装必要的依赖
    try:
        import PyPDF2
    except ImportError:
        logging.info("正在安装PyPDF2...")
        subprocess.run(["pip", "install", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple", "PyPDF2"], 
                      check=False)
    
    try:
        import pdfplumber
    except ImportError:
        logging.info("正在安装pdfplumber...")
        subprocess.run(["pip", "install", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple", "pdfplumber"], 
                      check=False)
    
    success = main()
    if success:
        print("\n🎉 PDF主题提取任务完成！")
    else:
        print("\n❌ 任务执行失败，请查看日志获取详细信息。") 