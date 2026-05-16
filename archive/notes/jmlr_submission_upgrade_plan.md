# 以 JMLR 为目标的论文升级工作文档

## 0. 文档目的

本文档用于规划论文《A Stability Calculus for Local Learning Rules》从当前理论草稿升级到可冲击 **Journal of Machine Learning Research (JMLR)** 的版本。目标不是简单润色，而是把文章从“概念澄清 + 小型反例 + 有限搜索证据”升级为“对机器学习稳定性理论有清晰推进价值的完整研究论文”。

JMLR 的定位是机器学习理论与方法期刊，偏好对广泛机器学习读者有意义的工作。理论论文也需要说明 practical utility，即为什么这些理论结果改变了我们对学习系统的理解、分析或使用方式。因此，JMLR 版本必须回答三个核心问题：

1. 这套稳定性区分是否只是 k-NN 的小现象，还是 local learning rules 中普遍存在的问题？
2. 文章是否给出了足够完整、严谨、不可替代的理论框架？
3. 这些理论结果为什么对机器学习实践、模型评估、交叉验证、鲁棒性或 conformal prediction 有真实启发？

---

## 1. 当前稿件的定位判断

当前稿件的优点：

- 概念清楚：明确区分 delete-one、insert-one、replace-one、LOO 等扰动类型。
- 有一个非常干净的 1-NN 两点图度量反例。
- 有 exact signed-margin criterion，说明 k-NN 预测变化的机制。
- 写作相对诚实：明确区分 theorem、computational certificate、conjecture。
- 与 algorithmic stability、deleted estimate、conformal prediction 等文献有初步连接。

当前稿件的不足：

- 主 theorem payload 偏轻：最强分离结果目前主要是 deterministic 1-NN 的两点 witness。
- odd-k 只到 k=3,5,7 的 computational evidence，尚未成为一般定理。
- 标题声称 local learning rules，但正文核心仍然集中在 deterministic finite k-NN。
- 对 JMLR 来说，实践意义和机器学习普遍意义还不够强。
- 缺少系统的 stability hierarchy：哪些稳定性概念之间有 implication，哪些没有，哪些需要额外条件。
- 缺少真实数据或至少半真实数据实验来说明 LOO 与 replace-one 的差距不是纯数学玩具。

因此，JMLR 路线的关键不是“把文字写得更漂亮”，而是要补充理论主体和应用动机。

---

## 2. JMLR 版本的目标贡献形态

建议将 JMLR 目标版本重塑为如下贡献结构：

> We develop a stability calculus for local learning rules, showing that leave-one-out stability, deletion stability, insertion stability, and replacement stability are distinct both operationally and mathematically. For deterministic nearest-neighbor rules, we provide exact margin-crossing characterizations, sharp separations between LOO and replace-one stability, a hierarchy of perturbation notions, and empirical diagnostics showing that LOO-style evaluation can substantially underestimate replacement sensitivity in local classifiers.

也就是说，JMLR 版的主线应从：

> “LOO 和 replace-one 不是一回事。”

升级为：

> “我们系统刻画了 local learning rules 中单样本扰动稳定性的结构，并证明常用的 LOO-style 稳定性不能替代 replacement-style 鲁棒性；这种差异在理论上可严格分离，在实际局部分类器中也可测量。”

---

## 3. 必须补充的理论工作

### 3.1 证明任意奇数 k 的分离定理

这是最重要的补强项。

当前稿件中，odd-k 只是 bounded finite search evidence。JMLR 审稿人很可能会认为：如果只有 1-NN 两点反例，文章太小；如果 odd-k 不能证明，主张 “k-NN stability calculus” 的力度不足。

建议目标定理：

**Theorem A: Odd-k LOO / replace-one separation.**  
For every odd integer k >= 1, there exists a finite metric space, an ordered binary-labeled sample S, and a query-label pair (x, y) such that all LOO indicators vanish, while some replace-one perturbation changes the loss at (x, y).

需要明确：

- 样本大小如何随 k 增长；
- 是否允许 duplicate occurrences；
- 是否允许 conflicting labels；
- metric space 是否仍可取两点图度量，还是需要更大空间；
- tie-breaking 是否必要；
- witness 是否可以 constructive 地写出，而不是靠搜索。

理想状态是构造一个非常简单的 repeated-occurrence gadget，并逐项验证：

1. 原始样本在所有 LOO evaluation points 上 loss 不变；
2. 某个 replace-one move 使 query 的 top-k signed margin 从非正变为正，或从正变为非正；
3. 对所有 sample indices 的 LOO 都成立，而不只是指定子集。

### 3.2 处理偶数 k 的情况

如果只证明奇数 k，JMLR 版仍然会被问：偶数 k 怎么办？

至少需要做到以下一种：

