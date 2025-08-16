#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件路径调试工具

功能：查看Excel文件中J列的完整路径内容，诊断超链接问题
"""

import openpyxl
import os
from urllib.parse import quote, unquote

def debug_file_paths():
    """调试文件路径"""
    file_path = "projects/AI学术分析/智能整理/data/processed/Hinton_with_Affiliations_v5.xlsx"
    
    print("🔍 文件路径调试")
    print("=" * 60)
    
    workbook = openpyxl.load_workbook(file_path)
    worksheet = workbook.active
    
    # 查看前5行的完整路径
    for row in range(2, 7):  # 查看前5行数据
        cell = worksheet.cell(row=row, column=10)  # J列
        path_value = cell.value
        
        print(f"\n📄 第{row}行:")
        print(f"原始路径: {path_value}")
        print(f"文件存在: {os.path.exists(path_value) if path_value else 'N/A'}")
        
        if path_value:
            # 检查当前超链接
            if hasattr(cell, 'hyperlink') and cell.hyperlink:
                print(f"当前超链接: {cell.hyperlink.target}")
            
            # 测试不同的URL编码方式
            from pathlib import Path
            p = Path(path_value)
            
            print(f"pathlib.as_uri(): {p.as_uri()}")
            print(f"手动file://: file://{path_value}")
            
            # 检查文件名
            if os.path.exists(path_value):
                print(f"文件名: {os.path.basename(path_value)}")
            else:
                print("❌ 文件不存在")

if __name__ == "__main__":
    debug_file_paths() 