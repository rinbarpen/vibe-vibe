# Intuit to Idea · 直觉成题

[![Language: English](https://img.shields.io/badge/Language-English-2563EB?style=flat-square)](README.md)
[![语言：简体中文](https://img.shields.io/badge/%E8%AF%AD%E8%A8%80-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-64748B?style=flat-square)](README.zh-CN.md)

**You bring a direction. AI asks the questions. Research ideas grow from your intuition.**

You do not need a concrete idea, a known research gap, an algorithm, or an experiment plan to begin. Just name an area you want to explore:

> “I want to research program analysis, but I don't have a specific idea yet. Ask me questions and let me answer intuitively.”

AI introduces a concrete situation and asks a question you can reason about. Your answers gradually become ideas; AI follows your reasoning, explains possible mechanisms, checks related work, and examines implementation and validation. **You provide the intuition and direction. AI guides the conversation and contributes technical analysis and evidence.** If you already have a hypothesis, start there.

## Why not simply ask an LLM to find an idea on its own?

**The main failure this skill aims to prevent: an AI starts ruling out ideas before it properly understands the literature, repeatedly narrows a worthwhile question, and ends up with a tiny niche that appears unclaimed but has little research value.**

This is a workflow failure to watch for, not a claim about every model or autonomous research system. The problem is treating “eliminate anything resembling prior work” as the main way to discover ideas.

### 1. Overzealous novelty filtering makes the question narrower and narrower

A similar goal, term, or module becomes a reason to say “already done.” Each related paper prompts another restriction. After several rounds, the original question may only concern one object, one disturbance, one time window, and one special condition.

**Not finding that exact combination does not establish a valuable contribution.** An important problem can support different mechanisms, explanations, and solutions. Reviewing prior work should clarify what it covers, rather than eliminate every neighboring direction.

### 2. Module assembly takes the place of creative reasoning

This workflow addresses a frustrating outcome: asked for innovation, a model mainly recombines familiar components. It swaps a backbone, adds memory, introduces a selector or a consistency loss, and presents each component as a contribution. The proposal looks complete but lacks a new insight into the problem itself.

If every step asks “what has nobody done yet?”, this assembly process may simply fill leftover gaps in the literature. More modules and newer names do not explain why the approach should provide a new capability or understanding. A combination can be a contribution, but it needs a reason and evidence that it solves something the components did not already solve.

**This skill therefore does not rely on a model independently producing valuable innovations.** It draws on human intuition: Which situations deserve different treatment? Is this operation necessary every time? Could an existing assumption change? You do not need to propose an algorithm immediately. Start with a judgment such as “I think this could work differently”; AI helps examine how it might become an implementable method.

### 3. The differences become more specific while the research value disappears

An approach can differ from prior work yet address an artificial problem, add substantial complexity without meeting a meaningful need, or explain no important phenomenon. “Nobody wrote about this exact case” is not enough to justify pursuing it.

The conversation should keep returning to the broader direction: Who benefits if the mechanism works? What real limitation does it remove? What new understanding does it provide? **A small setting can test an important mechanism; avoiding related papers should not shrink away the reason to do the research.** Narrow scope is not the problem. A missing case for significance is.

### 4. Misreading papers can invalidate the novelty judgment from the start

Matching keywords in abstracts does not establish an understanding of the method. Compare the representation, operations, assumptions, and scope of the evidence. For example, selecting existing information and learning a new representation are not the same mechanism merely because they pursue the same goal.

A poor reading can cause opposite errors: dismissing a distinct mechanism as a duplicate, or overlooking a genuine match and relabeling an existing method as new. Before dropping a direction, inspect the closest paper's actual mechanism. Leave unresolved details marked as unverified.

Intuit to Idea assigns roles accordingly: **AI asks questions; you develop ideas through intuitive answers; AI then examines technical paths, prior work, feasibility, and significance.** Papers help us understand the problem and check our reasoning. They are not a checklist for crossing out whole directions at the first resemblance.

## Why start with intuition?

**You use intuition to propose ideas. AI helps assess how to implement them. Literature and experiments test the reasoning.**

Starting with intuition does not mean arriving with a flash of inspiration. You may not yet be able to formulate a research question, but you can react to a concrete situation: “I think this would happen,” or “these cases should be treated differently.” The questions help those judgments emerge.

AI should then ask: Is the necessary information available? Can the operation be implemented? What techniques and resources would it require? Which assumption is most uncertain? What small experiment could test it? A feasibility claim needs a concrete path; uncertainty needs an explanation of the missing evidence.

Human intuition can be biased, and AI's feasibility analysis is not a final verdict. The model can suggest technical options and evidence-based alternatives, but should not quietly replace your judgment with a familiar collection of modules. Effectiveness still needs experimental evidence.

The skill does not promise that human ideas are always more novel. Its purpose is to make the source of a question, the reasoning behind a mechanism, and the evidence for a conclusion clear enough for you to explain: **why this problem, why this approach, and what would change your mind.**

## How it works

**Your broad direction → AI's concrete question → your intuitive answer → a follow-up grounded in that answer → a clearer mechanism → related-work checks and a minimal experiment.**

The process can move back and forth. You can say “I don't know,” “that's not what I meant,” “look this up first,” or “summarize what we have.” AI should adjust accordingly.

- **A broad direction is enough.** AI supplies situations and questions rather than asking you to return with an idea.
- **One key question at a time.** The conversation should not become a questionnaire or a defense.
- **You keep control of the direction.** AI explains, illustrates, and verifies without deciding every module for you.
- **Use examples when you get stuck.** Comparing concrete situations is often easier than choosing between unfamiliar algorithm names.
- **Compare mechanisms, not just goals.** A shared goal does not make two methods identical; a new name does not make one novel.
- **Preserve significance while checking novelty.** Do not keep adding special conditions just to avoid a match.
- **Allow intuition to change.** Finding out that a direction is not worth pursuing can be a useful outcome.

## Quick start

After installing in a Codex environment that supports skills:

```text
$intuit-to-idea
I want to research: …
I don't have a specific idea yet. Ask me concrete questions and let me answer intuitively.
Ask one key question at a time, build on my answers, and don't give me a complete proposal upfront.
```

You can steer the conversation with prompts such as:

```text
I don't understand this concept yet. Give me two concrete examples I can compare.
```

```text
Check related work for the mechanism we've developed. Focus on what the methods actually do.
```

```text
Summarize this as a research idea card. Keep the experiment plan high-level.
```

In a chat tool without skill discovery, provide `SKILL.md` as conversational guidance and attach the relevant reference files when needed. Results depend on the host model and available tools. The skill instructions, supporting guides, examples, evaluation scenarios, and interface metadata are written in English. The skill follows your preferred conversation language, including Chinese. Both English and Chinese READMEs are available above.

## Installation

The repository root is a complete skill. Its folder and invocation name are `intuit-to-idea`.

1. Download or clone [this repository](https://github.com/ShawnL1N/intuit-to-idea) into a folder named `intuit-to-idea`.
2. Place it in your Codex user skills directory: by default, `~/.codex/skills/`, or `%USERPROFILE%\.codex\skills\` on Windows. If `CODEX_HOME` is set, use its `skills/` directory.
3. Check that the resulting path is `…/skills/intuit-to-idea/SKILL.md`, without an extra nested directory.
4. Invoke `$intuit-to-idea` in a session with skill discovery. If it is not listed yet, start a new session to refresh discovery.

Installation paths and discovery behavior depend on your client. Follow the relevant installation rules for other skill hosts; those clients have not been individually tested here.

No runtime dependencies or API keys are required by the skill itself. **Related-work checks require web access through the host.** Offline use can clarify mechanisms and identify questions to check, but cannot claim to have completed a live literature search.

## Repository structure

```text
intuit-to-idea/
├── SKILL.md                       Core behavior and scope
├── agents/openai.yaml             Codex display metadata and invocation prompt
├── references/
│   ├── dialogue-example.md        Fictional conversation and correction examples
│   ├── novelty-check.md           Mechanism-level related-work comparison
│   └── idea-card.md               Research idea card
├── evals/scenarios.md              Behavioral scenarios for manual retesting
├── README.md                      English
├── README.zh-CN.md                简体中文
├── LICENSE
└── .gitignore
```

## A short example

> **You:** I want to research program analysis tools, but I don't have a specific idea. Ask me questions.
>
> **AI:** Let's start with using the tool. After editing code, do you care more about finding out quickly whether you introduced a problem, or getting a fuller explanation of errors? We can also start with a different frustration.
>
> **You:** Quick feedback. I don't think changing a few lines should always mean waiting so long.
>
> **AI:** Your intuition is that a small edit usually affects only part of the analysis. Should we reanalyze only edited files, or also files that depend on them?
>
> **You:** Dependencies too, but not all of them are affected.
>
> **AI:** Then we need to distinguish “a dependency exists” from “this change invalidates it.” Renaming a local variable and changing a function's return type may have different effects. Do you think classifying the change first could help determine its impact?

This is a fictional illustration of the conversation style, not a novelty claim. The [full example](references/dialogue-example.md) also covers uncertainty, corrections, related-work checks, and requests to summarize.

## Scope and limits

For people with a broad area of interest who want AI-led questions to help their intuitive judgments develop into research questions. No specific observation, hypothesis, or proposal is required. Existing ideas are also welcome. The skill supports engineering research as well, but is not a bulk topic generator, paper-writing service, or certification of novelty.

An outcome may be a research idea card, an experiment direction, or a rejected assumption. Novelty and significance still depend on literature and evidence.

The workflow was abstracted from real collaboration. The release uses independently written generic examples and contains no original private transcripts, unpublished project details, data, or local project paths.

## Evaluation and contributions

[Behavioral retest scenarios](evals/scenarios.md) cover question pacing, user corrections, novelty judgments, and scope control. These are test specifications, **not completed evaluations of model performance**.

Contributions are welcome. Share a minimal, anonymized failure case: the user input, actual response, user intent that should have been preserved, and an observable improvement criterion. Do not upload private conversations or research material you do not have permission to publish.

Prefer fixing demonstrated behavior over turning every example into a universal procedure. Distinguish structural validation from actual model behavior testing; passing a format check does not establish effectiveness.

## License

[MIT](LICENSE) © 2026 Xiantao Lin.
