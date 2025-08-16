# Attention Is All You Need – 术语系统提取与初步评估

> 处理日期：2025-08-03  
> 论文：Ashish Vaswani et al., 2017 《Attention Is All You Need》

## 术语清单

| 唯一编号 | 术语原文 | 中文翻译 | 语义边界 | 是否为缩写/组合词 | 出现频次 | 表达清晰度 | 语义风险等级 | 备注 | 定义 |
|---|---|---|---|---|---|---|---|---|---|
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00001 | Sequence Transduction Model | 序列转换模型 | 通用 | 否 |  | 高 | 低 | 研究范畴 | 将输入符号序列映射为输出符号序列的模型框架（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00002 | Recurrent Neural Network | 循环神经网络 | 通用 | 是 |  | 高 | 低 | 典型基线方法 | 通过递归连接隐藏状态来处理序列数据的神经网络架构（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00003 | Convolutional Neural Network | 卷积神经网络 | 通用 | 是 |  | 高 | 低 | 典型基线方法 | 采用卷积运算抽取局部特征并支持并行计算的网络结构（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00004 | Encoder | 编码器 | 通用 | 否 |  | 高 | 低 | 模型子组件 | 将输入序列映射为连续表示向量序列的网络堆栈（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00005 | Decoder | 解码器 | 通用 | 否 |  | 高 | 低 | 模型子组件 | 自回归地将表示向量序列解码为目标序列的网络堆栈（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00006 | Attention Mechanism | 注意力机制 | 通用 | 否 |  | 高 | 低 | 关键技术 | 根据查询与键的相似度对值加权求和以捕获长程依赖的计算模块（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00007 | Transformer | Transformer（变压器） | 作者自造 | 否 |  | 高 | 中 | 核心研究对象 | 一种完全基于注意力、无循环与卷积的新型序列转换网络架构 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00008 | BLEU | BLEU 分数 | 通用 | 是 |  | 高 | 低 | 评估指标 | 机器翻译领域常用的 n-gram 精确率加权几何平均评分指标（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00009 | WMT 2014 English-to-German translation task | WMT2014 英→德 任务 | 特定 | 否 |  | 高 | 低 | 数据集/基准 | WMT 2014 新闻翻译评测中的英德平行语料测试任务（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00010 | WMT 2014 English-to-French translation task | WMT2014 英→法 任务 | 特定 | 否 |  | 高 | 低 | 数据集/基准 | WMT 2014 新闻翻译评测中的英法平行语料测试任务（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00011 | Sequence Length | 序列长度 | 通用 | 否 |  | 高 | 低 | 变量 | 输入或输出标记序列包含的符号数量（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00012 | Hidden State | 隐藏状态 | 通用 | 否 |  | 高 | 低 | 变量 | RNN 中逐步传播的内部向量表示 $h_t$（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00013 | Self-Attention | 自注意力 | 通用 | 否 |  | 高 | 低 | 关键技术 | 在同一序列内建立元素间依赖的注意力机制，也称 intra-attention |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00014 | Multi-Head Attention | 多头注意力 | 作者自造 | 否 |  | 高 | 低 | 关键技术 | 并行执行 $h$ 个线性投影后再合并的注意力机制，提高表示多样性 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00015 | Extended Neural GPU | 扩展神经 GPU | 特定 | 否 |  | 中 | 低 | 参照模型 | 使用卷积门控单元减少序列依赖的并行模型（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00016 | ByteNet | ByteNet | 特定 | 否 |  | 中 | 低 | 参照模型 | 采用递归卷积实现对位置信息分层建模的序列模型（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00017 | ConvS2S | ConvS2S | 特定 | 否 |  | 中 | 低 | 参照模型 | 基于卷积序列到序列架构的机器翻译模型（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00018 | Scaled Dot-Product Attention | 缩放点积注意力 | 作者自造 | 否 |  | 高 | 低 | 关键技术 | 将 $QK^T/\sqrt{d_k}$ 经过 softmax 得权重后乘 V 的注意力公式 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00019 | Query | 查询向量 | 通用 | 否 |  | 高 | 低 | 子概念 | 注意力计算中表示当前焦点的向量 Q |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00020 | Key | 键向量 | 通用 | 否 |  | 高 | 低 | 子概念 | 与 Query 做相似度匹配的向量 K |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00021 | Value | 值向量 | 通用 | 否 |  | 高 | 低 | 子概念 | 被加权汇聚以产生输出的向量 V |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00022 | Softmax Function | Softmax 函数 | 通用 | 否 |  | 高 | 低 | 数学运算 | 将向量归一化为概率分布的指数归一化函数（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00023 | Dot-Product Attention | 点积注意力 | 通用 | 否 |  | 高 | 低 | 早期方法 | 不含缩放因子的 Q·K^T 注意力形式（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00024 | Additive Attention | 加性注意力 | 通用 | 否 |  | 高 | 低 | 早期方法 | 通过单隐层前馈网络计算兼容度的注意力形式（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00025 | Embedding Layer | 嵌入层 | 通用 | 否 |  | 高 | 低 | 模型组件 | 将离散符号映射到 $d_{model}$ 维连续向量的可学习查表层（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00026 | Layer Normalization | 层归一化 | 通用 | 否 |  | 高 | 低 | 正则手段 | 对同一层特征维度做归一化以稳定训练的技术 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00027 | Residual Connection | 残差连接 | 通用 | 否 |  | 高 | 低 | 训练技巧 | 将子层输出与输入相加以缓解梯度消失的结构设计（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00028 | Feed-Forward Network | 前馈网络 | 通用 | 否 |  | 高 | 低 | 模型组件 | 对每个位置独立应用两层线性+ReLU 的全连接网络 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00029 | Positional Encoding | 位置编码 | 作者自造 | 否 |  | 高 | 中 | 关键技术 | 将位置信息以正弦/余弦函数注入到输入嵌入中的向量（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00030 | Auto-Regressive Property | 自回归属性 | 通用 | 否 |  | 中 | 低 | 序列假设 | 生成第 i 位时仅依赖 <i 的已知输出的条件假设（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00031 | d_model | 模型维度 | 通用 | 是 |  | 中 | 低 | 超参数 | Transformer 中所有子层输出的统一向量维度（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00032 | Parameter Matrix | 参数矩阵 | 通用 | 否 |  | 高 | 低 | 变量 | 用于线性投影 Q,K,V,O 的可学习权重矩阵（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00033 | Beam Search | 集束搜索 | 通用 | 否 |  | 高 | 低 | 解码算法 | 以固定宽度探索概率最高序列的启发式搜索策略（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00034 | Byte-Pair Encoding | 子词对编码 | 通用 | 否 |  | 高 | 低 | 编码方法 | 基于频次迭代合并的子词切分算法，用于词表构建 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00035 | Word-Piece Vocabulary | 单词片段词表 | 通用 | 否 |  | 高 | 低 | 编码方法 | 由 WordPiece 规则生成的子词级词汇集合 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00036 | Adam Optimizer | Adam 优化器 | 通用 | 否 |  | 高 | 低 | 训练算法 | 使用一阶矩和二阶矩估计的自适应学习率优化方法 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00037 | Dropout | Dropout | 通用 | 否 |  | 高 | 低 | 正则手段 | 训练时随机丢弃神经元以缓解过拟合的技术 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00038 | Label Smoothing | 标签平滑 | 通用 | 否 |  | 高 | 低 | 正则手段 | 将目标分布加入均匀噪声以提升泛化与 BLEU 的技术 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00039 | Warmup Steps | 预热步数 | 特定 | 否 |  | 中 | 低 | 超参数 | 训练前期线性增大学习率的梯度上升步数 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00040 | Path Length | 路径长度 | 通用 | 否 |  | 中 | 低 | 分析指标 | 神经网络中任意两位置间前向/反向信号最短路径的层数 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00041 | Computational Complexity | 计算复杂度 | 通用 | 否 |  | 高 | 低 | 分析指标 | 对层级运算量随输入长度、维度变化的符号级估计 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00042 | Sequential Operations | 顺序操作 | 通用 | 否 |  | 高 | 低 | 分析指标 | 完成特定层需串行执行的依赖步骤数量 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00043 | English Constituency Parsing | 英语成分句法分析 | 特定 | 否 |  | 高 | 低 | 任务场景 | 将句子解析为短语结构树的 NLP 任务（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00044 | Penn Treebank | Penn Treebank 语料库 | 通用 | 否 |  | 高 | 低 | 数据来源 | 标注英语句法结构的大规模文本语料集 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00045 | Wall Street Journal | 华尔街日报数据集 | 通用 | 否 |  | 高 | 低 | 数据来源 | Penn Treebank 中 40K 句子子集，来源于 WSJ 报纸 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00046 | Attention Head | 注意力头 | 作者自造 | 否 |  | 高 | 低 | 子概念 | Multi-Head Attention 中独立学习不同子空间表示的单个注意力分支 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00047 | Mixture-of-Experts | 稀疏专家混合 | 通用 | 否 |  | 中 | 中 | 参照模型 | 通过门控路由到多个子模型以提升容量的架构（推断） |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00048 | ReLU Activation | ReLU 激活 | 通用 | 否 |  | 高 | 低 | 数学运算 | f(x)=max(0,x) 的非线性激活函数 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00049 | Position-wise Feed-Forward Network | 逐位置前馈网络 | 作者自造 | 否 |  | 高 | 低 | 模型子层 | 对序列每个位置独立使用两层线性+ReLU 的前馈子结构 |
| T-20250803-Vaswani2017-AttentionIsAllYouNeed-00050 | State-of-the-Art | 最高水平 | 通用 | 否 |  | 高 | 低 | 评价用语 | 同时期公开文献中性能最佳的参考基准（推断） |

