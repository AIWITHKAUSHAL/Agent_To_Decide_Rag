# Teach the agent in 30 minutes

## Learning objective

Students should explain why retrieval is needed for private facts but unnecessary for every question. They should distinguish a routing decision, evidence retrieval, computation, and clarification.

## 0–5 minutes: predict before running

Ask students to assign routes to these questions:

| Question | Expected behavior |
| --- | --- |
| What is 10 × 20? | Answer directly: 200; no retrieval |
| What does our policy say about refunds? | Retrieve the private policy |
| Calculate (1250 * 0.9) - 20 | Calculator: 1105; no retrieval |
| Can you explain it? | Clarify what “it” refers to |
| Calculate the refund under our policy for an unused product costing 2000 returned within 10 days with a receipt. | Retrieve, then calculator: 1800 |

## 5–15 minutes: live demonstration

Run the five questions in Live Euron mode. Inspect the short decision explanation, actual tool calls, and evidence panel. For arithmetic, emphasize that the absence of retrieval is intentional. For policy questions, explain that model training cannot establish your uploaded policy's contents.

Remove the sample policy and ask the policy question again. The agent should say supporting documents are missing. Restore the policy and ask “Calculate the refund based on this policy.” It should retrieve first and request the missing purchase/eligibility details; it must not invent them.

## 15–20 minutes: read the code together

Read `ROUTER_PROMPT`, `Agent.run`, and `Agent._answer` in `agent.py`. Explain the distinction between the route and `needs_calculator`. Inspect `calculate`: only a small set of numeric AST nodes is executable. Then inspect the retrieval search: matching terms rank local paragraphs.

## 20–25 minutes: evaluate

Run `python evaluation.py --live`. Compare the expected and actual routes in CSV. Count disagreements and discuss ambiguous cases rather than changing expected labels merely to improve the score. Inspect answers separately: routing accuracy alone cannot establish grounding or correct formulas.

For the policy calculation examples, manually check 1800 for the eligible 2000 product, 800 for the qualifying damaged product, clarification for missing amount/eligibility, and 360 for eligible products costing 100 and 300.

## 25–30 minutes: exercises

1. Add five unseen questions and label their expected routes before executing them.
2. Upload a different fictional policy with a different restocking fee; disable the sample policy. Confirm that the refund changes.
3. Ask a question using synonyms absent from the document. Explain lexical retrieval's limitations.
4. Upload conflicting policies. Discuss why version/date selection or clarification is necessary.
5. Compare a mandatory-retrieval design with this agent: count unnecessary retrieval calls on general questions.

## Useful distinctions

- A route is a decision; a tool trace records actions that actually happened.
- A concise explanation is not the model's private chain of thought.
- An offline rule baseline demonstrates plumbing; a live model evaluation tests LLM decisions.
- A correct route can still produce an incorrect answer. Inspect sources and numeric formulas separately.
- Asking for clarification is a successful outcome when essential information is missing.
