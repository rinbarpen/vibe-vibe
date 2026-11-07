# Dialogue example: eliciting intuition from a broad direction

This fictional example was written to illustrate the conversation style. It is not a private transcript or a claim that the illustrated method is novel. It concerns program analysis; the skill is not limited to that field.

## The user gives a direction; AI opens the conversation

**User:** I want to research program analysis tools, but I don't have a specific idea. Ask me questions and let me answer intuitively.

**Assistant:** Let's start with using the tool. After editing code, do you care more about finding out quickly whether you introduced a problem, or getting a fuller explanation of errors? We can also start with a different frustration.

**User:** Quick feedback. I don't think changing a few lines should always mean waiting so long.

The user did not arrive with a mechanism. The first question helped surface a concern and an intuitive judgment. If they chose error explanations, the next question should explore what makes an explanation useful, rather than continuing to steer toward incremental computation.

## Follow the answer to identify the intuition

**Assistant:** Your intuition is that a small edit usually affects only part of the analysis. The key is how we determine its impact. Should we reanalyze only edited files, or also files that depend on them?

**User:** Dependencies too, but not all of them are affected.

**Assistant:** You want to distinguish whether a dependency actually becomes invalid. Renaming a local variable might leave callers unaffected, while changing a function's return type could require reanalysis. Do you think classifying the change first could help determine its impact?

The user judges concrete cases instead of selecting a static-analysis algorithm upfront. If they already have an intuition, begin at this stage. Real implementation still requires checking language semantics and tool support; the example does not establish that these judgments always hold.

## When the user is unsure, offer comparable situations

**User:** I can't think of how to determine the impact. Can you give an example?

**Assistant:** Compare two situations: changing an internal name, and changing a function's promised inputs or outputs. The first might need only a local check; the second might require following call relationships. Which would you start with, or would you want to distinguish both?

Not knowing which algorithm to use does not mean lacking research intuition. A user who can compare real situations can participate in mechanism design.

## Address the current gap, not every missing detail

**User:** Both. If we find an effect, keep checking farther out.

**Assistant:** The mechanism is now to start locally and expand when necessary. The next issue is when to stop. If a caller's output summary remains unchanged after checking it, would that be enough to stop propagation to its callers?

If the user agrees, record a proposed stopping rule, not a proven result. Later, an indirect dependency or an incomplete summary can help identify the conditions under which the rule is valid.

## Correct the interpretation when the user objects

**User:** You're describing it as only checking locally again. I said the effect can keep propagating.

**Assistant:** You're right; I left out the propagation. The description should be: start at the edit, dynamically expand the checked region based on each result, and stop when the stopping condition is met. We still need to clarify which information that condition depends on.

The correction changes the mechanism itself. It does not demote the user's central point to an optional feature.

## Check prior work without dismissal or flattery

**User:** Does that mean nobody has done this?

**Assistant:** We can now search meaningfully. Incremental analysis, dependency invalidation, and change propagation are important areas to check. I'll compare how they represent dependencies, trigger propagation, and decide when to stop, then identify whether your rule differs materially.

Actually search primary papers or official implementations next. Do not announce novelty before searching. If the mechanism is well covered, explain the match and identify any meaningful unresolved problem without preserving a novelty claim through renaming.

## When asked to summarize, stop the question loop

**User:** Summarize what we have. Just a high-level experiment plan.

**Deliver:** A concise research idea card with the mechanism, verified related work, unresolved points, and a broad comparison of correctness, work performed, and elapsed time against full analysis and existing incremental methods. If related work has not been searched, give search directions rather than invented citations.

Do not continue asking about training data, layer counts, or hyperparameters, or automatically write a complete implementation or launch experiments.

## Responses to avoid

| Situation | Unhelpful response | Better approach |
|---|---|---|
| Only a broad direction | Require a specific idea or list ten complete topics | Supply a situation and ask one intuitive question |
| A new intuition | Immediately propose ten modules and three contributions | Identify one distinction that determines the mechanism |
| The user thinks it may work | Promise correctness or a publishable paper | Explain the conditions under which it might hold |
| The user is unsure | Ask again using harder terminology | Offer cases with different consequences |
| A paper shares the goal | Declare it already done | Compare representations, operations, and evidence |
| A mechanism matches prior work | Claim a backbone swap makes it novel | Explain the overlap and look for a real unresolved problem |
| Necessity is questioned | Keep making the scenario harder to preserve the proposal | Examine reasonable baselines and actual bottlenecks |

These questions illustrate pacing, not a fixed questionnaire. If the intuition concerns explanation, measurement, or scientific discovery rather than efficiency, ask about the relevant mechanisms and evidence.
