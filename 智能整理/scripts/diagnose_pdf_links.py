#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF链接诊断和修复脚本
功能：诊断Excel中PDF链接无法点击的问题，并提供修复方案

作者：AI助手
创建时间：2025-01-27
"""

import pandas as pd
import os
import subprocess
import urllib.parse
from pathlib import Path
import platform

def diagnose_pdf_links():
    """诊断PDF链接问题"""
    
    print("🔍 开始诊断PDF链接问题...")
    
    # 1. 检查Excel文件
    excel_file = "data/processed/Geoffrey_Hinton_机构信息_完整版_20250727_111757.xlsx"
    if not os.path.exists(excel_file):
        print(f"❌ Excel文件不存在: {excel_file}")
        return
    
    print(f"✅ Excel文件存在: {excel_file}")
    
    # 2. 读取Excel数据
    try:
        df = pd.read_excel(excel_file, sheet_name='Hinton论文机构信息')
        print(f"✅ 成功读取Excel数据，共 {len(df)} 行")
    except Exception as e:
        print(f"❌ 读取Excel失败: {e}")
        return
    
    # 3. 检查PDF链接列
    if 'PDF链接' not in df.columns:
        print("❌ 未找到PDF链接列")
        return
    
    print("✅ 找到PDF链接列")
    
    # 4. 分析PDF链接
    pdf_links = df['PDF链接'].dropna()
    print(f"📊 PDF链接统计:")
    print(f"   - 总链接数: {len(pdf_links)}")
    
    # 统计链接类型
    file_links = pdf_links[pdf_links.str.startswith('file://', na=False)]
    not_found_links = pdf_links[pdf_links.str.contains('PDF文件未找到', na=False)]
    error_links = pdf_links[pdf_links.str.contains('链接生成失败', na=False)]
    
    print(f"   - file:// 链接: {len(file_links)}")
    print(f"   - 文件未找到: {len(not_found_links)}")
    print(f"   - 链接生成失败: {len(error_links)}")
    
    # 5. 测试几个链接
    print("\n🧪 测试PDF链接...")
    
    test_count = 0
    for i, link in enumerate(file_links.head(3)):
        test_count += 1
        print(f"\n测试 {test_count}: {df.iloc[i]['标题'][:30]}...")
        print(f"   链接: {link}")
        
        # 提取文件路径
        if link.startswith('file://'):
            file_path = link[7:]  # 移除 'file://'
            print(f"   文件路径: {file_path}")
            
            # 检查文件是否存在
            if os.path.exists(file_path):
                print("   ✅ 文件存在")
                
                # 尝试用系统默认程序打开（仅作测试，不实际执行）
                system = platform.system()
                if system == "Darwin":  # macOS
                    cmd = f'open "{file_path}"'
                elif system == "Windows":
                    cmd = f'start "" "{file_path}"'
                else:  # Linux
                    cmd = f'xdg-open "{file_path}"'
                
                print(f"   建议命令: {cmd}")
            else:
                print("   ❌ 文件不存在")
    
    # 6. 检查可能的问题
    print("\n🔧 问题诊断:")
    
    # 检查路径中的特殊字符
    special_chars_found = False
    for link in file_links.head(5):
        if link.startswith('file://'):
            path = link[7:]
            if any(char in path for char in [' ', '(', ')', '[', ']', '中', '文']):
                if not special_chars_found:
                    print("   ⚠️  路径中包含特殊字符，可能需要URL编码")
                    special_chars_found = True
                break
    
    # 检查Excel版本兼容性
    print("   ℹ️  Excel中file://链接的常见问题:")
    print("      - macOS上Excel可能不支持file://协议")
    print("      - 路径中的特殊字符需要URL编码")
    print("      - 某些Excel版本需要相对路径而非绝对路径")
    
    return df

def create_fixed_excel():
    """创建修复后的Excel文件"""
    
    print("\n🛠️  创建修复版Excel文件...")
    
    # 读取原始数据
    excel_file = "data/processed/Geoffrey_Hinton_机构信息_完整版_20250727_111757.xlsx"
    df = pd.read_excel(excel_file, sheet_name='Hinton论文机构信息')
    
    # 创建修复后的PDF链接
    def fix_pdf_link(row):
        original_link = row['PDF链接']
        doi = row['DOI']
        
        if pd.isna(original_link) or 'file://' not in str(original_link):
            return original_link
        
        # 提取文件路径
        file_path = str(original_link)[7:]  # 移除 'file://'
        
        if os.path.exists(file_path):
            # 方案1: URL编码的file://链接
            encoded_path = urllib.parse.quote(file_path, safe='/:')
            url_encoded_link = f'file://{encoded_path}'
            
            # 方案2: 相对路径链接
            try:
                current_dir = os.path.dirname(os.path.abspath(excel_file))
                rel_path = os.path.relpath(file_path, current_dir)
                relative_link = rel_path
            except:
                relative_link = file_path
            
            # 方案3: macOS专用链接格式
            macos_link = f'file://localhost{file_path}'
            
            return {
                'original': original_link,
                'url_encoded': url_encoded_link,
                'relative': relative_link,
                'macos': macos_link,
                'raw_path': file_path
            }
        else:
            return original_link
    
    # 应用修复
    print("   正在生成多种链接格式...")
    
    # 创建多个版本的链接
    df_fixed = df.copy()
    
    # 添加多种链接格式列
    df_fixed['PDF链接_URL编码'] = ''
    df_fixed['PDF链接_相对路径'] = ''
    df_fixed['PDF链接_macOS格式'] = ''
    df_fixed['PDF文件绝对路径'] = ''
    
    for i, row in df_fixed.iterrows():
        fixed_result = fix_pdf_link(row)
        
        if isinstance(fixed_result, dict):
            df_fixed.loc[i, 'PDF链接_URL编码'] = fixed_result['url_encoded']
            df_fixed.loc[i, 'PDF链接_相对路径'] = fixed_result['relative']
            df_fixed.loc[i, 'PDF链接_macOS格式'] = fixed_result['macos']
            df_fixed.loc[i, 'PDF文件绝对路径'] = fixed_result['raw_path']
    
    # 保存修复后的文件
    output_file = "data/processed/Geoffrey_Hinton_机构信息_链接修复版_20250727.xlsx"
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 主数据表
        df_fixed.to_excel(writer, sheet_name='Hinton论文机构信息_修复版', index=False)
        
        # 使用说明表
        instructions = pd.DataFrame({
            '链接类型': [
                'PDF链接（原始）',
                'PDF链接_URL编码',
                'PDF链接_相对路径',
                'PDF链接_macOS格式',
                'PDF文件绝对路径'
            ],
            '说明': [
                '原始file://链接，可能在某些Excel版本中无法使用',
                'URL编码后的file://链接，解决特殊字符问题',
                '相对路径，适用于文件和Excel在同一项目中',
                'macOS专用格式，包含localhost前缀',
                '纯文件路径，可复制粘贴到文件管理器'
            ],
            '推荐使用': [
                '❌',
                '⭐⭐⭐',
                '⭐⭐',
                '⭐⭐⭐ (仅macOS)',
                '⭐'
            ]
        })
        instructions.to_excel(writer, sheet_name='使用说明', index=False)
    
    print(f"✅ 修复版Excel已保存: {output_file}")
    return output_file

def test_pdf_opening():
    """测试PDF文件打开功能"""
    
    print("\n🧪 测试PDF文件打开...")
    
    # 找一个PDF文件进行测试
    pdf_dir = "data/processed/doi_renamed_pdfs_improved"
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ 未找到PDF文件")
        return
    
    test_pdf = os.path.join(pdf_dir, pdf_files[0])
    print(f"测试文件: {test_pdf}")
    
    if os.path.exists(test_pdf):
        print("✅ 测试文件存在")
        
        # 生成各种链接格式
        abs_path = os.path.abspath(test_pdf)
        
        print(f"\n📋 该文件的各种链接格式:")
        print(f"1. 绝对路径: {abs_path}")
        print(f"2. file://链接: file://{abs_path}")
        print(f"3. URL编码链接: file://{urllib.parse.quote(abs_path, safe='/:')}")
        print(f"4. macOS格式: file://localhost{abs_path}")
        
        # 提供手动测试建议
        print(f"\n💡 手动测试建议:")
        print(f"1. 在终端中运行: open \"{abs_path}\"")
        print(f"2. 在Finder中导航到目录并双击文件")
        print(f"3. 在浏览器地址栏中输入: file://{abs_path}")
        
    else:
        print("❌ 测试文件不存在")

def main():
    """主函数"""
    print("🔧 PDF链接诊断和修复工具")
    print("=" * 50)
    
    # 1. 诊断问题
    df = diagnose_pdf_links()
    
    if df is not None:
        # 2. 创建修复版本
        fixed_file = create_fixed_excel()
        
        # 3. 测试PDF打开
        test_pdf_opening()
        
        # 4. 提供解决方案
        print("\n🎯 解决方案建议:")
        print("1. 使用修复版Excel文件中的'PDF链接_URL编码'列")
        print("2. 如果仍无法点击，尝试复制'PDF文件绝对路径'到文件管理器")
        print("3. 在macOS上，推荐使用'PDF链接_macOS格式'列")
        print("4. 也可以直接在终端使用 open 命令打开文件")
        
        print(f"\n📁 修复后的文件: {fixed_file}")

if __name__ == "__main__":
    main() 