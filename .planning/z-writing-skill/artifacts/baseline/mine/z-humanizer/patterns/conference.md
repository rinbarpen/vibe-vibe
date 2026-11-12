# Conference Paper Humanization Patterns

Supplement to humanizer-zh-academic and academic-humanizer. Covers AI
patterns specific to conference papers (short papers, full papers,
workshop papers) — both Chinese and English.

Conference papers have distinct constraints: strict page limits, dense
information, and specific reader expectations (reviewers are tired,
impatient, comparison-shopping across submissions).

## Positive Style Guide

Good conference paper prose is:
- **Dense** — every sentence carries information; no fat
- **Signposted** — clear structure within strict space
- **Self-contained** — a reviewer should grasp the contribution in the first page
- **Modest** — claims match the scope of a short evaluation
- **Venue-aware** — matches the reviewing culture of the target conference

## AI Patterns

### C1: Related Work Enumeration

AI writes Related Work as a laundry list rather than a positioning argument.

**Pattern:**
- "[A] proposed X. [B] proposed Y. [C] proposed Z. However, these methods
  have limitations."
- "文献[1]提出了X方法，文献[2]提出了Y方法，文献[3]提出了Z方法"

**Fix:** Organize by problem dimension, not by paper:
- "For problem X, approach A works when... but fails when... (Section 3
  addresses this gap). For problem Y..."
- Group 3-4 papers per paragraph. Max 2 paragraphs for Related Work in
  a short paper.

**Hard constraint:** No paragraph that lists >2 papers without synthesis.
Every citation paragraph must have an organizing claim.

---

### C2: Contribution List Template

AI generates contribution lists as a numbered template that sounds
identical across papers.

**Pattern:**
- "(1) We propose a novel method; (2) We conduct extensive experiments;
  (3) We achieve state-of-the-art results"
- These are NOT contributions — they describe the paper's structure,
  not what it contributes.

**Fix:** Each contribution must name a specific capability or finding:
- ✓ "We show that attention is unnecessary for this task — a simple MLP
  matches BERT with 10x less compute"
- ✗ "We propose a novel attention mechanism"

**Hard constraint:** Each contribution item must contain at least one
specific noun (dataset name, metric, baseline, finding), not just
methodology labels.

---

### C3: Page-Limit-Induced Artifacts

AI forced to shorten text produces distinctive compression patterns.

**Patterns:**
- Excessive abbreviations (introducing 5+ acronyms)
- Missing transitions between sections (because "no room")
- Figures described in text that could just be captions
- Every paragraph is exactly 3-4 sentences (optimized for page fitting)

**Fix:**
- Limit new acronyms to 3 per paper
- Keep 1 sentence transitions between major sections
- If a figure already shows the result, the text should analyze, not
  describe
- Vary paragraph length: allow 1-2 sentence paragraphs and 5+ sentence
  paragraphs

---

### C4: Introduction Structure Rigidity

AI intros follow a 4-sentence template: broad context → narrow gap →
our method → our results.

**Pattern:**
- "X is an important problem. Despite advances, existing methods suffer
  from Y. In this paper, we propose Z. Experiments show that..."
- Every sentence is formulaic, making the intro predictable and boring.

**Fix:** Vary intro structure:
- Option A: Start with a specific problem instance, not the broad domain
- Option B: Start with a surprising negative result that motivates the work
- Option C: State your finding first, then explain why it matters
- The 4 elements (context, gap, method, result) should all be present but
  NOT as 4 consecutive template sentences

---

### C5: Figure/Table Language Padding

AI writes figure descriptions that restate the visual rather than
interpreting it — wasting precious page space.

**Pattern:**
- "As shown in Figure 1, our method (red line) achieves higher accuracy
  than baseline (blue line) across all epochs."
- → Any reader can see this. The text should explain WHY or WHAT IT MEANS.