---

## R1：术语内容反思

1. **语义重复/表达变体**：如 *Attention Mechanism* 与 *Self-Attention*、*Dot-Product Attention* 等存在层级关系，易被混用；*Feed-Forward Network* 与 *Position-wise Feed-Forward Network* 亦为包含关系。
2. **术语密集但结构不明段落**：3.2 节在介绍多种 Attention 形式与参数时，概念集中出现，若无图示辅助可能导致信息过载。
3. **高频但缺乏定义术语**：*Beam Search*、*BLEU* 在正文中多次出现却缺少正式定义，新手读者需查阅外部文献。
4. **表达不稳/歧义术语**：*Hidden State* 在不同模型上下文意义略有差异；*Path Length* 可指网络深度也可指依赖距离，需结合表 1 理解。
5. **具备演化潜力术语**：*Positional Encoding*、*Multi-Head Attention* 与 *Position-wise Feed-Forward Network* 均已被后续研究衍生为独立改进方向或模块名。

## R2：AI 执行过程元反思

- **术语边界判断**：文中复合名词较多，且作者倡导新架构，需依据语义功能而非词形长度判断边界，整体可操作性中等。
- **聚合/拆分分歧**：例如将 *Query/Key/Value* 视为独立术语还是合并为 *Attention Triplet* 存在取舍，本次保留粒度细节以利模型映射。
- **策略瓶颈**：纯基于规则快速扫描无法获取行文外频次，未来可接入统计脚本自动计数；定义提取仍需手动概括，自动化困难。
- **易遗漏类型**：常见数学符号（如 $d_k$）若未出现显式文字描述易被跳过，可通过正则捕获 LaTeX 变量名改进。
- **自评分**：覆盖率≈90%，命名判断≈85%，定义还原≈80%；主要风险来自频次统计缺失与部分定义推断。
