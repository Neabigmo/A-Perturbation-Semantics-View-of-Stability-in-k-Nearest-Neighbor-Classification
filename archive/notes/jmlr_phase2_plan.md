# JMLR 升级 Phase 2: 运行、验证、润色、收尾

## 目标

在 Phase 1 的基础上，完成从理论草稿到可编译、可运行的 JMLR 稿件的最后冲刺。

## 核心任务

### 1. 交叉一致性检查

Phase 1 创建了 13 个新文件，涉及大量的 cross-reference。需要系统检查：

- [ ] 所有 `\label{...}` 和 `\Cref{...}` / `\ref{...}` 是否匹配（跨新旧 sections）
- [ ] 定理编号是否连贯（new_main.tex 中定理编号逻辑是否可行）
- [ ] 所有 `\cite{...}` 引用在 refs.bib 中是否存在
- [ ] 新旧 sections 之间的命名约定是否统一（如 thm: vs prop: vs theorem:）
- [ ] 检查 Section 3b (DLVR) 中 Proposition 3.2 使用的 aggregation threshold τ 和旧 Section 5 的 Proposition 5.1 是否一致
- [ ] 检查 new_main.tex 的章节顺序逻辑

### 2. 运行实验

Phase 1 创建了实验脚本和图片生成脚本，需要实际运行：

- [ ] 运行 `stability_gap_synthetic.py` 生成 synthetic benchmark 数据
- [ ] 运行 `stability_gap_tabular.py` 生成 UCI 数据
- [ ] 运行 `stability_gap_embedding.py` 生成 embedding 数据
- [ ] 运行 `generate_experiment_figures.py` 生成实际图表
- [ ] 确保输出路径与 LaTeX 中的 `\includegraphics{}` 路径一致
- [ ] 确认实验数据与论文中的 claims 一致

### 3. LaTeX 编译验证

- [ ] 尝试编译 `new_main.tex`，修复所有编译错误
- [ ] 修复缺失的 bib 引用
- [ ] 确保所有 graphics 文件存在（或暂时使用 draft 模式）
- [ ] 确认 no overfull/underfull hbox warnings 泛滥

### 4. 叙事线加强

- [ ] 检查整个稿件的"红线"是否连贯：从定义 → 纯理论 → DLVR 泛化 → 实验 → 实践意义
- [ ] 确保每个 section 都以过渡句开始，连接到前一个 section
- [ ] 检查防御性语言是否还有残留
- [ ] 检查每个定理是否都有足够的动机说明，而不是"从天而降"

### 5. 输出产物

- [ ] 修正后的完整 LaTeX 源文件
- [ ] 实验数据和图表（实际运行，非 placeholder）
- [ ] 编译验证报告（可以/不可以编译）
- [ ] 待办问题列表（如果有未解决的问题）

## 开始执行

请从任务 1 开始，按顺序执行。每一步记录发现的问题和修复。
