# Mechanism-level related-work checks

Find the real overlap and differences with the closest work to inform the next decision. Do not search merely to prove that a preferred proposal has never been attempted.

## Make the mechanism searchable

Summarize the current idea in one to three sentences:

> In which situation, using what available information, does the method change which representation or operation, with what expected benefit?

Separate situation, mechanism, and outcome terms. Add common synonyms and terminology from neighboring fields. Search direct counterparts and analogous mechanisms elsewhere. Respect the user's domain boundary: label cross-domain precedents separately rather than quietly expanding the task.

## Read and compare

Prefer primary papers, author project pages, and official implementations. Use abstracts for screening. Verify consequential mechanism differences in methods or implementation rather than comparing titles alone.

For a close paper that could change the conclusion, record relevant dimensions:

| Dimension | What to verify |
|---|---|
| Task and objective | Prediction, control, generation, recognition, or another task; what is actually optimized |
| Representation | What information is retained, compressed, separated, or discarded |
| Operation | Actual selection, transformation, updating, retrieval, recomputation, or other steps |
| Decision inputs | Required information and whether it is available at decision time |
| Temporal process | One-time processing or ongoing adaptation; initialization and termination |
| Computation and evaluation | What work is avoided, whether added overhead is counted, and how benefits are measured |

Show only dimensions relevant to the distinction. Filling every table cell is not a measure of research quality.

## Avoid overzealous novelty filtering and meaningless narrowing

Preserve the research question and its intended value while checking which parts related work covers. Shared goals, similar terms, and common modules justify investigation; they cannot alone rule out a direction.

If a paper could determine whether to continue, explain its inputs, key operations, outputs, assumptions, and evaluation scope in your own words, then map them to the current mechanism. Mark unresolved details as unverified. Do not infer unshown capabilities from an abstract or overlook capabilities it explicitly demonstrates.

Distinguish four cases: the important problem is already adequately solved; an existing solution has real limitations; the work shares a goal but uses a different mechanism; or information is insufficient. Dropping a novelty claim requires evidence that prior work covers that claim. Similarity alone does not justify abandoning the entire direction.

Do not add a special condition for every related paper. When proposing a different object, restricted task, or shorter time window, explain the independent practical need or scientific insight. Without that rationale, withdraw the artificial restriction and return to the original problem. A narrow question can be valuable; significance matters more than breadth or search-result counts.

Record novelty and importance separately: why the difference exists, and why it matters. "No exact paper found" cannot establish importance. Do not conceal a matching method to preserve a claim of value.

## Match the conclusion to the evidence

Select a description and explain why:

- **Direct overlap:** Prior work covers the principal representation, operations, and relevant conditions.
- **Adaptation or extension:** The object, data, scope, or some conditions change; value needs support from the problem and results.
- **Concrete difference:** Identify a different operation, information source, or assumption, not merely a new name.
- **Insufficient information:** Necessary details are unavailable or unverified; defer the judgment.

Separate "there is a difference" from "the difference is worth studying." A new module may be unnecessary; a simple change may remove an important limitation. Do not require algorithmic complexity or a theoretical proof as a universal condition for research value.

When reporting that no exact match was found, state search scope, date, and material gaps. This is not proof of priority. Do not invent novelty percentages or acceptance probabilities.

## Output and next step

Usually report a few closest works, primary-source links, overlaps, concrete differences, and one priority validation question. State whether you read only an abstract, checked the method, or ran an implementation.

Label interpretations as interpretations. Inaccessible sources, secondary summaries, and unverified titles cannot serve as confirmed facts. Never present another paper's performance as the current proposal's expected result.

Without browsing, organize available sources and a search plan, but say that a live check is incomplete. If direct overlap is established, allow the direction to end or change. Do not evade the conclusion by repeatedly renaming, adding modules, or switching applications.
