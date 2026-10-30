# vibe-coding

This project is a toolkit that integrates various professional AI Skills, aiming to transform Claude into an intelligent assistant with multi-domain professional knowledge. By integrating scientific research, design aesthetics, and developer tools, you can perform complex professional tasks directly in the conversation.

---

## 🚀 Core Skills Detailed Introduction

### 1. 🧬 Scientific Research & Collaborative Lab
Based on **[Claude Scientific Skills](skills/claude-scientific-skills)** (K-Dense AI), containing **140+** deeply integrated research skills.

*   **Bioinformatics & Genomics**: Sequence analysis, single-cell RNA-seq processing, gene regulatory networks, variant annotation.
*   **Cheminformatics & Drug Discovery**: Molecular property prediction, virtual screening, ADMET analysis, molecular docking.
*   **Proteomics**: LC-MS/MS data processing, peptide identification, protein quantification.
*   **Clinical Research & Precision Medicine**: Clinical trial analysis, drug safety assessment, treatment planning.
*   **Medical Imaging**: DICOM processing, whole-slide image analysis, digital pathology workflows.
*   **Physics & Materials Science**: Crystal structure analysis, phase diagram calculation, astronomical data conversion.

### 2. 🎨 UI/UX Design Intelligence
Combines **[UI-UX Pro Max](skills/ui-ux-pro-max-skill)** with Anthropic official design skills.

*   **Intelligent Design System Generation**: Automatically analyze project requirements and generate complete visual specifications.
*   **58+ UI Style Library**: Supports Glassmorphism, Neumorphism, Minimalism, and other popular styles.
*   **[Frontend Design](skills/anthropics/skills/frontend-design)**: Generate interface components following professional design aesthetics, avoiding mediocre "AI-flavored" designs.
*   **[Theme Factory](skills/anthropics/skills/theme-factory)**: Preset multiple industry themes (e.g., Arctic Frost, Midnight Galaxy) for one-click visual style switching.
*   **[Algorithmic Art](skills/anthropics/skills/algorithmic-art)**: Generative art creation based on p5.js.

### 3. 📄 Enterprise Productivity & Office Automation
Deeply integrates **[Anthropic Official Document Skills](skills/anthropics)**, containing **16+** official document processing skills.

*   **[Word (docx)](skills/anthropics/skills/docx)**: Advanced document creation, revision tracking, complex formatting.
*   **[Excel (xlsx)](skills/anthropics/skills/xlsx)**: Automated pivot tables, formula generation, and large-scale spreadsheet analysis.
*   **[PowerPoint (pptx)](skills/anthropics/skills/pptx)**: Structured slide generation, content layout optimization.
*   **[PDF Master](skills/anthropics/skills/pdf)**: Extract form fields, PDF annotation filling, image conversion.
*   **[Internal Comms](skills/anthropics/skills/internal-comms)**: Corporate press releases, status reports, FAQ writing templates.

### 4. 🛠️ Developer Empowerment
Automated workflows designed for programmers to enhance development efficiency.

*   **[MCP Builder](skills/anthropics/skills/mcp-builder)**: Automatically generate server code (Node/Python) following Model Context Protocol specifications.
*   **[Web Artifacts Builder](skills/anthropics/skills/web-artifacts-builder)**: Quickly build interactive component previews with React + Tailwind + Lucide.
*   **[Webapp Testing](skills/anthropics/skills/webapp-testing)**: Automatically write and run local application test cases using Playwright.
*   **[Skill Creator](skills/anthropics/skills/skill-creator)**: Assist in developing and validating custom skills following the Agent Skills specification.

### 5. 📦 More Community & Specialized Skills