- 证明偶数 k 也存在类似分离；
- 证明在当前 tie-breaking / binary vote convention 下偶数 k 有特殊结构；
- 说明偶数 k 的困难来自 label-vote tie resolution，并给出 partial theorem；
- 把主要定理限定为 odd-k，但在正文中严肃讨论 even-k，并给出清晰 open problem。

不要只写“even-k appears subtler”。这在普通稿件里可以，在 JMLR 里偏弱。

建议目标：

**Theorem B / Proposition B: Even-k partial characterization.**  
Under fixed label-order tie-breaking, even-k admits / does not admit separation under specified restrictions. If no complete theorem is available, provide a precise conjecture and a nontrivial partial result.

### 3.3 建立完整 stability hierarchy

现在已有 replace-one <= delete-one + insert-one 的 uniform decomposition。但 JMLR 版需要更系统。

建议构造一张 formal hierarchy table，逐项证明或反例否定：

- uniform delete-one vs uniform insert-one；
- uniform replace-one vs delete+insert；
- pointwise delete-one vs LOO；
- LOO vs replace-one；
- expected stability vs worst-case pointwise stability；
- fresh-test replace-one stability vs fixed-query replace-one stability；
- deterministic tie-breaking vs randomized tie-breaking。

每条关系应标注：

- implication true / false；
- theorem / counterexample / open；
- assumptions；
- tightness。

建议目标定理群：

**Theorem C: Perturbation hierarchy.**  
For bounded loss, replace-one stability is upper bounded by delete-one plus insert-one stability, and this bound is tight up to constants in finite local classifiers.

**Theorem D: LOO non-domination.**  
LOO stability does not imply pointwise delete-one or replace-one stability, even for deterministic finite nearest-neighbor rules under specified conditions.

**Theorem E: Conditional equivalence.**  
Under additional margin or neighborhood-invariance assumptions, LOO-style control can imply restricted replacement control.

Theorem E 很重要，因为只有反例会显得消极。JMLR 更喜欢完整理解：什么时候失败，什么时候可以恢复。

### 3.4 给出 exact margin theory 的强化版本

当前 signed-margin criterion 是正确但偏 elementary。需要把它发展成真正有用的工具。

可以补充：

- replacement perturbation 的 margin-change upper/lower bound；
- delete-one / insert-one 对 top-k margin 的 exact effect；
- 用 margin gap 给出 stability certificate；
- 当 top-k margin 绝对值大于某阈值时，某类 perturbation 不可能改变预测；
- 当 margin 处在 boundary 时，构造 perturbation 使预测改变。

建议目标结果：

**Theorem F: Margin certificate for local perturbation stability.**  
For deterministic k-NN, if the signed top-k margin at query x exceeds the maximal possible perturbation effect under a specified operation class, then the prediction is stable; conversely, if the margin is within the operation-specific vulnerability range, a perturbation can be constructed under suitable neighborhood conditions.

这会让 Section 5 不再只是“观察”，而成为后续理论和实验诊断的核心。

### 3.5 从 k-NN 扩展到 local vote rules

JMLR 版本标题如果继续使用 “local learning rules”，必须超出 k-NN。

最低可接受扩展：

- weighted k-NN；
- radius-neighbor majority vote；
- finite local vote classifiers with deterministic neighborhood map；
- prototype / nearest-prototype classifier 的一个特例。

建议定义抽象类：

A local vote rule is specified by:

1. a deterministic neighborhood selector N(S, x);
2. label weights w_i(S, x);
3. a vote aggregation function;
4. fixed tie-breaking.

然后证明：

- margin-crossing criterion 对这类 local vote rules 成立；
- LOO / replace-one separation 可转移到满足某种 locality 和 replacement sensitivity 的规则；
- k-NN 是该框架的一个特例。

这样文章标题和贡献会更可信。

---

## 4. 建议补充的实验工作

JMLR 不一定要求大型视觉实验，但理论论文也需要 practical utility。建议做一组轻量但有说服力的实验，目标不是刷 SOTA，而是证明“LOO 稳定性与 replacement sensitivity 的 gap 在真实数据中可观测”。

### 4.1 Synthetic finite metric benchmark

目的：验证理论构造、展示不同 k 和不同样本结构下的 gap。

实验内容：

- graph metric random generation；
- duplicate / conflict ratio 控制；
- label noise 控制；
- k = 1, 3, 5, 7, 9；
- 比较 max LOO、max delete-one、max insert-one、max replace-one；
- 统计 gap = max replace-one - max LOO。

输出：

- heatmap；
- stability hierarchy violation frequency；
- margin distribution before/after perturbation；
- witness visualization。

### 4.2 Real tabular k-NN experiments

使用 UCI / OpenML 数据集即可，不需要太重。

候选数据：

- Iris；
- Wine；
- Breast Cancer Wisconsin；
- Digits；
- Letter Recognition；
- MNIST subset。

