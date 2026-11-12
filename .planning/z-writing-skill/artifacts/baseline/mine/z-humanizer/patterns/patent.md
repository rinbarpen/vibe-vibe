# Patent Humanization Patterns

Supplement to existing humanizer skills. Covers AI patterns specific to patent
writing (Chinese + English) that general humanizers do not address.

## Positive Style Guide

Good patent prose is:
- **Precise** — every term has exactly one referent; no synonym cycling
- **Structural** — describes what something IS and HOW it works, not what it achieves
- **Measured** — no subjective praise, no relative terms without definition
- **Consistent** — same term for same component across entire document
- **Claim-ready** — specification language is consistent with claim language

## AI Patterns

### P1: Claim Transition Rigidity

AI overuses formulaic claim transitions, producing claims that read as
template fill-ins rather than precise legal definitions.

**Chinese triggers:**
- 其特征在于，所述……包括……
- 其特征在于，还包括……
- 如权利要求X所述的……，其特征在于……

**Fix:** Vary transition structure. Use different placement of characterizing
language. Not every claim needs "其特征在于" — use dependent claim formats
that reference without restating.

**Hard constraint:** In a set of 5+ claims, no more than 3 should start
the characterizing portion with identical phrasing.

---

### P2: Terminology Cycling (Elegant Variation)

AI penalizes repetition, so it substitutes synonyms for the same component.
Patent law requires EXACTLY ONE term per component.

**Watch for:**
- 处理器 → CPU → 处理单元 → 计算设备 across different sections
- 存储模块 → 存储器 → 存储单元 → 内存
- signal → data → information → output (when referring to same thing)

**Fix:** Pick ONE canonical term per distinct component. Use it everywhere.
Only introduce a new term when referring to a genuinely different entity.

**Hard constraint:** Zero allowed. Every component must have exactly one
canonical term. If synonym cycling is detected, unify.

---

### P3: Subjective Adjectives and Significance Hype

Patent writing explicitly forbids subjective praise language.

**Chinese ban list:**
- 优秀的 / 卓越的 / 极佳的
- 革命性的 / 突破性的 / 开创性的
- 显著的 / 巨大的 / 惊人的
- 完美的 / 理想的

**English ban list:**
- excellent / superior / outstanding / exceptional
- revolutionary / groundbreaking / novel (more than once per section)
- significant / dramatic / surprising
- ideal / perfect / optimal

**Fix:** Replace with structural or comparative descriptions.
- "显著提升" → "相比现有技术，处理速度提升20-30%"
- "excellent performance" → "throughput of 1000 transactions per second"

**Hard constraint:** Zero subjective adjectives in entire document.

---

### P4: Result-to-be-achieved Language

AI describes what a component is FOR rather than what it IS. Patent
specification requires structural enablement.

**Pattern:**
- "配置为……" → "包括……，所述……用于……"
- "被配置用于实现……" → "包括一个……接口，所述接口连接到……"
- "configured to achieve X" → "comprising a processor coupled to a memory"

**Fix:** Replace functional descriptions with structural ones. Show the
mechanism, not the goal.

**Hard constraint:** Every functional phrase ("配置为"/"configured to")
must be paired with a structural component it connects to. Pure functional
descriptions without structural basis → rewrite.

---

### P5: Relative Terms Without Definition

AI uses relative terms without establishing a reference frame. Patent law
requires definite measurement or context.

**Watch for:**
- thin / thick / small / large / fast / slow
- 薄 / 厚 / 小 / 大 / 快 / 慢
- improved / enhanced / reduced
- 改进的 / 增强的 / 降低的

