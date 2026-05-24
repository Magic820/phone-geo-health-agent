# {product_name} GEO健康检查报告

> 检查时间：{timestamp}
> 测试Query数：{query_count}
> 认知一致性综合得分：{consistency_score}/100

---

## 1. 检查摘要

| 指标 | 结果 | 说明 |
|------|------|------|
| 认知一致性得分 | {consistency_score}/100 | AI认知与市场定位的匹配度 |
| 价格认知偏差 | {price_deviation} | AI认知价格与官方定价的差异 |
| 卖点覆盖度 | {feature_coverage} | 核心卖点被提及的比例 |
| 人群匹配度 | {audience_match} | 目标人群特征的匹配程度 |
| 高频竞品 | {top_competitors} | 出现次数最多的竞品 |

**核心发现**：{key_findings}

---

## 2. 产品画像（基准定位）

### 基础信息
- **产品名称**：{product_name}
- **品牌**：{brand}
- **价格段**：{price_range}
- **品类**：{category}

### 市场定位
- **定位描述**：{positioning}
- **目标人群**：{target_audience}
- **核心场景**：{core_scenarios}

### 核心卖点
| 序号 | 卖点 | 官方描述 |
|------|------|---------|
| 1 | {feature_1} | {feature_desc_1} |
| 2 | {feature_2} | {feature_desc_2} |
| 3 | {feature_3} | {feature_desc_3} |

---

## 3. 认知/推荐阶段表现

> 用户处于需求发现阶段，寻求初步推荐。此阶段验证产品的自然曝光和价格/人群定位认知。

### 3.1 泛推荐场景

| 指标 | 数值 | 说明 |
|------|------|------|
| 提及率 | {general_mention_rate} | 在泛推荐中被提及的比例 |
| 首推率 | {general_first_rate} | 在推荐列表中排第一的比例 |
| 情感倾向 | {general_sentiment} | 正面/中性/负面 |
| 正向关键词 | {general_positive} | AI认可的产品优势 |
| 负向关键词 | {general_negative} | AI提及的产品不足 |
| 主要竞品 | {general_competitors} | 同时被推荐的竞品 |

### 3.2 价位推荐场景

| 指标 | 数值 | 说明 |
|------|------|------|
| 提及率 | {price_mention_rate} | 在{price_range}价位推荐中被提及 |
| 首推率 | {price_first_rate} | 在价位推荐中排第一 |
| 情感倾向 | {price_sentiment} | 正面/中性/负面 |
| 正向关键词 | {price_positive} | 价位维度的优势关键词 |
| 负向关键词 | {price_negative} | 价位维度的劣势关键词 |
| 主要竞品 | {price_competitors} | 同价位竞品 |

**价格认知偏差**：AI认为{product_name}属于{ai_price_perception}，与官方定价{price_range}存在{price_deviation}偏差。

### 3.3 人群推荐场景

| 指标 | 数值 | 说明 |
|------|------|------|
| 提及率 | {audience_mention_rate} | 在{target_audience}人群推荐中被提及 |
| 首推率 | {audience_first_rate} | 在人群推荐中排第一 |
| 情感倾向 | {audience_sentiment} | 正面/中性/负面 |
| 正向关键词 | {audience_positive} | 人群匹配的优势 |
| 负向关键词 | {audience_negative} | 人群匹配的劣势 |
| 主要竞品 | {audience_competitors} | 同人群竞品 |

### 3.4 场景推荐场景

| 指标 | 数值 | 说明 |
|------|------|------|
| 提及率 | {scenario_mention_rate} | 在核心场景推荐中被提及 |
| 首推率 | {scenario_first_rate} | 在场景推荐中排第一 |
| 情感倾向 | {scenario_sentiment} | 正面/中性/负面 |
| 正向关键词 | {scenario_positive} | 场景相关优势 |
| 负向关键词 | {scenario_negative} | 场景相关劣势 |
| 主要竞品 | {scenario_competitors} | 同场景竞品 |

---

## 4. 对比阶段表现

> 用户进入产品比较阶段，评估不同选项。此阶段分析产品在直接竞争中的胜负表现和优劣势。

| 对比竞品 | 胜负率 | 对比维度 | 优势点 | 劣势点 |
|---------|-------|---------|-------|-------|
| {competitor_1} | {competitor_1_win_rate} | {competitor_1_dimensions} | {competitor_1_strengths} | {competitor_1_weaknesses} |
| {competitor_2} | {competitor_2_win_rate} | {competitor_2_dimensions} | {competitor_2_strengths} | {competitor_2_weaknesses} |

### 对比维度分析

| 维度 | 表现 | 说明 |
|------|------|------|
| 性能 | {perf_result} | {perf_note} |
| 拍照 | {camera_result} | {camera_note} |
| 续航 | {battery_result} | {battery_note} |
| 价格 | {price_result} | {price_note} |

---

## 5. 决策阶段表现