*   **[AI-Research-SKILLs](skills/AI-Research-SKILLs)**: 83+ AI/ML research engineering skills (model architecture, training, inference, evaluation, paper writing).
*   **[Humanizer-zh](skills/Humanizer-zh)**: Remove AI-writing traces from Chinese text for more natural phrasing.
*   **[Pretty-mermaid-skills](skills/Pretty-mermaid-skills)**: High-quality Mermaid diagram rendering with multiple themes, SVG/ASCII output.
*   **[chinese-novelist-skill](skills/chinese-novelist-skill)**: Chapter-by-chapter Chinese fiction writing, long-form and multi-genre.
*   **[Chinese-WebNovel-Skill](skills/chinese-webnovel-skill)**: Chinese web-novel planning, drafting, revision, pacing, chapter endings, reference retrieval, and consistency review.
*   **[De-AI-Prompt-Enhancer](skills/de-ai-prompt-enhancer)**: De-AI Chinese writing skill with author style replication and 24-pattern AI trace detection.
*   **[X Research](skills/x-research-skill)**: General X/Twitter research assistant supporting real-time search, tweet analysis, and expert opinion extraction.
*   **[Humanizer-ZH-Academic](skills/humanizer-zh-academic)**: Reduce AIGC detection rate in Chinese academic writing.
*   **[academic-humanizer](skills/academic-humanizer)**: Academic AIGC trace detection and de-AI-ification skill.
*   **[shuorenhua](skills/shuorenhua)**: Chinese-first rewrite skill — removes AI tone, preserves facts.
*   **[Unity Game Development](mine/unity-game-development)**: End-to-end game skills with 67 skills covering orchestration, nine stages, 29 specialties, a six-skill 3D/DCC modeling branch, eight game-testing skills, nine executors and five reviewer skills; install the bundle, a stage, or an individual capability.
*   **[State Machine Reasoning](mine/state-machine-reasoning)**: Model decisions, debugging, research, and workflows as state machines and generate Mermaid visualizations.
*   **[writing-agent](workflows/writing-agent)**: Full-stack Claude Code writing system from topic selection to publication.

---

## 🏗️ Vibe Coding Manifests

This project provides a series of Vibe Coding configuration Manifests adapted to different scenarios, which can be used directly to initialize new projects or optimize AI context for existing projects:

*   **[Vibe Coding (Core)](manifests/vibe-coding)**: Core Vibe Coding workflow configuration with `CLAUDE.md` and `AGENTS.md` templates.
*   **[Auto Research](manifests/auto-research)**: Automated research pipeline covering literature discovery, experiment execution, paper writing, and review.
*   **[Auto Research (ARS)](manifests/auto-research-ars)**: Enhanced automated research system with multi-agent collaboration and deep literature mining.
*   **[Fund Proposal](manifests/fund-proposal)**: Grant/proposal writing configuration integrating research, review, and visualization skills.
*   **[Git Manager](manifests/git-manager)**: Git repository management and automation configuration.
*   **[Tutor](manifests/tutor)**: Adaptive tutoring with or without textbooks, illustrated notes, learning records, and optional PDF export.
*   **[Market Analysis](manifests/market-analysis)**: Market analysis and competitive research configuration.
*   **[Novel Writing](manifests/novel-writing)**: Fiction writing and literary creation configuration.
*   **[Social Media](manifests/social-media)**: Social media content creation and management configuration.
*   **[UI Testing](manifests/ui-testing)**: Automated UI testing configuration supporting Playwright/Vitest/mobile/accessibility testing.
*   **[Unity Game](manifests/unity-game)**: End-to-end Unity 2D/3D game production, from concept to release and live operations, with 21 native Claude Code/Codex subagents, 3D modeling/external-software and execution/reviewer skills, Editor CLI helpers and a [workflow SVG](manifests/unity-game/references/workflow.svg).

---

## 📂 Skills & MCP Index

For convenience, we provide detailed annotation indices for skills and MCP servers:
- 🇨🇳 [Chinese Annotations Index](skills/ANNOTATIONS.md)
- 🇺🇸 [English Annotations Index](skills/ANNOTATIONS_EN.md)

## 🛠️ How to Use

1.  **Load Skills**: Reference the corresponding directory in an environment that supports Skills (e.g., Claude Code or Claude.ai).
2.  **Trigger Directly**: 
    *   *"Use scientific skills to analyze this DNA sequence..."*
    *   *"Use UI-UX skills to generate a design system for my finance app..."*
    *   *"Use Word skills to generate a quarterly report based on this outline..."*

## Manifest Authoring

A manifest is a human–AI collaboration contract. When creating a manifest or changing
its workflow, also deliver a corresponding **workflow SVG, editable source,
reproducible rendering command, and read-only drift check**, linked from its README or
main instructions. Distinguish autonomous AI execution, AI validation/review, and
human decisions; show branches, rework and the AI continuation after confirmation.

See the [authoring requirements](docs/manifest-workflow.md) and the
[rendered example](docs/examples/manifest-workflow/workflow.svg). Reuse existing
canonical sources and renderers, including Unity's workflow; these requirements do
not change installation behavior or bulk-migrate existing manifests.

```bash
python3 scripts/render-manifest-workflow.py \
  --source docs/examples/manifest-workflow/workflow.json \
  --output docs/examples/manifest-workflow/workflow.svg --check

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_manifest_workflow.py' -v
```

## 📜 License

The skill libraries integrated in this project follow their respective original authors' open-source licenses:
- Anthropic Skills: Apache 2.0 / Source-available
- Scientific Skills: MIT
- UI-UX Pro Max: MIT