**Fix:** Text accompanying a figure should:
- Point out the NON-OBVIOUS insight ("Despite higher accuracy, our method
  converges slower — Section 4.3 discusses this trade-off")
- Or state the implication ("This confirms that the attention mechanism
  is unnecessary for short sequences")
- Never: describe what's visible in the figure

---

### C6: Workshop vs Full Paper Voice Confusion

AI writes workshop papers in the same voice as full papers, missing the
distinctive workshop register.

**Full paper voice:** Definitively claims contributions, comprehensive
experiments, polished narrative.
**Workshop paper voice:** Early-stage, ideas-focused, more speculative,
less experiment burden. A workshop paper that claims too much sounds
like it should be a full paper — and disappoints.

**Workshop-specific patterns to fix:**
- Over-claiming results from limited experiments ("prove" → "suggest")
- Full experimental sections that are clearly incomplete
- Too-formal structure that doesn't invite discussion

**Fix for workshop papers:**
- Tone down claim verbs: "demonstrate" → "suggest / provide evidence for"
- Replace "extensive experiments" with specific scope: "on 3 datasets"
- Add open questions or limitations section (signals intellectual honesty)

---

### C7: Reviewer-Exhaustion Blindness

AI writes for a neutral reader, not a tired reviewer who is comparing
12 papers and needs quick judgment.

**Patterns:**
- Key contribution buried on page 2
- Method details before the problem is clear
- Results presented without context on baselines
- No explicit "why should I care" in the first paragraph

**Fix:** Apply the "taxi cab test": after page 1, the reviewer should
be able to state:
1. What problem this solves
2. Why it matters (who cares?)
3. What the key insight/finding is
4. How it's different from the closest prior work

If any of these 4 is not clear by the end of page 1, fix.

---

### C8: Ablation Study AI-isms

AI-generated ablation studies follow a predictable pattern that lacks
insight.

**Pattern:**
- Remove component A → performance drops. Remove component B →
  performance drops. Therefore both are important.
- Never investigates interactions between components
- Never ablate to understand WHY, only to confirm the design

**Fix:** For each ablation, ask what question it answers:
- "Does A matter?" → show what happens without A
- "Why does A matter?" → ablate A but characterize the type of failure
  (speed? accuracy on hard cases? generalization?)
- "Does A interact with B?" → test A-without-B and B-without-A

---

### C9: Citation Proximity Padding

AI places citations at the end of generic claims to make them seem
supported, without actually engaging with the cited work.

**Pattern:**
- "Deep learning has achieved great success in computer vision [1,2,3,4,5]
  and natural language processing [6,7,8,9,10]."
- The citation dump pads the paper without adding information.

**Fix:** Cite 1-2 most relevant works per claim and say WHY they're relevant.
"If more citations are needed, use a survey paper as the anchor citation."

**Hard constraint:** No citation list of >3 without a connecting verb or
organizing claim. "X and Y found that... [1,2]" is OK. "Many works study
this [1,2,3,4,5]" is not.

---

### C10: Camera-Ready Polish Gaps

AI-generated camera-ready versions miss the specific revisions reviewers
asked for, or address them in a mechanical "we have addressed the
reviewer's concern" without genuine revision.

**Pattern:**
- Added "We acknowledge this limitation" without actually constraining
  the claim
- Added a paragraph addressing Reviewer 2's concern that sits awkwardly
  and breaks flow
- "Following the reviewer's suggestion, we added experiments" — but the
  experiment doesn't change the narrative

**Fix:** For each reviewer concern:
- If it changes the claim, rewrite the claim throughout
- If it adds a constraint, integrate it naturally
- If it adds an experiment, let the result change the discussion
- Never add a paragraph that starts with "As suggested by the reviewer"

---

## Quality Metrics

| Dimension | Criteria |
|-----------|----------|
| **Page-1 clarity** | Can reviewer state problem + contribution + novelty by end of page 1? |
| **Claim-evidence match** | Every claim has a specific result, citation, or argument backing it. |
| **Related-work positioning** | Organized by dimension, not by paper. No citation dumps. |
| **Venue fit** | Voice matches venue expectations (workshop vs full, tier match). |
| **Compression quality** | Shortened text uses dense information, not abbreviations + missing transitions. |

## Scene Differentiation

| Type | Key Difference |
|------|---------------|
| **Full paper (8+ pages)** | More evidence, deeper related work, complete ablation. |
| **Short paper (4 pages)** | Single contribution, minimal related work, 1-2 experiments. |
| **Workshop paper** | Ideas-focused, speculative, open questions welcome. |
| **Rebuttal** | Claim-level response, evidence-only tone, no defensiveness. |

## References

- `skills/humanizer-zh-academic/` — Chinese academic patterns (conference-
  relevant: theory-opening fixes, symmetry breaking, citation discipline)
- `skills/academic-humanizer/` — English academic patterns (Layer 2: academic
  AI tells, Layer 4: claim-evidence discipline, Layer 5: venue matching)