实验设计：

- 标准化特征；
- 使用 k-NN classifier；
- 计算 LOO instability；
- 计算 approximate worst-case replace-one sensitivity；
- 若 exact worst-case 太贵，可以用 candidate replacement pool；
- 比较两者在不同 k、不同 noise ratio 下的差距。

重点不是准确率，而是 stability gap。

### 4.3 Embedding-space k-NN experiments

为了增强现代机器学习意义，可加入 embedding-space nearest-neighbor classifier。

候选：

- sklearn digits embedding；
- pretrained image features；
- CLIP / ResNet features；
- sentence embedding 文本分类也可，但若不想偏离 ML 主线，可先做图像/数字。

实验问题：

- 在 learned embedding 中，LOO 稳定是否低估 replacement sensitivity？
- 哪些 query 具有小 top-k margin，因而 replacement-vulnerable？
- label noise 或 duplicated near-neighbors 是否放大 gap？

### 4.4 Diagnostic algorithm

建议把实验工具包装成一个算法：

**Algorithm: StabilityGapDiagnostic**

输入：distance matrix、labels、k、tie-breaking rule、replacement candidate set。  
输出：

- LOO instability profile；
- delete / insert / replace instability profile；
- vulnerable queries；
- margin-crossing certificates；
- top-k neighbor explanations。

这会显著提升 practical utility。它不一定是新算法用于提高准确率，但可以作为评估和诊断工具。

---

## 5. 写作结构建议

建议 JMLR 版结构如下：

1. Introduction
   - 明确指出 “change one sample” 在 local learning rules 中不是单一概念。
   - 给出 LOO 替代 replace-one 的风险。
   - 强调本文提供完整 calculus，而不是单个反例。

2. Related Work
   - Algorithmic stability and generalization。
   - Nearest-neighbor theory and deleted estimates。
   - Cross-validation and LOO stability。
   - Conformal prediction and stability certificates。
   - Robustness / poisoning / local classifiers。

3. Perturbation Framework
   - delete / insert / replace / LOO definitions。
   - pointwise / uniform / expected notions。
   - operation axis vs evaluation axis。

4. Uniform Perturbation Calculus
   - delete+insert decomposition。
   - tightness / non-implications。
   - hierarchy table。

5. Margin Theory for Local Vote Rules
   - abstract local vote rule。
   - signed margin criterion。
   - stability certificates。
   - k-NN specialization。

6. Separation Theorems for k-NN
   - 1-NN minimal witness。
   - odd-k general construction。
   - even-k results or partial results。
   - role of duplicates, conflicts, and tie-breaking。

7. Beyond k-NN: Local Learning Rules
   - weighted k-NN / radius classifiers / prototype rules。
   - transfer of separation or certificates。

8. Empirical Stability Gap Diagnostics
   - synthetic finite metrics。
   - UCI/OpenML。
   - embedding-space k-NN。
   - visualizations and case studies。

9. Practical Implications
   - why LOO is not replacement robustness；
   - implications for CV, conformal prediction, data poisoning, local classifiers；
   - recommended reporting practices。

10. Limitations and Open Problems
   - honest but not self-undermining。

11. Conclusion

Appendices:

- Full proofs。
- Enumeration details。
- Additional experiments。
- Reproducibility checklist。

---

## 6. 需要重写的关键叙事

当前稿件中多次强调 “we do not claim ...”。这种诚实是优点，但 JMLR 版要避免给人“贡献不足”的心理暗示。

建议替换叙事方式：

不要写：

> We do not claim a new generalization bound.

改成：

> Our goal is orthogonal to distributional generalization bounds: we characterize the finite-sample perturbation semantics that such bounds often abstract away. This provides a diagnostic layer for local learning rules and clarifies when LOO-style evidence can or cannot be interpreted as replacement-style robustness.

不要写：

> Odd-k search outputs are not theorem statements.

改成：

> We prove a general odd-k construction. The finite search is used only to validate minimal examples and support reproducibility.

当然，前提是 odd-k 已经证明。若不能证明，就不要把 odd-k 放在主贡献里。

---

## 7. 文献需要补充的方向

当前 bibliography 已经覆盖 stability、nearest neighbor、deleted estimates、conformal prediction。JMLR 版建议补充以下方向：

1. Algorithmic stability 后续理论
   - high-probability stability；
   - on-average stability；
   - stability and generalization for randomized algorithms。

2. Cross-validation / LOO 理论
   - LOO as risk estimator；
   - stability of cross-validation；
   - deleted estimates in nonparametric learning。

3. Robustness / poisoning / data perturbation
   - training-data poisoning；
   - label noise；
   - adversarial examples in training data；
   - local robustness of classifiers。

