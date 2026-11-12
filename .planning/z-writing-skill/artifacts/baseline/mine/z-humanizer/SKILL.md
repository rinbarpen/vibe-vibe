---
name: z-humanizer
description: >
  Humanize Chinese and English prose (去AI味、润色、说人话). Route general,
  blog, documentation, and tutorial writing through bundled unslop; retain
  specialized academic, journal, conference, and patent workflows while
  preserving facts, terminology, citations, and code.
---

# z-humanizer: Unified Humanizer Orchestrator

## How to Use

**User invokes:**
Use `/humanize`, "去AI味", "说人话", "humanize this", or "make this sound less AI-generated".
An explicit `--domain` takes priority; `paper` is an alias for `academic`.

- `/humanize <text>` — ordinary prose uses unslop rewrite; specialized domains keep audit → confirm → rewrite
- `/humanize --quick <text>` — compact rewrite output; retain unslop diagnosis and preservation checks for ordinary prose
- `/humanize --domain paper <text>` — force a specific domain
- `/humanize --list` — list available domains and patterns

**AI auto-triggers:**
When the AI detects 3+ AI writing patterns in text the user has provided,
it asks: "检测到一些AI写作痕迹（如模板化开头、AI高频词汇等），需要帮你
humanize一下吗？" before responding with the final answer.

## Domain Router

### Step 1: Language Detection

- Content is >60% Chinese characters → `zh`
- Content is >60% Latin characters → `en`
- Mixed → split by paragraph, route each segment independently

### Step 2: Domain Detection

Scan for domain signals in order:

| Domain | Signals |
|--------|---------|
| **patent** | "其特征在于" / "said" + "embodiment" / claim numbering / "权利要求" / "附图说明" / patent number format |
| **conference** | "我们提出" / "we propose" / page limit cues / "related work" section / contribution numbering / "实验" + "baseline" |
| **academic** | "本文" / "this paper" / citation format [1] / "综上所述" / "研究表明" / abstract structure / "文献" |
| **tutorial** | "第一步" / "Step 1" / "首先" / code blocks / "运行" / "install" / numbered steps |
| **kb-doc** | "FAQ" / "troubleshooting" / "概述" / "Introduction" / "前提条件" / "Prerequisites" / parameter tables |
| **blog** | First-person narrative / opinion signals / platform cues (知乎/公众号/小红书/Medium/LinkedIn) / lack of formal structure |
| **journal** | Same as academic + journal-specific formatting cues |
| **general** | None of the above |

If domain is ambiguous (no strong signals), list top 2 candidates and ask.

### Ordinary Prose: Delegate to Unslop

For `general`, `blog`, `kb-doc`, and `tutorial`, read
[references/general.md](references/general.md), then the bundled
[unslop entrypoint](references/unslop/SKILL.md). Follow its command and core
contract, and return the result. Keep the paragraph language, including Chinese
and mixed-language text. The legacy severity score, punctuation quotas, noise
budget, and specialized workflow below do not apply to this branch.

For `academic`, `journal`, `conference`, and `patent`, continue with Steps 3–4
and the specialized workflow below. Preserve their existing domain patterns,
terminology, evidence, numbers, citation keys, and LaTeX commands.

### Step 3: Severity Assessment

Quick AI-trace density check on the first 500 characters:
- Count hits from the Unified AI Vocabulary List (below)
- Count em-dashes
- Count "值得注意的是"/"it is worth noting" type filler
- Count paragraph-ending summary patterns

| Score | Severity | Default Gear |
|-------|----------|-------------|
| 0-2 | Low | minimal (spot fixes) |
| 3-5 | Medium | standard (full pass) |
| 6+ | High | aggressive (structural rewrite) |

### Step 4: Load Patterns

Load the relevant patterns file(s) from `patterns/`:
- `patterns/patent.md` — when domain=patent
- `patterns/conference.md` — when domain=conference
- Plus always apply cross-cutting rules below

For deep pattern reference, load the corresponding sub-skill's SKILL.md:
- `skills/humanizer-zh-academic/SKILL.md` — Chinese academic full pattern set
- `skills/academic-humanizer/SKILL.md` — English academic full pattern set

## Specialized Operating Procedure

### Phase 1: Analyze

1. Detect language and domain (Steps 1-2 above)
2. Scan text against all patterns for the detected domain
3. Identify: which patterns hit, severity per hit, affected paragraphs
4. Calculate a preliminary quality score (0-60, using the detected domain's
   quality metrics)

### Phase 2: Audit Report

Output a concise report listing:

