# YouTube recording pack

Suggested title: **Build an Agent That Knows When NOT to Use RAG | Euron + Gemini + Python**

Length: approximately 6–8 minutes. Record the app and editor with OBS, PowerPoint screen recording, or another recorder. This file is a script, not a recorded or uploaded video. Never show your `.env` contents or API key on screen.

## 0:00 — The problem

“Many RAG demos search documents for every question. But if I ask what ten times twenty is, retrieval adds no useful evidence. Today we will build an agent that decides whether to answer, retrieve, calculate, or ask for clarification.”

Show the four route cards on the first tab.

## 0:45 — The decision

“The live router uses Gemini through Euron's OpenAI-compatible endpoint. It sees the question and whether documents exist. It returns a structured route, a brief explanation, and whether a calculator is needed. The code validates the decision before executing tools.”

Show `ROUTER_PROMPT` and the route validation in `agent.py`. Do not describe the explanation as hidden chain of thought.

## 1:30 — No retrieval needed

Select Live Euron mode. Ask “What is 10 × 20?” Show the selected route and zero tool calls. Then ask a general teaching question such as “Explain photosynthesis to a student.”

“These answers do not depend on our uploaded documents.”

## 2:15 — Retrieval is necessary

Ask “What does our uploaded policy say about refunds?” Expand the evidence panel.

“Our fictional store's policy is private task context. The agent searches paragraph chunks locally and uses the returned passages to answer. The source identifiers let us inspect the evidence.”

## 3:00 — Retrieval plus calculator

Ask “Calculate the refund under our policy for an unused product costing 2000 returned 10 days after delivery with a receipt.”

Show the retrieval call followed by calculator execution. Verify the result is 1800 under the 90% policy.

“The policy supplies the rule. The question supplies the amount and eligibility. The calculator executes the numeric expression. This is still the retrieval route, with the calculator flag enabled.”

## 4:00 — Clarification

Ask “Calculate the refund based on this policy.” Show the missing information question. Then ask “Can you explain it?” to demonstrate the direct clarification route.

“The agent should not guess a product price or what ‘it’ means. Each query in this demo is independent, so I provide the full details in the next question.”

## 4:45 — Test results

Run `python evaluation.py --live`, or open a previously generated live CSV. State the actual observed score; do not substitute the offline score. Show at least the 24-question table and explain that route agreement is distinct from answer correctness.

If recording without credentials, explicitly say: “These are offline rule-baseline results. Live model routing has not yet been evaluated.”

## 5:45 — Limitations and conclusion

“Lexical retrieval can miss synonyms or exceptions. An LLM can choose the wrong formula even when the calculator computes it correctly. We inspect evidence, test unseen questions, and ask for missing context. Retrieval is useful when the answer depends on documents; it is a tool the agent selects.”

Show the repository README and project structure. Add the real GitHub repository link to the video's description after publishing.

## Description template

Student project: selective RAG with four routing options, document evidence, calculator execution, and query logs.

GitHub: [insert actual repository URL]

Routing results: [insert link to reviewed routing CSV in your repository]

Model: gemini-3.5-flash-lite through Euron, subject to account availability.

Chapters: 0:00 Why selective retrieval / 0:45 Router / 1:30 Direct answer / 2:15 Documents / 3:00 Calculator / 4:00 Clarification / 4:45 Evaluation / 5:45 Limitations
