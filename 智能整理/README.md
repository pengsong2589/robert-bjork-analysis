# AI学术分析 - 智能整理项目

## 📋 项目简介

本项目是AI学术分析课程的实践项目，主要用于学术文献的智能整理、去重、分组和元数据完善。通过结合Zotero文献管理工具与AI技术，实现学术研究的自动化处理流程。

## 🏗️ 项目结构

```
/Users/tommy/Projects/projects/AI学术分析/智能整理/
├── README.md                 # 项目说明文档
├── Ch03学术整理·实操演示.md    # 课程实操演示记录
├── W3基础作业.md              # 基础作业文档
├── data/                     # 数据存储目录
│   ├── raw/                  # 原始数据（永不改动）
│   ├── interim/              # 中间处理文件（每一步生成新文件）
│   ├── processed/            # 最终清洗后的分析数据
│   └── backup/               # 重要文件备份目录
└── scripts/                  # 数据处理脚本
```

## 🚀 主要功能

### 1. 编码处理
- **DOI补全**：自动获取缺失的论文DOI信息
- **PDF重命名**：使用DOI为论文PDF文件统一命名
- **唯一编码**：为补充信息设置可追溯的唯一标识

### 2. 去重处理
- **Zotero自带去重**：基于元数据的基础去重
- **插件去重**：使用Zoplicate等插件进行高精度去重
- **通用工具**：dupeGuru、imgdupes等专业去重工具
- **语义查重**：FastGPT语义相似性分析

### 3. 分组整理
- **时间分组**：按论文发表年份分类
- **空间分组**：按作者机构分类
- **主题分组**：按研究主题分类

### 4. 元数据完善
- **多源整合**：合并不同数据库的元数据
- **标签添加**：为Markdown文件添加YAML前置数据
- **关键词提取**：使用KeyBERT自动提取关键词

## 🛠️ 技术栈

- **文献管理**：Zotero + Better BibTeX
- **编程语言**：Python 3.x
- **主要库**：pandas, openpyxl, keybert
- **AI工具**：Claude, Gemini-2.5-Pro
- **环境管理**：虚拟环境 (.venv)

## 📦 环境配置

### 虚拟环境激活
```bash
source /Users/tommy/Projects/.venv/bin/activate
```

### 依赖安装（使用清华镜像）
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pandas openpyxl keybert
```

## 📝 使用规范

### 数据处理原则
1. **原始数据保护**：`data/raw/` 中的文件永不直接修改
2. **备份机制**：重要文件修改前自动备份到 `data/backup/`
3. **版本控制**：每个处理步骤生成新文件，保留完整处理链
4. **安全操作**：删除操作需要二次确认并记录日志

### 文件命名规范
- **CSV文件**：`YYYY-MM-DD-HH-MM-SS-[描述].csv`
- **PDF文件**：`[DOI].pdf`（DOI用方括号包裹）
- **Markdown文件**：使用时间戳或唯一标识符命名

## 🔧 常用脚本

### 1. DOI补全脚本
用于批量获取缺失的论文DOI信息

### 2. PDF重命名脚本
根据元数据将PDF文件重命名为标准格式

### 3. 去重检测脚本
识别和处理重复的文献条目

### 4. 元数据合并脚本
整合来自不同数据源的元数据信息

## ⚠️ 注意事项

1. **环境依赖**：优先使用虚拟环境，避免全局包污染
2. **敏感文件**：自动添加到 `.gitignore`，防止意外提交
3. **错误处理**：遇到错误时提供具体原因和解决方案
4. **标准库优先**：优先使用Python标准库，避免复杂依赖

## 📚 参考资料

- [Zotero官方文档](https://www.zotero.org/support/)
- [Better BibTeX插件](https://retorque.re/zotero-better-bibtex/)
- [OpenAlex API文档](https://docs.openalex.org/)
- [KeyBERT文档](https://maartengr.github.io/KeyBERT/)

## 📞 技术支持

如遇到问题，请参考：
1. `Ch03学术整理·实操演示.md` - 详细的实操记录和问题解决方案
2. 虚拟环境配置和依赖管理说明
3. 课程提供的技术文档和示例代码

---

**最后更新时间**：2025年1月27日  
**项目版本**：v1.0  
**维护者**：Tommy