> 用户接近购买决策，关注风险和价值。此阶段验证购买建议和风险认知。

### 5.1 值不值得买

| 指标 | 数值 | 说明 |
|------|------|------|
| 推荐率 | {worth_buy_rate} | 明确推荐购买的比例 |
| 情感倾向 | {worth_buy_sentiment} | 整体评价倾向（正面/中性/负面） |
| 购买建议 | {buy_recommendations} | AI的购买建议要点 |
| 顾虑点 | {buy_concerns} | AI提及的购买顾虑 |

### 5.2 风险疑虑分析

| 风险类型 | 评价 | 核心关键词 |
|---------|------|-----------|
| {risk_1} | {risk_1_eval} | {risk_1_keywords} |
| {risk_2} | {risk_2_eval} | {risk_2_keywords} |

---

## 6. 引用来源分析

> 分析豆包回答中的引用情况，结合GEO知识库给出优化策略。

### 6.1 引用情况统计

| 维度 | 结果 | 说明 |
|------|------|------|
| 有引用的Query数 | {cited_queries} | 包含外部引用的问题数量 |
| 无引用的Query数 | {uncited_queries} | 完全无引用的问题数量 |
| 引用率 | {cite_rate} | 有引用的Query占比 |
| 引用来源总数 | {total_sources} | 不同来源数量 |

### 6.2 引用来源质量评估

| 来源平台 | 出现次数 | 权威性评分（1-5） | 新鲜度（最新/近期/旧） | 说明 |
|---------|-------|-------------|-------------------|------|
| {source_1} | {source_1_count} | {source_1_authority} | {source_1_freshness} | {source_1_note} |
| {source_2} | {source_2_count} | {source_2_authority} | {source_2_freshness} | {source_2_note} |

### 6.3 引用内容结构化分析（参考GEO知识库）

| 评估项 | 表现 | 优化建议（对应知识库章节） |
|------|------|-------------------------|
| 参数语义化 | {param_semantic} | **参照4.1参数语义化重构**：将参数转化为"技术参数+使用场景+用户收益"三位一体描述，如"5000mAh→连续刷剧14小时" |
| 数据支撑 | {data_support} | **参照维度一**：引用中关村在线、鲁大师、安兔兔等测评机构数据，标注3C/IPX/HDR等认证信息 |
| 结构表达 | {struct_expression} | **参照维度五**：使用###分层标题、表格、列表组织内容，核心参数表格化，"问题→证据→结论"三段式结构 |
| 时效性 | {timeliness} | **参照维度二**：标注"截至2026年X月"，及时更新产品价格与参数，覆盖最新发布的型号 |
| 多角度覆盖 | {multi_angle} | **参照维度四**：内容包含优势+不足+适用人群，对比2-3款同价位竞品 |

---

## 7. 认知一致性评估

> 评估AI对产品的认知与市场团队定位的匹配程度。

### 7.1 各维度评分

| 评估维度 | 评分 | 匹配度 | 说明 |
|---------|------|-------|------|
| 价格认知 | {price_score} | {price_match} | AI认知价格与官方定价的偏差程度 |
| 卖点认知 | {feature_score} | {feature_match} | 核心卖点的覆盖和准确传达 |
| 人群认知 | {audience_score} | {audience_match_text} | 目标人群特征的匹配 |
| 定位认知 | {positioning_score} | {positioning_match} | 产品定位描述的一致性 |
| **综合得分** | {consistency_score} | {overall_match} | 加权平均 |

### 7.2 认知偏差分析

| 偏差类型 | 偏差描述 | 影响程度 | 建议 |
|---------|---------|---------|------|
| {bias_1_type} | {bias_1_desc} | {bias_1_impact} | {bias_1_suggestion} |
| {bias_2_type} | {bias_2_desc} | {bias_2_impact} | {bias_2_suggestion} |

---

## 8. 优化建议

### 🔴 高优先级（P0）

#### {action_1_title}
- **问题描述**：{action_1_problem}
- **偏差来源**：{action_1_source}
- **优化方向**：{action_1_direction}
- **预期效果**：{action_1_effect}

#### {action_2_title}
- **问题描述**：{action_2_problem}
- **偏差来源**：{action_2_source}
- **优化方向**：{action_2_direction}
- **预期效果**：{action_2_effect}

### 🟡 中优先级（P1）

#### {action_3_title}
- **问题描述**：{action_3_problem}
- **偏差来源**：{action_3_source}
- **优化方向**：{action_3_direction}
- **预期效果**：{action_3_effect}

### 🟢 低优先级（P2）

#### {action_4_title}
- **优化方向**：{action_4_direction}
- **预期效果**：{action_4_effect}

---

> **免责声明**：本报告基于{timestamp}的豆包回答快照生成。AI推荐结果具有非确定性，本报告呈现的是时间点快照而非承诺结果。策略建议旨在"提高认知一致性"，而非保证特定输出。