#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter CSV转Markdown脚本
将CSV文件中的每行Twitter数据转换为独立的Markdown文档

作者: AI助手
创建时间: 2025年1月27日
功能: 
- 读取Twitter CSV数据
- 转换时间格式为中文
- 使用KeyBERT提取关键词
- 生成YAML前置数据
- 创建独立的Markdown文件
"""

import pandas as pd
import os
import re
from datetime import datetime
from keybert import KeyBERT
import html
import warnings
warnings.filterwarnings("ignore")

def chinese_numbers(num):
    """将阿拉伯数字转换为中文数字"""
    chinese_num_map = {
        '0': '零', '1': '一', '2': '二', '3': '三', '4': '四',
        '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'
    }
    return ''.join(chinese_num_map.get(c, c) for c in str(num))

def convert_time_to_chinese(time_str):
    """
    将英文时间转换为中文格式
    输入: "Sun Jun 08 10:58:10 +0000 2025"
    输出: 时间元组 (中文日期, uin格式)
    """
    try:
        # 解析时间
        dt = datetime.strptime(time_str, "%a %b %d %H:%M:%S +0000 %Y")
        
        # 生成中文日期
        year = chinese_numbers(dt.year)
        month = chinese_numbers(dt.month)
        day = chinese_numbers(dt.day)
        hour = chinese_numbers(dt.hour)
        minute = chinese_numbers(dt.minute)
        
        chinese_date = f"{year}年{month}月{day}日 {hour}点{minute}分"
        
        # 生成uin格式: YYYYMMDDHHMMSS
        uin = dt.strftime("%Y%m%d%H%M%S")
        
        return chinese_date, uin
    except Exception as e:
        print(f"时间转换错误: {time_str} - {e}")
        return "时间解析失败", "19700101000000"

def extract_keywords(text, kw_model, max_keywords=5):
    """使用KeyBERT提取关键词"""
    try:
        # 清理文本
        clean_text = html.unescape(text)
        clean_text = re.sub(r'http[s]?://\S+', '', clean_text)  # 移除URL
        clean_text = re.sub(r'@\w+', '', clean_text)  # 移除用户提及
        clean_text = re.sub(r'#\w+', '', clean_text)  # 移除标签
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()  # 规范化空白字符
        
        if len(clean_text) < 10:  # 文本太短
            return []
            
        # 提取关键词
        keywords = kw_model.extract_keywords(clean_text, 
                                           keyphrase_ngram_range=(1, 2), 
                                           stop_words='english')[:max_keywords]
        
        return [kw[0] for kw in keywords]
    except Exception as e:
        print(f"关键词提取错误: {e}")
        return []

def determine_category(text, hashtags=""):
    """根据推文内容推断分类"""
    text_lower = text.lower()
    hashtags_lower = str(hashtags).lower()
    
    # AI相关关键词
    if any(word in text_lower for word in ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural', 'gpt', 'openai']):
        return "AI技术"
    
    # 学术相关
    if any(word in text_lower for word in ['paper', 'research', 'study', 'university', 'conference', 'publication']):
        return "学术研究"
    
    # 观点评论
    if any(word in text_lower for word in ['think', 'believe', 'opinion', 'view', 'should', 'must']):
        return "观点评论"
    
    # 新闻事件
    if any(word in text_lower for word in ['news', 'announcement', 'launch', 'report', 'breaking']):
        return "新闻动态"
    
    # 默认分类
    return "其他推文"

def create_excerpt(text, max_length=50):
    """创建摘要，提取前N个字符"""
    # 清理HTML实体和特殊字符
    clean_text = html.unescape(text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # 截取指定长度
    if len(clean_text) <= max_length:
        return f'"{clean_text}"'
    else:
        return f'"{clean_text[:max_length]}..."'

def create_markdown_content(row, kw_model):
    """为单行数据创建Markdown内容"""
    try:
        # 提取基本信息
        full_text = str(row['full_text'])
        created_at = str(row['created_at'])
        hashtags = str(row.get('hashtags', ''))
        
        # 转换时间
        chinese_date, uin = convert_time_to_chinese(created_at)
        
        # 创建摘要
        excerpt = create_excerpt(full_text)
        
        # 推断分类
        category = determine_category(full_text, hashtags)
        
        # 提取关键词
        keywords = extract_keywords(full_text, kw_model)
        keywords_str = str(keywords).replace("'", '"')
        
        # 构建YAML前置数据
        yaml_front_matter = f"""---