4. Metric learning and nearest-neighbor classification
   - modern embedding-based k-NN；
   - prototype methods；
   - nearest-neighbor in representation learning。

5. Conformal prediction
   - training-conditional coverage；
   - stability-based conformal methods；
   - leave-one-out conformal / jackknife+ style connections。

目标不是堆文献，而是让 JMLR reviewer 看到：本文解决的是 ML 稳定性与局部分类器评估中的一个真实缝隙。

---

## 8. 最小可行 JMLR 版本 vs 理想 JMLR 版本

### 8.1 最小可行版本

如果时间有限，至少做到：

1. 证明所有奇数 k 的 separation theorem。
2. 给出 stability hierarchy table，并证明主要 non-implications。
3. 强化 margin criterion 为 stability certificate。
4. 加入至少一组 synthetic + 一组真实数据实验。
5. 写清楚 practical utility。
6. 删除或弱化所有未证明 conjecture。

这是最低门槛。

### 8.2 理想版本

更强版本应做到：

1. 完整处理 odd/even k。
2. 给出 tight bounds。
3. 扩展到 weighted k-NN / radius rules / abstract local vote rules。
4. 提供 diagnostic algorithm。
5. 做 embedding-space 实验。
6. 给出 reproducible package。
7. 文章形成 “framework + theory + diagnostics + implications” 的完整闭环。

---

## 9. 任务拆解清单

### Phase 1: 理论主定理补强

- [ ] 形式化 repeated-occurrence odd-k construction。
- [ ] 证明所有 LOO indicators vanish。
- [ ] 证明存在 replace-one perturbation 使 loss 改变。
- [ ] 分析构造是否依赖 duplicate / conflicting labels。
- [ ] 研究 even-k 情形。
- [ ] 证明或反驳 delete / LOO / replace 的主要 implications。
- [ ] 补充 tightness examples。

### Phase 2: margin theory 升级

- [ ] 把 signed-margin criterion 抽象到 local vote rules。
- [ ] 定义 operation-specific margin perturbation radius。
- [ ] 给出 sufficient stability certificate。
- [ ] 给出 converse vulnerability condition。
- [ ] 把理论连接到 diagnostic algorithm。

### Phase 3: 实验与代码

- [ ] 整理现有 finite search pipeline。
- [ ] 实现 StabilityGapDiagnostic。
- [ ] 生成 synthetic graph metric benchmark。
- [ ] 跑 UCI/OpenML 数据。
- [ ] 跑 embedding-space k-NN 实验。
- [ ] 生成主文图：hierarchy diagram、margin crossing、gap heatmap、real-data case studies。
- [ ] 准备 reproducibility appendix。

### Phase 4: 写作重构

- [ ] 重写 introduction，突出 JMLR-level contribution。
- [ ] 重写 related work，强化 broader ML connection。
- [ ] 把 theorem / conjecture / certificate 边界重新整理。
- [ ] 把 computational evidence 降为 supporting material。
- [ ] 加 practical utility section。
- [ ] 控制篇幅，避免正文过多图示但保留关键可视化。

### Phase 5: 投稿前自检

- [ ] 每个主张都有 theorem、proof、experiment 或明确限定。
- [ ] 不依赖“最小性 computational certificate”作为主贡献。
- [ ] 文章读者不需要关心 graph metric 细节也能理解意义。
- [ ] 文章能回答：为什么 ML 社区应该关心这个 distinction？
- [ ] 文章能回答：这是否改变了我们评估 local classifiers 的方式？
- [ ] 所有代码、数据、图、随机种子可复现。

---

## 10. 建议的最终摘要方向

JMLR 版摘要应避免只描述小 witness，可以写成以下逻辑：

1. Local learning rules are often evaluated through leave-one-out or deleted-sample procedures.
2. However, operation type and evaluation point are distinct axes of stability.
3. We introduce a perturbation calculus separating delete-one, insert-one, replace-one, and LOO stability.
4. For deterministic nearest-neighbor and broader local vote rules, we characterize prediction changes by signed margin crossing.
5. We prove sharp separations showing that LOO stability can fail to control replacement sensitivity, including general odd-k constructions.
6. We provide stability diagnostics and empirical evidence that the gap appears in finite metric and real-data local classifiers.
7. The results clarify how LOO-style evidence should and should not be interpreted for local learning systems.

---

## 11. 现实判断

如果只在当前版本基础上做语言润色，不建议投 JMLR。更合适的是 TMLR、Machine Learning 或短理论期刊。

如果愿意补充上述理论和实验，JMLR 是合理但仍然有挑战的目标。最关键的突破点是：

1. odd-k 一般定理；
2. stability hierarchy；
3. local vote rule 泛化；
4. practical utility 与诊断实验。

其中前两个是硬门槛，后两个决定文章能否从“不错的理论 note”变成“JMLR 级别的机器学习论文”。
