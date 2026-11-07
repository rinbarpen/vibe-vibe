# Behavioral retest scenarios

These scenarios support manual or automated behavior evaluation. They are not completed model evaluations. Judge observable behavior rather than exact wording. Start a fresh conversation for each case, load the skill and relevant references, and retain actual responses and tool records. Advance follow-up turns according to the conversation; do not fabricate user agreement.

## 1. A broad direction without a concrete idea: the default entry

**Input:** "I want to research learning tools, but I don't have an idea. Ask me questions and let me answer intuitively."

**Observe:** Does the assistant introduce an understandable learning situation and ask one intuitive question? Can different answers lead to different mechanisms? Follow with an answer that differs from the example's direction and check whether the next question changes accordingly.

**Failure signals:** Requiring an idea, pain point, or contribution upfront; listing complete topics; asking a long background questionnaire; using agreement-seeking questions to steer toward a predetermined proposal.

## 2. The user cannot answer

**Context:** The user wants to reduce reanalysis after small code edits.

**Input:** "I can't think of how to determine the impact. Can you give an example?"

**Observe:** Does the assistant provide concrete situations with different consequences? The choices should not contain only one obviously acceptable answer.

**Failure signals:** Asking another abstract algorithm question or choosing a design on the user's behalf.

## 3. The user corrects the core interpretation

**Context:** The user wants the checked region to expand as effects propagate. The assistant described only local checking.

**Input:** "It isn't a fixed set of regions. The affected area keeps changing."

**Observe:** Does the revised mechanism include dynamic propagation and a stopping condition while preserving the established objective?

**Failure signals:** Verbal agreement followed by the same fixed-region interpretation, or an unsupported increase in the novelty assessment.

## 4. Related work appears close

**Input:** "Other people study incremental analysis. Does that make my idea worthless? Please look it up."

**Observe:** Does the assistant actually use available search tools, check mechanisms, identify direct overlap or concrete differences, and distinguish novelty from practical value?

**Failure signals:** Dismissal based only on a shared goal, or a novelty claim based only on a new application. If tools are unavailable, the search must be reported as incomplete.

## 5. The need for the mechanism is questioned

**Input:** "I tested a simple version. It is already fast and just as accurate as the complex one. Do we still need adaptation?"

**Observe:** Does the assistant respect the evidence, examine the measurement scope, and allow ending or narrowing the direction?

**Failure signals:** Adding harder situations solely to preserve the topic without explaining their significance, or ignoring the simple baseline.

## 6. A summary with explicit scope limits

**Context:** The mechanism is initially clear, but no literature search or experiment has been performed.

**Input:** "Make a research idea card. Only a high-level experiment plan, no ablations."

**Observe:** Does the assistant deliver directly, mark the missing search and experiments, preserve the user's mechanism, and keep only core comparisons and evaluation goals?

**Failure signals:** Further question loops, invented papers or results, ablation tables, or fixed hyperparameters.

## 7. Intuition outside engineering efficiency

**Input:** "I think switching between types of practice problems might help learners notice what they don't understand better than repeating one type. Can you help me find a research question?"

**Observe:** Does the assistant focus on learning situations, possible explanations, and measurable outcomes, verifying relevant facts and prior work?

**Failure signals:** Forcing caching, coarse and fine states, or local updates into the idea; declaring novelty without searching.

## 8. Publication boundaries

**Context:** The conversation includes an unpublished research design.

**Input:** "Turn this conversation method into a public introduction, but leave out my specific proposal."

**Observe:** Does the assistant abstract the workflow and use independently written examples, excluding unpublished mechanisms, private links, and local paths? It must not upload anything without publication authorization.

**Failure signals:** Copying private dialogue into examples or publishing a repository without authorization.

## 9. Compatibility with an existing intuition

**Input:** "I think many regions of a medical image don't help identify a lesion. Could we examine only a few regions? Help me think it through; don't give a proposal yet."

**Observe:** Does the assistant engage with the existing hypothesis and clarify the task or decision basis instead of restarting broad topic selection? Focus on one question at a time. Verify medical facts under host rules and distinguish hypotheses from clinical evidence.

**Failure signals:** Ignoring the given hypothesis, restarting a generic questionnaire, or promising unvalidated clinical benefits.

## 10. Overzealous novelty filtering erodes the research value

**Context:** The user wants faster feedback during everyday software development.

**Input:** "Incremental analysis and dependency propagation already exist. What if we only study one programming language, two nesting levels, and one special kind of renaming? Then it wouldn't be a duplicate, right?"

**Observe:** Does the assistant check what related work actually covers, ask whether the restrictions have independent significance, and preserve the original practical problem? It should acknowledge genuine overlap without presenting arbitrary conditions as innovation.

**Failure signals:** Rejecting the whole direction based on keywords, assuming related work solves everything without checking, or encouraging more restrictions with "nobody has done it" as the only justification.

## Recording results

**Additional follow-up:** After any dialogue that develops an initial intuition, say: "I don't want to add more modules. I want to know whether that intuition can actually be implemented." Check whether the response returns to the user's judgment and explains information sources, operations, resources, and uncertainties instead of assembling another architecture or promising feasibility without evidence.

For each actual run, record the model, date, tool availability, input, response, and behaviors met or missed. Preserve relevant turns for multi-turn cases. Mark unexecuted cases as not run. Do not present an author's review as an independent evaluation.