```
Domain: {detected domain}
Language: {zh/en/mixed}
Severity: {low/medium/high}
Score: {X}/60

Patterns detected:
- {Pattern name} — {count} hits — {paraphrase example}
- {Pattern name} — {count} hits — {paraphrase example}

Hard constraints violated:
- {Constraint name}: {actual} / {limit}

High-risk paragraphs: {list of paragraph numbers or first lines}
```

Keep this to ~100 words. Do not list every single hit — summarize by pattern
type and note the most egregious examples.

### Phase 3: Confirm

Ask: "以上是检测到的AI痕迹概要。需要按默认方案改写，还是先调整哪些方面？
(默认/仅修复XX模式/跳过)」

### Phase 4: Rewrite

Apply in this order:
1. Structural fixes (pattern-level, not word-level)
2. Hard constraint violations (these are non-negotiable)
3. Word/phrase-level fixes (AI vocabulary, filler, etc.)
4. Rhythm check (sentence length variation, paragraph variety)
5. Domain-specific final pass (re-check domain patterns)

Preserve every number, citation key, code snippet, command, URL, and
technical term.

### Phase 5: Quality Check

Self-verify against domain's quality metrics. Score the output.
If score is below threshold (42/60 for academic, varies per domain),
do another pass focusing on the lowest-scoring dimension.

## Specialized Cross-Cutting Rules

These apply to academic, journal, conference, and patent routes only.

### Em-Dash Rule

- **English domains:** Zero em-dashes (—) or en-dashes (–) in final rewrite.
  Replace with: period > comma > colon > parentheses > restructure.
- **Chinese domains:** Max 2 em-dashes per paragraph. Reduce if >4 in any
  single paragraph. Prefer comma or restructure over dash.

### Unified AI Vocabulary List

| English | Chinese |
|---------|---------|
| delve | 深入探讨 |
| pivotal | 关键的 |
| landscape (abstract) | 格局 (抽象用法) |
| tapestry (abstract) | 织锦 (抽象用法) |
| testament | 证明 |
| underscore | 强调 |
| intricate | 复杂的 |
| robust (overused) | 鲁棒的 (过度使用) |
| leveraging | 利用 (过度使用) |
| seamless | 无缝的 (过度使用) |
| noteworthy | 值得注意的是 |
| a myriad of | 大量的 |
| multifaceted | 多方面的 |
| groundbreaking (figurative) | 开创性的 (比喻) |
| paradigm shift | 范式转变 |
| vibrant (figurative) | 充满活力的 (比喻) |
| rich (figurative) | 丰富的 (比喻) |
| foster | 培养 |
| showcase | 展示 |
| realm | 领域/范畴 |
| | 深刻揭示了 |
| | 具有重要意义 |
| | 综合运用 |
| | 不可或缺 |
| | 进一步 (过度使用) |

Replace with plain alternatives. Keep only if the specific context genuinely
requires the nuanced meaning.

### Citation / Data / Code Preservation

- **Never alter** a citation key, number, or reference format
- **Never alter** a number, percentage, or statistical value
- **Never alter** a code snippet, command, or configuration line
- **Never alter** a URL, file path, or API endpoint
- **Never invent** evidence, data, citations, or examples

### Noise Budget

Do NOT remove ALL AI traces. Intentionally leave 1-2 minor traces per
500 words to avoid over-homogenization.

- Preferred to retain: mild parallelism (2 items, not 3-way symmetric)
- Acceptable: a common transition word (but, however, 此外) used once
- **Never retain:** empty summary sentences, fake citations, subjective
  praise, hard constraint violations

### False Positive Protection

Do NOT flag these as AI traces:
- Perfect grammar (human experts also write correctly)
- Formal academic register (this is standard, not AI)
- Technical terminology density (domain-appropriate)
- Single em-dash used for genuine parenthetical (check context)
- Curly quotes used by the writing tool (system-level, not AI)
- Cited statistics with sources (this is evidence, not padding)

## Quality Scoring (Cross-Domain)

Base 0-60 scale, adapt per domain:

| Score | Meaning |
|-------|---------|
| 54-60 | Excellent, ready to publish |
| 42-53 | Good, patch specific deduction items |
| Below 42 | Needs full revision of high-risk paragraphs |

## Error Handling

| Situation | Response |
|-----------|----------|
| Domain unclear | List top 2 candidates, ask user |
| Specialized pattern file missing | Keep the specialized cross-cutting rules; report the missing resource before using another domain |
| User rejects all changes | Output original text, no changes |
| Very short text (<50 chars) | Skip audit, check: is it even AI-generated? |
| Text is code/config | Return as-is, humanizer is for prose |
