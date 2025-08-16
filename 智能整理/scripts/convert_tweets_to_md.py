#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter CSV转Markdown文件处理脚本

功能说明：
1. 读取CSV文件中的tweet数据
2. 将每条tweet的full_text内容生成独立的markdown文件
3. 根据created_at时间戳生成文件名（格式：YYYY-MM-DD-HH-MM-SS.md）
4. 处理重复时间戳问题（添加序号后缀）
5. 生成Excel索引文件，包含md_file列记录对应的markdown文件路径

作者：AI助手
创建日期：2025-01-27
"""

import csv
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
import re
from collections import defaultdict


def parse_twitter_timestamp(timestamp_str):
    """
    解析Twitter时间戳格式转换为Python datetime对象
    
    参数:
        timestamp_str (str): Twitter格式时间戳，如 "Sun Jun 08 10:58:10 +0000 2025"
    
    返回:
        datetime: 解析后的datetime对象
    """
    try:
        # Twitter时间戳格式：'Sun Jun 08 10:58:10 +0000 2025'
        # 转换为datetime对象
        dt = datetime.strptime(timestamp_str, '%a %b %d %H:%M:%S %z %Y')
        return dt
    except ValueError as e:
        print(f"时间戳解析错误: {timestamp_str}, 错误: {e}")
        return None


def datetime_to_filename(dt):
    """
    将datetime对象转换为文件名格式
    
    参数:
        dt (datetime): datetime对象
    
    返回:
        str: 格式化的文件名（不含扩展名），如 "2025-06-08-10-58-10"
    """
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d-%H-%M-%S')


def sanitize_text_for_markdown(text):
    """
    清理文本内容，使其适合保存为markdown文件
    
    参数:
        text (str): 原始文本内容
    
    返回:
        str: 清理后的文本内容
    """
    if not text or pd.isna(text):
        return ""
    
    # 处理HTML实体编码
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    
    # 移除多余的空白字符，但保留换行
    text = re.sub(r'\n\s*\n', '\n\n', text)  # 多个连续换行变为双换行
    text = text.strip()
    
    return text


def generate_unique_filename(base_filename, used_filenames):
    """
    生成唯一的文件名，处理重复时间戳的情况
    
    参数:
        base_filename (str): 基础文件名（不含扩展名）
        used_filenames (set): 已使用的文件名集合
    
    返回:
        str: 唯一的文件名（含.md扩展名）
    """
    if base_filename is None:
        # 如果时间戳解析失败，使用默认命名
        base_filename = "unknown-timestamp"
    
    md_filename = f"{base_filename}.md"
    
    # 如果文件名已存在，添加序号后缀
    counter = 1
    while md_filename in used_filenames:
        md_filename = f"{base_filename}-{counter}.md"
        counter += 1
    
    used_filenames.add(md_filename)
    return md_filename


def create_excel_with_hyperlinks(df, excel_file_path):
    """
    创建带超链接的Excel文件
    
    参数:
        df (pandas.DataFrame): 包含数据的DataFrame
        excel_file_path (str): Excel文件输出路径
    """
    try:
        import xlsxwriter
        
        # 创建workbook和worksheet
        workbook = xlsxwriter.Workbook(excel_file_path)
        worksheet = workbook.add_worksheet('Tweets')
        
        # 设置格式
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1
        })
        
        link_format = workbook.add_format({
            'color': 'blue',
            'underline': 1
        })
        
        # 写入表头
        for col_num, column_name in enumerate(df.columns):
            worksheet.write(0, col_num, column_name, header_format)
        
        # 写入数据
        for row_num, (index, row) in enumerate(df.iterrows(), 1):
            for col_num, column_name in enumerate(df.columns):
                value = row[column_name]
                
                # 如果是md_file列，创建超链接
                if column_name == 'md_file' and pd.notna(value) and value:
                    # 创建本地文件的绝对路径URL，不进行URL编码以避免中文路径问题
                    md_file_full_path = os.path.join(os.path.dirname(excel_file_path), value)
                    # 使用绝对路径创建file://协议的URL，保持中文字符不变
                    file_url = f"file:///{md_file_full_path.replace(os.sep, '/')}"
                    worksheet.write_url(row_num, col_num, file_url, link_format, value)
                else:
                    # 处理其他数据类型
                    if pd.isna(value):
                        worksheet.write(row_num, col_num, '')
                    else:
                        worksheet.write(row_num, col_num, str(value))
        
        # 调整列宽
        worksheet.set_column('A:Z', 15)  # 设置基本列宽
        worksheet.set_column('D:D', 50)  # full_text列设置更宽
        worksheet.set_column('Z:Z', 25)  # md_file列设置适中宽度
        
        workbook.close()
        print(f"✓ 成功创建带超链接的Excel文件")
        
    except ImportError:
        # 如果xlsxwriter不可用，回退到openpyxl
        print("使用openpyxl作为备选方案...")
        df.to_excel(excel_file_path, index=False, engine='openpyxl')
        print("⚠ Excel文件已创建，但md_file列为普通文本（需要xlsxwriter支持超链接）")


def process_csv_to_markdown(csv_file_path, output_dir):
    """
    主处理函数：将CSV文件转换为markdown文件并生成Excel索引
    
    参数:
        csv_file_path (str): 输入CSV文件路径
        output_dir (str): 输出目录路径
    
    返回:
        tuple: (成功处理的记录数, 总记录数)
    """
    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 读取CSV文件
    print(f"正在读取CSV文件: {csv_file_path}")
    df = pd.read_csv(csv_file_path)
    
    total_records = len(df)
    processed_records = 0
    used_filenames = set()
    
    # 为DataFrame添加md_file列
    df['md_file'] = ''
    
    print(f"共找到 {total_records} 条记录，开始处理...")
    
    # 遍历每条记录
    for index, row in df.iterrows():
        try:
            # 解析时间戳
            created_at = row['created_at']
            dt = parse_twitter_timestamp(created_at)
            
            # 生成基础文件名
            base_filename = datetime_to_filename(dt)
            
            # 生成唯一文件名
            md_filename = generate_unique_filename(base_filename, used_filenames)
            
            # 获取tweet内容
            full_text = sanitize_text_for_markdown(row['full_text'])
            
            # 创建markdown文件路径
            md_file_path = os.path.join(output_dir, md_filename)
            
            # 写入markdown文件
            with open(md_file_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            # 更新DataFrame中的md_file列
            df.at[index, 'md_file'] = md_filename
            
            processed_records += 1
            
            # 显示进度
            if processed_records % 10 == 0 or processed_records == total_records:
                print(f"已处理: {processed_records}/{total_records} 条记录")
                
        except Exception as e:
            print(f"处理第 {index+1} 条记录时出错: {e}")
            # 即使出错也要记录一个占位符文件名
            df.at[index, 'md_file'] = f"error-record-{index+1}.md"
    
    # 生成Excel索引文件
    excel_file_path = os.path.join(output_dir, 'tweets_with_md.xlsx')
    print(f"正在生成Excel索引文件: {excel_file_path}")
    
    # 使用xlsxwriter引擎来创建带超链接的Excel文件
    try:
        # 先尝试使用xlsxwriter创建超链接
        create_excel_with_hyperlinks(df, excel_file_path)
    except ImportError:
        print("xlsxwriter未安装，正在安装...")
        import subprocess
        subprocess.check_call(['pip', 'install', '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple', 'xlsxwriter'])
        # 重新导入并创建
        create_excel_with_hyperlinks(df, excel_file_path)
    
    print(f"处理完成！")
    print(f"- 成功处理: {processed_records}/{total_records} 条记录")
    print(f"- Markdown文件保存在: {output_dir}")
    print(f"- Excel索引文件: {excel_file_path}")
    
    return processed_records, total_records


def main():
    """
    主函数：设置路径并执行处理
    """
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # 设置输入和输出路径
    csv_file_path = project_root / "data" / "raw" / "dataset_twitter-Hinton-tweets-scraper_2025-07-27.csv"
    output_dir = project_root / "data" / "processed" / "tweets_md"
    
    print("=" * 60)
    print("Twitter CSV 转 Markdown 文件处理工具")
    print("=" * 60)
    print(f"输入文件: {csv_file_path}")
    print(f"输出目录: {output_dir}")
    print("=" * 60)
    
    # 检查输入文件是否存在
    if not csv_file_path.exists():
        print(f"错误：输入文件不存在 - {csv_file_path}")
        return
    
    try:
        # 执行处理
        processed, total = process_csv_to_markdown(str(csv_file_path), str(output_dir))
        
        print("=" * 60)
        print("处理结果统计：")
        print(f"- 总记录数: {total}")
        print(f"- 成功处理: {processed}")
        print(f"- 失败记录: {total - processed}")
        print("=" * 60)
        
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 