**Fix:** Either contextualize ("相比现有技术") or quantify ("厚度为
0.5-2mm"). If neither is possible, flag for author.

**Hard constraint:** Every relative adjective must have either:
(a) a specific measurement, or (b) an explicit reference frame. Flag if
neither exists.

---

### P6: Negative Limitation Structure

AI defaults to describing what something is NOT instead of what it IS.
Negative limitations are narrower and harder to defend.

**Patterns:**
- "不包含数据库" → "包含一个本地缓存"
- "无需人工干预" → "自动执行"
- "does not require X" → "operates independently of X"
- "without using Y" → "uses Z instead of Y"

**Fix:** Convert to positive structural features. Only keep negative
limitations when the negative is the actual inventive step (rare).

**Hard constraint:** No more than 2 negative limitations per independent
claim. Each must be justified as the actual invention.

---

### P7: Antecedent Basis Failure

AI fails to maintain proper "a/an" → "the/said" flow across sentences.

**Pattern:**
- First mention: "a processor" ✓
- Second mention: "a processor" ✗ (should be "the processor" / "said processor")
- 首次提及："一个处理器" ✓
- 后续提及："所述处理器" ✓  vs "一个处理器" ✗

**Fix:** Ensure every subsequent reference to an introduced element uses
"the/said" (EN) or "所述" (CN). Check especially after paragraph breaks
and across sections.

---

### P8: Boilerplate Embodiment Language

AI generates embodiment descriptions that follow the same template for
every component, producing monotony.

**Patterns:**
- "在本实施例中，所述……与所述……连接" repeated for every component
- "可选地，所述……还包括……" stacked in identical structure
- "In one embodiment, the X is connected to the Y" templated

**Fix:** Vary embodiment format:
- Some components: describe connection first, then function
- Others: describe function first, then connection
- Vary sentence structure: connector placement, verb choice, information order
- Break the "优选地/可选地/示例性地" chain

---

### P9: Machine Translation Artifacts (Chinese-English)

When a Chinese patent is machine-translated to English (or vice versa),
distinctive AI patterns emerge.

**Chinese→English tells:**
- Overuse of "the said" (literal translation of "所述")
- Missing articles (Chinese has no articles)
- "The present invention" used where not needed
- Overly long pre-modifier chains ("the data processing method based on
  deep learning and implemented by a neural network")

**English→Chinese tells:**
- 过度使用"的"（英语所有格直译）
- 被动语态堆叠（英语专利的被动直译为中文）
- 从句结构保留（英语关系从句直译为中文长定语）

**Fix:** Read in target language. If translation artifacts detected, rewrite
to target-language-native patent style.

---

### P10: Embodiment Number Padding

AI pads embodiments with minor variations that add length without scope.

**Pattern:**
- Embodiment 1-5 are essentially the same with one parameter changed
- "优选地" stacked at 4+ levels ("可选地，优选地，进一步优选地，最优选地")

**Fix:** Collapse numbered embodiments that only vary one parameter into a
single embodiment with a range. Remove optional/preferred stacks beyond
2 levels.

**Hard constraint:** Maximum 2 levels of preferred/optional nesting.
Stacked "优选地/可选地" → collapse into single description with scope.

---

### P11: Drawing Description Formula

AI generates drawing descriptions in a monotonous template pattern.

**Pattern:**
- "图1是本发明实施例提供的一种……的结构示意图"
- "图2是本发明实施例提供的一种……的流程图"
- Every figure description starts with same template

**Fix:** Vary figure description structures:
- Some: "参照图1，……包括……"
- Others: "图2展示了……的流程"
- Mix: "下面结合图3说明……"

---

### P12: Background Section Over-Structuring

AI writes background sections as mini-literature reviews rather than
focused problem statements (patent backgrounds are NOT survey papers).

**Patterns:**
- Listing 3+ prior art references with full analysis
- "现有技术中，文献1公开了……，文献2公开了……，文献3公开了……"
- Acknowledging prior art as "superior" (never concede superiority)

**Fix:**
- Keep only 1-2 closest prior art references
- Each reference: name it + its specific deficiency (1 sentence each)
- Never admit prior art is better at what it does
- End with: "因此，需要一种……" stating what's missing

## Quality Metrics

| Dimension | Criteria |
|-----------|----------|
| **术语一致性** | Each component has exactly one canonical term. Zero cycling. |
| **结构可实施性** | Every functional claim has structural basis in specification. |
| **客观性** | Zero subjective adjectives. Zero unsupported relative terms. |
| **权利要求多样性** | Claim transition structures vary. Not all use "其特征在于". |
| **翻译自然度** | If translated, reads as native patent language, not MT output. |

## Reference

Patent-specific skills in this repo:
- `skills/chinese-patent/` — Chinese patent drafting conventions
- Patent writing principles in workflow manifests