title: {chinese_date}
excerpt: {excerpt}
layout: defult
category: {category}
keywords: {keywords_str}
source: [X@geoffreyhinton]
uin: {uin}
---

"""
        
        # 构建正文内容
        content = f"""## 推文内容

{full_text}

## 推文统计

- 点赞数: {row.get('favorite_count', 0)}
- 转发数: {row.get('retweet_count', 0)}
- 回复数: {row.get('reply_count', 0)}
- 收藏数: {row.get('bookmark_count', 0)}
- 浏览量: {row.get('view_count', 0)}

## 推文链接

[查看原推文]({row.get('url', '')})

## 发布信息

- 发布时间: {created_at}
- 推文ID: {row.get('id', '')}
- 语言: {row.get('lang', '')}
- 来源: {row.get('source', '')}
"""
        
        return yaml_front_matter + content, uin
        
    except Exception as e:
        print(f"创建Markdown内容时出错: {e}")
        return None, None

def main():
    """主函数"""
    print("开始转换Twitter CSV文件到Markdown...")
    
    # 文件路径
    csv_file = "data/raw/dataset_twitter-Hinton-tweets-scraper_2025-07-27.csv"
    output_dir = "data/processed/tweets_md_v2"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 读取CSV文件
        print(f"正在读取CSV文件: {csv_file}")
        df = pd.read_csv(csv_file)
        print(f"共找到 {len(df)} 条推文数据")
        
        # 初始化KeyBERT模型
        print("正在初始化KeyBERT模型...")
        kw_model = KeyBERT()
        print("KeyBERT模型初始化完成")
        
        # 处理每行数据
        successful_count = 0
        failed_count = 0
        
        for index, row in df.iterrows():
            try:
                print(f"正在处理第 {index + 1}/{len(df)} 条推文...")
                
                # 创建Markdown内容
                markdown_content, uin = create_markdown_content(row, kw_model)
                
                if markdown_content and uin:
                    # 创建文件名
                    filename = f"{uin}.md"
                    filepath = os.path.join(output_dir, filename)
                    
                    # 写入文件
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                    
                    print(f"成功创建: {filename}")
                    successful_count += 1
                else:
                    print(f"第 {index + 1} 条推文处理失败")
                    failed_count += 1
                    
            except Exception as e:
                print(f"处理第 {index + 1} 条推文时出错: {e}")
                failed_count += 1
                continue
        
        # 输出统计信息
        print(f"\n转换完成!")
        print(f"成功处理: {successful_count} 个文件")
        print(f"处理失败: {failed_count} 个文件")
        print(f"输出目录: {output_dir}")
        
        # 创建处理日志
        log_content = f"""# Twitter CSV转Markdown处理日志

## 处理统计
- 处理时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
- 输入文件: {csv_file}
- 输出目录: {output_dir}
- 总推文数: {len(df)}
- 成功处理: {successful_count}
- 处理失败: {failed_count}

## 处理说明
- 时间格式已转换为中文格式
- 摘要自动截取前50字符
- 关键词通过KeyBERT自动提取
- 分类根据推文内容自动推断
- 每个推文生成独立的Markdown文件

## 生成的字段说明
- title: 中文时间格式
- excerpt: 推文摘要（前50字符）
- layout: 固定为 "defult"
- category: 根据内容推断的分类
- keywords: KeyBERT提取的关键词列表
- source: 固定为 [X@geoffreyhinton]
- uin: 基于时间的唯一编码（YYYYMMDDHHMMSS）
"""
        
        log_file = os.path.join(output_dir, "转换日志.md")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(log_content)
        
        print(f"日志文件已保存: {log_file}")
        
    except Exception as e:
        print(f"程序执行出错: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 